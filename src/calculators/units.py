"""Unit conversions with explicit, documented constants.

Sources:
- Pressure/head of water: 1 psi supports a column of water about 2.31 ft
  high at ordinary irrigation temperatures, i.e. 0.433 psi per foot of
  elevation. These are the standard values used throughout the Rain Bird
  Landscape Irrigation Design Manual (knowledge/source_manifest.yaml:
  "Landscape Irrigation Design Manual") and general hydraulic references.
- Exact legal definitions: 1 gallon = 3.785411784 L, 1 inch = 25.4 mm,
  1 psi = 6.894757 kPa (NIST SP 811 conversion factors).

All functions reject non-finite input. Functions whose physical quantity
cannot be negative (flow, pressure magnitude) also reject negatives.
"""

import math

# Pressure <-> water column (industry-standard rounded values; see module docstring)
PSI_PER_FOOT_OF_WATER = 0.433
FEET_OF_WATER_PER_PSI = 2.31

# Exact conversion factors (NIST SP 811)
LITERS_PER_GALLON = 3.785411784
MM_PER_INCH = 25.4
KPA_PER_PSI = 6.894757

# 1 cubic foot per second = 448.831 gallons per minute (derived: 7.48052 gal/ft^3 * 60)
GPM_PER_CFS = 448.831


def _require_finite(value: float, name: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number, got {value!r}")


def _require_positive(value: float, name: str) -> None:
    _require_finite(value, name)
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero, got {value!r}")


def _require_non_negative(value: float, name: str) -> None:
    _require_finite(value, name)
    if value < 0:
        raise ValueError(f"{name} must not be negative, got {value!r}")


def psi_to_feet_of_head(psi: float) -> float:
    """Convert pressure in psi to feet of water column. Sign is preserved."""
    _require_finite(psi, "psi")
    return psi * FEET_OF_WATER_PER_PSI


def feet_of_head_to_psi(feet: float) -> float:
    """Convert feet of water column to psi. Sign is preserved."""
    _require_finite(feet, "feet")
    return feet * PSI_PER_FOOT_OF_WATER


def gpm_to_gph(gpm: float) -> float:
    _require_non_negative(gpm, "gpm")
    return gpm * 60.0


def gph_to_gpm(gph: float) -> float:
    _require_non_negative(gph, "gph")
    return gph / 60.0


def gpm_to_cfs(gpm: float) -> float:
    _require_non_negative(gpm, "gpm")
    return gpm / GPM_PER_CFS


def gallons_to_liters(gallons: float) -> float:
    _require_non_negative(gallons, "gallons")
    return gallons * LITERS_PER_GALLON


def inches_to_millimeters(inches: float) -> float:
    _require_finite(inches, "inches")
    return inches * MM_PER_INCH


def psi_to_kpa(psi: float) -> float:
    _require_finite(psi, "psi")
    return psi * KPA_PER_PSI
