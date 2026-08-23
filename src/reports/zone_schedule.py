"""Zone schedule per docs/07 section 18.

A row carries every required field; the renderer never fills a blank
with a guess — missing optional values print as "field verify".
"""

from dataclasses import dataclass, field

from calculators.units import _require_positive

FIELD_VERIFY = "field verify"


@dataclass(frozen=True)
class ZoneRow:
    zone_number: int
    name: str
    hydrozone: str                 # e.g. "turf / full sun / silt loam / flat"
    application: str               # spray / rotary_nozzle / rotor / drip ...
    area_sqft: float
    device_model: str
    nozzle_and_arc: str            # e.g. "R-VAN18, 90-360 deg"
    quantity: int
    device_flow_gpm: str           # per-device flow or range, as published
    total_flow_gpm: float
    required_pressure_psi: float
    critical_path_loss_psi: float = None
    residual_pressure_psi: float = None
    design_margin_psi: float = None
    precipitation_rate_in_hr: float = None
    soil_and_root_notes: str = ""
    runtime_minutes: float = None
    cycles: int = None
    interval_days: str = ""
    controller_program: str = ""
    field_verification_notes: str = ""

    def __post_init__(self):
        _require_positive(self.area_sqft, "area_sqft")
        _require_positive(self.total_flow_gpm, "total_flow_gpm")
        _require_positive(self.required_pressure_psi, "required_pressure_psi")
        if self.quantity < 1:
            raise ValueError("quantity must be at least 1")


def _num(v, unit=""):
    if v is None:
        return FIELD_VERIFY
    return f"{v:g}{unit}"


def to_markdown(rows: list) -> str:
    """Render the zone schedule as a markdown table plus per-zone notes."""
    if not rows:
        raise ValueError("a zone schedule needs at least one zone")
    header = ("| Zone | Name | Hydrozone | Device | Qty | Flow (gpm) | "
              "Pressure (psi) | Margin (psi) | PR (in/hr) | Runtime |")
    sep = "|" + "---|" * 10
    lines = [header, sep]
    for r in sorted(rows, key=lambda x: x.zone_number):
        runtime = FIELD_VERIFY
        if r.runtime_minutes is not None:
            runtime = f"{r.runtime_minutes:.0f} min"
            if r.cycles and r.cycles > 1:
                runtime += f" in {r.cycles} cycles"
        lines.append(
            f"| {r.zone_number} | {r.name} | {r.hydrozone} | "
            f"{r.device_model} ({r.nozzle_and_arc}) | {r.quantity} | "
            f"{r.total_flow_gpm:g} | {r.required_pressure_psi:g} | "
            f"{_num(r.design_margin_psi)} | {_num(r.precipitation_rate_in_hr)} | {runtime} |")
    notes = []
    for r in sorted(rows, key=lambda x: x.zone_number):
        detail = [f"**Zone {r.zone_number} — {r.name}**",
                  f"Application: {r.application}; area {r.area_sqft:g} sq ft; "
                  f"device flow {r.device_flow_gpm}; "
                  f"critical-path loss {_num(r.critical_path_loss_psi, ' psi')}; "
                  f"residual {_num(r.residual_pressure_psi, ' psi')}."]
        if r.soil_and_root_notes:
            detail.append(f"Soil/roots: {r.soil_and_root_notes}")
        if r.interval_days:
            detail.append(f"Interval: {r.interval_days}")
        if r.controller_program:
            detail.append(f"Controller program: {r.controller_program}")
        if r.field_verification_notes:
            detail.append(f"Field verify: {r.field_verification_notes}")
        notes.append("  \n".join(detail))
    return "\n".join(lines) + "\n\n" + "\n\n".join(notes) + "\n"
