"""Product selection from the verified catalog, per docs/02 and docs/04.

Selection never overrides hydraulics (docs/08 s.24): the design pressure
and radius requirement come in from the hydraulic/layout side, and a
product qualifies only when its PUBLISHED ranges cover them. Every
exclusion is reported with its reason so the choice is traceable.

Performance lookups return only exact published rows - no interpolation
or extrapolation beyond the manufacturer's table (Charter rules 1 and 5).
"""

import csv
from dataclasses import dataclass
from pathlib import Path

from calculators.units import _require_positive

PERFORMANCE_DIR = Path(__file__).resolve().parents[2] / "data" / "manufacturers" / "rain_bird" / "performance"


@dataclass(frozen=True)
class Candidate:
    model: str
    manufacturer: str
    application_type: str
    reason: str
    source_url: str


@dataclass(frozen=True)
class Exclusion:
    model: str
    reason: str


@dataclass(frozen=True)
class SelectionResult:
    candidates: tuple
    exclusions: tuple


def select_products(records: list, application_type: str,
                    design_pressure_psi: float,
                    radius_needed_ft: float = None) -> SelectionResult:
    """Filter catalog records for one requirement.

    A record qualifies when its application type matches, the design
    pressure sits inside its published pressure range, and (when a
    radius is required) its published radius range covers that radius.
    Records ranked closest-to-recommended-pressure first.
    """
    _require_positive(design_pressure_psi, "design_pressure_psi")
    if radius_needed_ft is not None:
        _require_positive(radius_needed_ft, "radius_needed_ft")

    candidates, exclusions = [], []
    for r in records:
        model = r["model"]
        if r["application_type"] != application_type:
            continue  # different category, not an exclusion worth reporting
        pr = r.get("pressure_range_psi")
        if not pr:
            exclusions.append(Exclusion(model, "no published pressure range on record"))
            continue
        if not (pr["min"] <= design_pressure_psi <= pr["max"]):
            exclusions.append(Exclusion(
                model, f"design pressure {design_pressure_psi:g} psi outside published "
                       f"range {pr['min']:g}-{pr['max']:g} psi"))
            continue
        if radius_needed_ft is not None:
            rr = r.get("radius_range_ft")
            if not rr:
                exclusions.append(Exclusion(model, "no published radius range on record"))
                continue
            if not (rr["min"] <= radius_needed_ft <= rr["max"]):
                exclusions.append(Exclusion(
                    model, f"needed radius {radius_needed_ft:g} ft outside published "
                           f"range {rr['min']:g}-{rr['max']:g} ft"))
                continue
        rec = r.get("recommended_pressure_psi")
        closeness = abs(design_pressure_psi - rec) if rec else float("inf")
        candidates.append((closeness, Candidate(
            model=model, manufacturer=r["manufacturer"],
            application_type=r["application_type"],
            reason=("operates at design pressure per published range"
                    + (f"; recommended pressure {rec:g} psi" if rec else "")),
            source_url=r["source"]["url"])))
    candidates.sort(key=lambda c: (c[0], c[1].model))
    return SelectionResult(
        candidates=tuple(c for _, c in candidates),
        exclusions=tuple(exclusions))


def performance_rows(model_csv: str, performance_dir: Path = PERFORMANCE_DIR) -> list:
    """Load a product's published performance table.

    Returns the rows as dicts of floats/strings. Raises FileNotFoundError
    when the product has no committed performance table.
    """
    path = performance_dir / model_csv
    if not path.is_file():
        raise FileNotFoundError(
            f"no committed performance table {model_csv!r}; add it from the "
            "manufacturer's current document before using this product")
    with path.open() as f:
        lines = [l for l in f if not l.startswith("#")]
    rows = []
    for raw in csv.DictReader(lines):
        rows.append({k: (float(v) if _is_number(v) else v) for k, v in raw.items()})
    return rows


def _is_number(v):
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def published_performance(model_csv: str, pressure_psi: float,
                          match: dict = None,
                          performance_dir: Path = PERFORMANCE_DIR) -> dict:
    """Exact published performance row at a pressure (and optional extra
    match keys such as {'arc_degrees': 270} or {'nozzle': 3.0}).

    Raises ValueError when the exact pressure is not published, listing
    the published pressures - interpolating between rows is a design
    decision that must be made explicitly and documented, never silently.
    """
    _require_positive(pressure_psi, "pressure_psi")
    rows = performance_rows(model_csv, performance_dir)
    match = match or {}
    subset = [r for r in rows if all(r.get(k) == v for k, v in match.items())]
    if not subset:
        raise ValueError(f"no published rows in {model_csv} matching {match}")
    hits = [r for r in subset if r.get("pressure_psi") == pressure_psi]
    if not hits:
        avail = sorted({r["pressure_psi"] for r in subset})
        raise ValueError(
            f"{model_csv}: no published row at {pressure_psi:g} psi for {match or 'any'}; "
            f"published pressures: {avail}. Use a published pressure or document an "
            "explicit interpolation decision")
    if len(hits) > 1:
        raise ValueError(
            f"{model_csv}: {len(hits)} rows match {pressure_psi:g} psi and {match}; "
            "add match keys to make the lookup unambiguous")
    return hits[0]
