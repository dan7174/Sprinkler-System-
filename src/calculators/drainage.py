"""Basic site-drainage calculations: runoff estimate, grade, and gravity
pipe capacity.

Method sources (registered in knowledge/source_manifest.yaml):

- Rational method peak runoff (standard small-catchment practice, per
  FHWA HEC-22 Urban Drainage Design Manual):

      Q = C * i * A     [cfs]

  with C the dimensionless runoff coefficient (0-1), i the design
  rainfall intensity in in/hr for the time of concentration and return
  period, and A the drainage area in ACRES. The unit conversion constant
  is 1.008 and is conventionally taken as 1.0.

- Manning's equation for a circular pipe flowing full (FHWA HEC-22):

      Q = (1.49 / n) * A * R^(2/3) * S^(1/2)     [cfs]

  with A the flow area in sq ft, R = D/4 the hydraulic radius of a full
  circular pipe, S the slope in ft/ft and n the Manning roughness.

This module supports BASIC drainage screening only. Runoff coefficients,
design intensities and roughness values must come from cited local/
manufacturer sources. Larger drainage, public storm systems, retaining
walls and anything affecting structures or neighboring property require
civil or geotechnical review (Agent Charter safety rule).
"""

import math

from .units import _require_non_negative, _require_positive

# Typical published Manning n ranges (FHWA HEC-22 and pipe-manufacturer
# data) for reference only; verify against the actual pipe specified.
TYPICAL_MANNINGS_N = {
    "smooth_plastic_pvc": 0.010,
    "corrugated_hdpe_smooth_interior": 0.012,
    "corrugated_hdpe_single_wall": 0.020,
}


def rational_peak_flow_cfs(
    runoff_coefficient: float,
    intensity_in_per_hr: float,
    area_acres: float,
) -> float:
    """Rational-method peak runoff Q = C*i*A in cfs (A in acres)."""
    _require_non_negative(runoff_coefficient, "runoff_coefficient")
    if runoff_coefficient > 1.0:
        raise ValueError(
            f"runoff_coefficient must be <= 1 (got {runoff_coefficient!r}); "
            "more water cannot run off than falls"
        )
    _require_positive(intensity_in_per_hr, "intensity_in_per_hr")
    _require_positive(area_acres, "area_acres")
    return runoff_coefficient * intensity_in_per_hr * area_acres


def slope_ft_per_ft(rise_ft: float, run_ft: float) -> float:
    """Grade as ft/ft from a rise over a horizontal run. Positive = falling
    toward the discharge (use the drop in elevation as a positive rise)."""
    _require_positive(rise_ft, "rise_ft")
    _require_positive(run_ft, "run_ft")
    return rise_ft / run_ft


def mannings_full_flow_cfs(
    diameter_in: float,
    slope: float,
    mannings_n: float,
) -> float:
    """Capacity of a circular pipe flowing full, in cfs.

    ``slope`` is ft/ft (e.g. 0.01 for 1 percent). Full-flow capacity is a
    screening number; actual gravity drains should be designed with some
    freeboard and checked for minimum self-cleaning velocity.
    """
    _require_positive(diameter_in, "diameter_in")
    _require_positive(slope, "slope")
    _require_positive(mannings_n, "mannings_n")
    diameter_ft = diameter_in / 12.0
    area_sqft = math.pi * diameter_ft ** 2 / 4.0
    hydraulic_radius_ft = diameter_ft / 4.0
    return (1.49 / mannings_n) * area_sqft * hydraulic_radius_ft ** (2.0 / 3.0) * math.sqrt(slope)
