"""Zone compatibility checks, per docs/04 section 10.

A valve zone passes only when:
- all devices use one application method (no sprays + rotors + drip mixes),
- all devices can operate at the zone design pressure per their
  published pressure ranges,
- precipitation is matched across the zone within tolerance,
- total flow stays within the safe zone flow.

Results always carry the reasons, never a bare pass/fail.
"""

from dataclasses import dataclass

from calculators.precipitation import matched_precipitation_check
from calculators.units import _require_positive


@dataclass(frozen=True)
class CompatibilityResult:
    passes: bool
    failures: tuple
    warnings: tuple
    matched_precipitation: dict


def check_zone(devices: list, design_pressure_psi: float,
               max_zone_flow_gpm: float,
               matched_tolerance: float = 0.10) -> CompatibilityResult:
    """Check one valve zone's devices for compatibility.

    Each device dict needs: model, application_type, flow_gpm,
    arc_degrees, pressure_range_psi ({min,max}, from the product record).
    """
    if not devices:
        raise ValueError("a zone needs at least one device")
    _require_positive(design_pressure_psi, "design_pressure_psi")
    _require_positive(max_zone_flow_gpm, "max_zone_flow_gpm")

    failures, warnings = [], []

    methods = {d["application_type"] for d in devices}
    if len(methods) > 1:
        failures.append(
            f"mixed application methods on one valve: {sorted(methods)}; "
            "sprays, rotary nozzles, rotors and drip must not share a zone "
            "unless compatibility is explicitly proven (docs/04 s.10)")

    for d in devices:
        pr = d.get("pressure_range_psi")
        if not pr:
            failures.append(f"{d['model']}: no published pressure range on record; "
                            "cannot confirm it operates at the design pressure")
            continue
        if not (pr["min"] <= design_pressure_psi <= pr["max"]):
            failures.append(
                f"{d['model']}: design pressure {design_pressure_psi:g} psi is outside "
                f"its published range {pr['min']:g}-{pr['max']:g} psi")

    total = sum(d["flow_gpm"] for d in devices)
    if total > max_zone_flow_gpm:
        failures.append(
            f"zone flow {total:.2f} gpm exceeds the safe zone flow "
            f"{max_zone_flow_gpm:g} gpm")

    matched = {}
    arcs = [(d["flow_gpm"], d.get("arc_degrees", 360)) for d in devices]
    if len(devices) > 1 and not any(m in ("drip_emitter", "inline_dripline") for m in methods):
        matched = matched_precipitation_check(arcs, matched_tolerance)
        if not matched["matched"]:
            failures.append(
                f"precipitation is not matched: full-circle-equivalent flows spread "
                f"{matched['spread_fraction']:.0%}, above the {matched_tolerance:.0%} "
                "tolerance; the heaviest-watered spot would drive overwatering everywhere else")
    if total > 0.8 * max_zone_flow_gpm and total <= max_zone_flow_gpm:
        warnings.append(
            f"zone flow {total:.2f} gpm uses more than 80% of the safe zone flow; "
            "little reserve remains for pressure variation or added heads")

    return CompatibilityResult(
        passes=not failures,
        failures=tuple(failures),
        warnings=tuple(warnings),
        matched_precipitation=matched,
    )
