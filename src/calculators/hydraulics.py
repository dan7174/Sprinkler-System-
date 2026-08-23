"""Hydraulic calculations: velocity, friction loss, elevation, pressure path.

Formula sources (registered in knowledge/source_manifest.yaml):

- Hazen-Williams pressure-loss equation, U.S. customary form used by
  irrigation pressure-loss charts (including the Rain Bird Landscape
  Irrigation Design Manual and Rain Bird friction-loss charts):

      P = 4.52 * Q^1.852 / (C^1.852 * d^4.8655)      [psi per foot of pipe]

  where Q is flow in gpm, C is the pipe roughness coefficient and d is
  the actual inside diameter in inches. Valid for water at ordinary
  temperatures in pressurized pipes; not valid for other fluids.

- Velocity in a circular pipe:

      V = 0.4085 * Q / d^2                            [ft/s]

  derived exactly from V = Q/A with unit conversion
  (0.4085 = 4 * 231 in^3/gal / (60 s/min * pi) / 144 ... standard form).

- Elevation: 0.433 psi change per foot of elevation (see units.py).

Velocity and pressure margins are design policy, not physics. Callers
must supply their limit and record its source; a commonly used
conservative limit for solvent-welded PVC mainlines is 5 ft/s (Rain Bird
Landscape Irrigation Design Manual), but this module does not hardcode
any universal limit.
"""

from dataclasses import dataclass, field

from .units import PSI_PER_FOOT_OF_WATER, _require_finite, _require_non_negative, _require_positive

VELOCITY_COEFFICIENT = 0.4085
HAZEN_WILLIAMS_COEFFICIENT = 4.52
HAZEN_WILLIAMS_FLOW_EXPONENT = 1.852
HAZEN_WILLIAMS_DIAMETER_EXPONENT = 4.8655

# Typical published C-factors for reference only; verify against the pipe
# actually specified and its manufacturer data before final design.
TYPICAL_C_FACTORS = {
    "pvc": 150,
    "polyethylene": 140,
    "new_steel": 140,
    "copper": 140,
    "galvanized_steel_aged": 100,
}


def water_velocity_fps(flow_gpm: float, inside_diameter_in: float) -> float:
    """Average water velocity in ft/s for a circular pipe flowing full.

    V = 0.4085 * Q / d^2, Q in gpm, d = actual inside diameter in inches.
    Nominal pipe size is not inside diameter; use the real ID for the
    specific pipe class (e.g. 1 in SCH40 PVC ID = 1.049 in).
    """
    _require_non_negative(flow_gpm, "flow_gpm")
    _require_positive(inside_diameter_in, "inside_diameter_in")
    return VELOCITY_COEFFICIENT * flow_gpm / (inside_diameter_in ** 2)


def hazen_williams_loss_psi(
    flow_gpm: float,
    inside_diameter_in: float,
    length_ft: float,
    c_factor: float,
) -> float:
    """Friction pressure loss in psi over a pipe length (Hazen-Williams).

    Uses the U.S. customary per-foot form P = 4.52 * Q^1.852 /
    (C^1.852 * d^4.8655), multiplied by length_ft. Fitting losses are not
    included; add them separately via equivalent lengths or published
    fitting losses.
    """
    _require_non_negative(flow_gpm, "flow_gpm")
    _require_positive(inside_diameter_in, "inside_diameter_in")
    _require_non_negative(length_ft, "length_ft")
    _require_positive(c_factor, "c_factor")
    if flow_gpm == 0 or length_ft == 0:
        return 0.0
    per_foot = (
        HAZEN_WILLIAMS_COEFFICIENT
        * flow_gpm ** HAZEN_WILLIAMS_FLOW_EXPONENT
        / (c_factor ** HAZEN_WILLIAMS_FLOW_EXPONENT
           * inside_diameter_in ** HAZEN_WILLIAMS_DIAMETER_EXPONENT)
    )
    return per_foot * length_ft


def elevation_pressure_change_psi(elevation_rise_ft: float) -> float:
    """Pressure change caused by elevation.

    elevation_rise_ft > 0 means the outlet is HIGHER than the reference
    point, which REDUCES pressure, so the returned value is negative.
    A drop in elevation (negative rise) returns a positive gain.
    """
    _require_finite(elevation_rise_ft, "elevation_rise_ft")
    return -elevation_rise_ft * PSI_PER_FOOT_OF_WATER


