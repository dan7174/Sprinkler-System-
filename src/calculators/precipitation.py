"""Precipitation-rate and matched-precipitation calculations.

Formula source (registered in knowledge/source_manifest.yaml):

- Precipitation rate for head-to-head layouts (Rain Bird Landscape
  Irrigation Design Manual; same form used by Irrigation Association
  auditing references):

      PR = 96.3 * total zone GPM / (head spacing * row spacing)   [in/hr]

  The constant 96.3 converts gallons per minute per square foot to
  inches per hour: 231 in^3/gal * 60 min/hr / 144 in^2/ft^2 = 96.25,
  published rounded to 96.3.

- Triangular spacing: rows are offset and spaced at 0.866 * head
  spacing (cos 30 degrees), so the area per head is S * 0.866*S.

- Part-circle heads: a head watering an arc applies its whole flow to a
  fraction of a circle. For matched-precipitation checks, normalize each
  head to its full-circle-equivalent flow = flow * 360 / arc.

A calculated precipitation rate describes the layout geometry; actual
applied water must still be confirmed with a catch-can audit
(docs/03, section 7).
"""

from .units import _require_positive

PRECIPITATION_CONSTANT = 96.3
TRIANGULAR_ROW_FACTOR = 0.866  # cos(30 degrees), rounded as published


def precipitation_rate_rectangular(
    total_zone_gpm: float,
    head_spacing_ft: float,
    row_spacing_ft: float,
) -> float:
    """PR in in/hr for square or rectangular head layouts.

    PR = 96.3 * GPM / (S * L). For a square layout pass the same value
    for both spacings.
    """
    _require_positive(total_zone_gpm, "total_zone_gpm")
    _require_positive(head_spacing_ft, "head_spacing_ft")
    _require_positive(row_spacing_ft, "row_spacing_ft")
    return PRECIPITATION_CONSTANT * total_zone_gpm / (head_spacing_ft * row_spacing_ft)


def precipitation_rate_triangular(total_zone_gpm: float, head_spacing_ft: float) -> float:
    """PR in in/hr for equilateral triangular head layouts.

    Row spacing is 0.866 * head spacing, so
    PR = 96.3 * GPM / (S * 0.866 * S).
    """
    _require_positive(total_zone_gpm, "total_zone_gpm")
    _require_positive(head_spacing_ft, "head_spacing_ft")
    return PRECIPITATION_CONSTANT * total_zone_gpm / (
        head_spacing_ft * TRIANGULAR_ROW_FACTOR * head_spacing_ft
    )


def precipitation_rate_from_area(total_zone_gpm: float, irrigated_area_sqft: float) -> float:
    """PR in in/hr from total zone flow over the actual irrigated area.

    Use for irregular areas where a measured/verified irrigated area is
    available instead of a regular spacing grid.
    """
    _require_positive(total_zone_gpm, "total_zone_gpm")
    _require_positive(irrigated_area_sqft, "irrigated_area_sqft")
    return PRECIPITATION_CONSTANT * total_zone_gpm / irrigated_area_sqft


def full_circle_equivalent_gpm(flow_gpm: float, arc_degrees: float) -> float:
    """Normalize a part-circle head to its full-circle-equivalent flow.

    A 90-degree head at 1 gpm waters a quarter of the area a full-circle
    head covers, so its equivalent full-circle flow is 4 gpm.
    """
    _require_positive(flow_gpm, "flow_gpm")
    _require_positive(arc_degrees, "arc_degrees")
    if arc_degrees > 360:
        raise ValueError(f"arc_degrees cannot exceed 360, got {arc_degrees!r}")
    return flow_gpm * 360.0 / arc_degrees


def matched_precipitation_check(heads: list, tolerance_fraction: float = 0.10) -> dict:
    """Check whether heads on one zone apply water at a matched rate.

    ``heads`` is a list of (flow_gpm, arc_degrees) pairs. Each head is
    normalized to full-circle-equivalent flow; the zone is matched when
    the spread between the highest and lowest equivalent flow is within
    ``tolerance_fraction`` of the lowest (default 10 percent, a common
    matched-precipitation screening tolerance — record the tolerance
    used in the design report).

    Returns a dict with the equivalent flows, spread and pass/fail so the
    report can show the work, not just the verdict.
    """
    if not heads:
        raise ValueError("at least one head is required")
    _require_positive(tolerance_fraction, "tolerance_fraction")
    equivalents = [full_circle_equivalent_gpm(flow, arc) for flow, arc in heads]
    lowest, highest = min(equivalents), max(equivalents)
    spread_fraction = (highest - lowest) / lowest
    return {
        "full_circle_equivalent_gpm": equivalents,
        "lowest_equivalent_gpm": lowest,
        "highest_equivalent_gpm": highest,
        "spread_fraction": spread_fraction,
        "tolerance_fraction": tolerance_fraction,
        "matched": spread_fraction <= tolerance_fraction,
    }
