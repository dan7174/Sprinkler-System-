"""Irrigation-scheduling calculations: plant demand, interval, runtime,
cycle-and-soak.

Formula sources (registered in knowledge/source_manifest.yaml):

- Crop/landscape evapotranspiration: ETc = ETo * Kc, where ETo is
  reference evapotranspiration and Kc a crop or landscape coefficient
  (standard method per Irrigation Association scheduling practice and
  the Rain Bird Landscape Irrigation Design Manual).
- Readily available water: RAW = AWHC * root depth * MAD, where AWHC is
  the soil's available water-holding capacity and MAD the management
  allowed depletion fraction.
- Runtime: minutes = 60 * gross depth / precipitation rate.
- Cycle-and-soak: when the application rate exceeds the soil intake
  rate, runoff begins once surface storage is filled; the maximum cycle
  is 60 * storage / (PR - intake rate) minutes.

A calculated schedule is a STARTING POINT. It must be adjusted from
field observation, and local watering restrictions override it. ETo, Kc,
AWHC and intake-rate values must come from cited local sources — this
module computes, it does not supply agronomic data.
"""

import math
from dataclasses import dataclass

from .units import _require_finite, _require_non_negative, _require_positive


def crop_evapotranspiration_in_per_day(eto_in_per_day: float, coefficient: float) -> float:
    """ETc = ETo * Kc (or landscape coefficient KL).

    The coefficient must come from a cited source for the actual plant
    and region; typical turf values differ by species and season.
    """
    _require_non_negative(eto_in_per_day, "eto_in_per_day")
    _require_positive(coefficient, "coefficient")
    if coefficient > 1.5:
        raise ValueError(
            f"coefficient {coefficient!r} exceeds 1.5; landscape/crop coefficients "
            "above this are not credible — check the source and units"
        )
    return eto_in_per_day * coefficient


def net_daily_demand_in(etc_in_per_day: float, effective_rain_in_per_day: float = 0.0) -> float:
    """Net irrigation demand after effective rainfall, never below zero."""
    _require_non_negative(etc_in_per_day, "etc_in_per_day")
    _require_non_negative(effective_rain_in_per_day, "effective_rain_in_per_day")
    return max(0.0, etc_in_per_day - effective_rain_in_per_day)


def readily_available_water_in(
    awhc_in_per_ft: float,
    root_depth_ft: float,
    mad_fraction: float,
) -> float:
    """RAW = AWHC (in/ft) * root depth (ft) * MAD (fraction 0-1)."""
    _require_positive(awhc_in_per_ft, "awhc_in_per_ft")
    _require_positive(root_depth_ft, "root_depth_ft")
    _require_positive(mad_fraction, "mad_fraction")
    if mad_fraction > 1.0:
        raise ValueError(f"mad_fraction must be a fraction <= 1, got {mad_fraction!r}")
    return awhc_in_per_ft * root_depth_ft * mad_fraction


def irrigation_interval_days(raw_in: float, net_daily_demand: float) -> float:
    """Days between irrigations = RAW / net daily demand.

    Returns the exact value; round DOWN to whole days for a practical
    schedule so the soil is refilled before depletion exceeds MAD.
    """
    _require_positive(raw_in, "raw_in")
    _require_positive(net_daily_demand, "net_daily_demand")
    return raw_in / net_daily_demand


def gross_depth_in(net_depth_in: float, efficiency_fraction: float) -> float:
    """Gross application depth = net depth / irrigation efficiency.

    Efficiency (or lower-quarter distribution uniformity) must be in
    (0, 1]; a claimed efficiency above 1 is impossible.
    """
    _require_positive(net_depth_in, "net_depth_in")
    _require_positive(efficiency_fraction, "efficiency_fraction")
    if efficiency_fraction > 1.0:
        raise ValueError(f"efficiency_fraction must be <= 1, got {efficiency_fraction!r}")
    return net_depth_in / efficiency_fraction


def runtime_minutes(gross_depth: float, precipitation_rate_in_per_hr: float) -> float:
    """Zone runtime in minutes = 60 * gross depth / precipitation rate."""
    _require_positive(gross_depth, "gross_depth")
    _require_positive(precipitation_rate_in_per_hr, "precipitation_rate_in_per_hr")
    return 60.0 * gross_depth / precipitation_rate_in_per_hr


def max_cycle_minutes_before_runoff(
    precipitation_rate_in_per_hr: float,
    soil_intake_rate_in_per_hr: float,
    surface_storage_in: float,
):
    """Longest single cycle before runoff begins, in minutes.

    Runoff starts once (PR - intake rate) has filled the allowable
    surface storage (a function of slope and surface condition, from a
    cited source). Returns None when PR <= intake rate: the soil absorbs
    water as fast as it is applied and no runoff limit applies.
    """
    _require_positive(precipitation_rate_in_per_hr, "precipitation_rate_in_per_hr")
    _require_positive(soil_intake_rate_in_per_hr, "soil_intake_rate_in_per_hr")
    _require_positive(surface_storage_in, "surface_storage_in")
    excess = precipitation_rate_in_per_hr - soil_intake_rate_in_per_hr
    if excess <= 0:
        return None
    return 60.0 * surface_storage_in / excess


@dataclass(frozen=True)
class CycleSoakPlan:
    total_runtime_minutes: float
    cycles: int
    minutes_per_cycle: float
    cycle_and_soak_required: bool


def cycle_and_soak(total_runtime: float, max_cycle_minutes) -> CycleSoakPlan:
    """Split a runtime into equal cycles no longer than the runoff limit.

    ``max_cycle_minutes`` of None (no runoff limit) yields one cycle.
    Soak time between cycles must allow the surface to drain — at
    minimum long enough for the applied excess to infiltrate; schedule
    other zones during the soak.
    """
    _require_positive(total_runtime, "total_runtime")
    if max_cycle_minutes is None or total_runtime <= max_cycle_minutes:
        return CycleSoakPlan(total_runtime, 1, total_runtime, False)
    _require_positive(max_cycle_minutes, "max_cycle_minutes")
    cycles = math.ceil(total_runtime / max_cycle_minutes)
    return CycleSoakPlan(total_runtime, cycles, total_runtime / cycles, True)