@dataclass(frozen=True)
class VelocityCheck:
    velocity_fps: float
    limit_fps: float
    limit_source: str
    passes: bool


def check_velocity(
    flow_gpm: float,
    inside_diameter_in: float,
    limit_fps: float,
    limit_source: str,
) -> VelocityCheck:
    """Compare pipe velocity against a caller-supplied limit.

    The limit and its source must be provided by the caller so the
    report stays traceable; no universal limit is hardcoded here.
    """
    _require_positive(limit_fps, "limit_fps")
    if not limit_source or not limit_source.strip():
        raise ValueError("limit_source is required so the velocity limit is traceable")
    velocity = water_velocity_fps(flow_gpm, inside_diameter_in)
    return VelocityCheck(
        velocity_fps=velocity,
        limit_fps=limit_fps,
        limit_source=limit_source,
        passes=velocity <= limit_fps,
    )


@dataclass(frozen=True)
class PressureStep:
    label: str
    change_psi: float
    running_pressure_psi: float


@dataclass(frozen=True)
class PressurePathResult:
    source_pressure_psi: float
    steps: tuple
    device_pressure_psi: float
    required_device_pressure_psi: float
    margin_psi: float
    passes: bool
    warnings: tuple = field(default_factory=tuple)

    def explain(self) -> str:
        """Human-readable breakdown of the full pressure path."""
        lines = [f"Source pressure: {self.source_pressure_psi:.1f} psi"]
        for step in self.steps:
            lines.append(
                f"  {step.label}: {step.change_psi:+.2f} psi -> {step.running_pressure_psi:.2f} psi"
            )
        lines.append(
            f"Device pressure: {self.device_pressure_psi:.2f} psi "
            f"(required {self.required_device_pressure_psi:.2f} psi, "
            f"margin {self.margin_psi:+.2f} psi) -> {'PASS' if self.passes else 'FAIL'}"
        )
        for warning in self.warnings:
            lines.append(f"  WARNING: {warning}")
        return "\n".join(lines)


def pressure_path(
    source_pressure_psi: float,
    losses: list,
    elevation_rise_ft: float,
    required_device_pressure_psi: float,
) -> PressurePathResult:
    """Calculate the critical pressure path for a zone.

    source pressure -> each named loss (meter, backflow, mainline, valve,
    lateral, ...) -> elevation adjustment -> device pressure.

    ``losses`` is a list of (label, loss_psi) pairs in path order; each
    loss must be >= 0 (elevation is handled separately and is the only
    step allowed to add pressure). The result shows every intermediate
    value so the report never just says "passes".
    """
    _require_positive(source_pressure_psi, "source_pressure_psi")
    _require_positive(required_device_pressure_psi, "required_device_pressure_psi")
    _require_finite(elevation_rise_ft, "elevation_rise_ft")

    steps = []
    warnings = []
    running = source_pressure_psi
    for label, loss_psi in losses:
        if not label or not str(label).strip():
            raise ValueError("every pressure-path step needs a non-empty label")
        _require_non_negative(loss_psi, f"loss for step '{label}'")
        running -= loss_psi
        steps.append(PressureStep(label=str(label), change_psi=-loss_psi,
                                  running_pressure_psi=running))
        if running <= 0:
            warnings.append(
                f"pressure fell to {running:.2f} psi at step '{label}'; "
                "the system cannot operate as designed"
            )

    elevation_change = elevation_pressure_change_psi(elevation_rise_ft)
    running += elevation_change
    steps.append(PressureStep(
        label=f"elevation ({elevation_rise_ft:+.1f} ft)",
        change_psi=elevation_change,
        running_pressure_psi=running,
    ))

    margin = running - required_device_pressure_psi
    return PressurePathResult(
        source_pressure_psi=source_pressure_psi,
        steps=tuple(steps),
        device_pressure_psi=running,
        required_device_pressure_psi=required_device_pressure_psi,
        margin_psi=margin,
        passes=margin >= 0 and not warnings,
        warnings=tuple(warnings),
    )
