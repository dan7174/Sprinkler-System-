"""Pump calculations: total dynamic head, pump-curve operating point,
NPSH available.

Method sources (registered in knowledge/source_manifest.yaml):

- Total dynamic head (TDH) = static lift + friction losses + pressure
  head required at the discharge, all expressed in feet of water
  (standard pump-application practice; see Rain Bird Landscape
  Irrigation Design Manual pump section).
- A pump is never selected from horsepower alone: the required flow and
  TDH must be checked against the manufacturer's published pump curve
  (Agent Charter / docs/04 section 9).
- NPSH available = atmospheric head - static suction lift - suction
  friction - vapor pressure head. NPSHa must exceed the manufacturer's
  published NPSH required by a design margin, or the pump will cavitate.

Curve points, NPSHr, atmospheric and vapor-pressure heads are inputs
from cited sources (pump curve sheet, site elevation, water
temperature); this module never assumes them.
"""

from dataclasses import dataclass

from .units import _require_finite, _require_non_negative, _require_positive


def total_dynamic_head_ft(
    static_lift_ft: float,
    friction_loss_ft: float,
    pressure_head_ft: float,
) -> float:
    """TDH in feet. static_lift_ft is positive when the discharge point is
    above the water source; a flooded suction (source above pump) may be
    negative. Friction and required pressure head cannot be negative."""
    _require_finite(static_lift_ft, "static_lift_ft")
    _require_non_negative(friction_loss_ft, "friction_loss_ft")
    _require_non_negative(pressure_head_ft, "pressure_head_ft")
    tdh = static_lift_ft + friction_loss_ft + pressure_head_ft
    if tdh <= 0:
        raise ValueError(
            f"computed TDH {tdh!r} ft is not positive; check the inputs — "
            "a system with no head requirement does not need a pump"
        )
    return tdh


def head_at_flow_ft(curve_points: list, flow_gpm: float) -> float:
    """Interpolate pump head (ft) at a flow from published curve points.

    ``curve_points`` is a list of (flow_gpm, head_ft) taken from the
    manufacturer's pump curve, in any order; at least two points are
    required. Interpolation is linear between adjacent points and the
    function REFUSES to extrapolate outside the published curve.
    """
    if len(curve_points) < 2:
        raise ValueError("at least two pump-curve points are required")
    _require_non_negative(flow_gpm, "flow_gpm")
    points = sorted(curve_points)
    flows = [p[0] for p in points]
    if len(set(flows)) != len(flows):
        raise ValueError("pump-curve points contain duplicate flows")
    for flow, head in points:
        _require_non_negative(flow, "curve flow")
        _require_non_negative(head, "curve head")
    if not (flows[0] <= flow_gpm <= flows[-1]):
        raise ValueError(
            f"flow {flow_gpm!r} gpm is outside the published curve range "
            f"[{flows[0]}, {flows[-1]}]; do not extrapolate a pump curve"
        )
    for (f1, h1), (f2, h2) in zip(points, points[1:]):
        if f1 <= flow_gpm <= f2:
            if f1 == flow_gpm:
                return h1
            fraction = (flow_gpm - f1) / (f2 - f1)
            return h1 + fraction * (h2 - h1)
    return points[-1][1]


@dataclass(frozen=True)
class OperatingPointCheck:
    flow_gpm: float
    required_tdh_ft: float
    pump_head_at_flow_ft: float
    margin_ft: float
    passes: bool
    curve_source: str


def check_operating_point(
    curve_points: list,
    flow_gpm: float,
    required_tdh_ft: float,
    curve_source: str,
) -> OperatingPointCheck:
    """Check that the pump delivers the required TDH at the design flow.

    ``curve_source`` identifies the manufacturer curve document (title
    and revision) so the check is traceable.
    """
    _require_positive(required_tdh_ft, "required_tdh_ft")
    if not curve_source or not curve_source.strip():
        raise ValueError("curve_source is required so the pump check is traceable")
    available = head_at_flow_ft(curve_points, flow_gpm)
    margin = available - required_tdh_ft
    return OperatingPointCheck(
        flow_gpm=flow_gpm,
        required_tdh_ft=required_tdh_ft,
        pump_head_at_flow_ft=available,
        margin_ft=margin,
        passes=margin >= 0,
        curve_source=curve_source,
    )


@dataclass(frozen=True)
class NpshCheck:
    npsh_available_ft: float
    npsh_required_ft: float
    design_margin_ft: float
    margin_ft: float
    passes: bool


def npsh_available_ft(
    atmospheric_head_ft: float,
    static_suction_lift_ft: float,
    suction_friction_ft: float,
    vapor_pressure_head_ft: float,
) -> float:
    """NPSHa = atmospheric head - suction lift - suction friction - vapor head.

    Atmospheric head depends on site elevation (about 33.9 ft at sea
    level, less at altitude) and vapor head on water temperature; both
    must come from cited references for the actual site conditions.
    static_suction_lift_ft is positive when the pump is above the water
    surface; flooded suction is negative and adds head.
    """
    _require_positive(atmospheric_head_ft, "atmospheric_head_ft")
    _require_finite(static_suction_lift_ft, "static_suction_lift_ft")
    _require_non_negative(suction_friction_ft, "suction_friction_ft")
    _require_non_negative(vapor_pressure_head_ft, "vapor_pressure_head_ft")
    return (
        atmospheric_head_ft
        - static_suction_lift_ft
        - suction_friction_ft
        - vapor_pressure_head_ft
    )


def check_npsh(
    npsha_ft: float,
    npsh_required_ft: float,
    design_margin_ft: float,
) -> NpshCheck:
    """Compare NPSH available with the manufacturer's NPSH required plus a
    caller-chosen design margin (a common conservative practice is 2 ft
    or more; record the margin policy used)."""
    _require_finite(npsha_ft, "npsha_ft")
    _require_positive(npsh_required_ft, "npsh_required_ft")
    _require_non_negative(design_margin_ft, "design_margin_ft")
    margin = npsha_ft - (npsh_required_ft + design_margin_ft)
    return NpshCheck(
        npsh_available_ft=npsha_ft,
        npsh_required_ft=npsh_required_ft,
        design_margin_ft=design_margin_ft,
        margin_ft=margin,
        passes=margin >= 0,
    )
