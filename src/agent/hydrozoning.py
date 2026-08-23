"""Hydrozoning and valve-zone grouping, per docs/04 sections 8, 10 and 12.

Rules encoded here:
- Areas are grouped into hydrozones only when plant type, sun exposure,
  soil, slope class and irrigation method can all match (docs/04 s.12).
- The application method is recommended from the actual product catalog:
  a method is feasible only when a current product's published radius
  range fits the area's narrowest dimension (docs/02 - no guessing
  performance). Planted beds and gardens go to drip/low-volume per
  low-volume design practice.
- Valve zones never mix hydrozones or exceed the safe zone flow
  (docs/04 s.10: no mixed methods; s.9: zones respect available flow).
"""

import math
from dataclasses import dataclass, field

from calculators.units import _require_positive

SLOPE_CLASS_BOUNDARIES = (5.0, 12.0)  # percent: flat / moderate / steep


def slope_class(slope_percent: float) -> str:
    if slope_percent < 0:
        raise ValueError(f"slope_percent cannot be negative, got {slope_percent!r}")
    if slope_percent <= SLOPE_CLASS_BOUNDARIES[0]:
        return "flat"
    if slope_percent <= SLOPE_CLASS_BOUNDARIES[1]:
        return "moderate"
    return "steep"


@dataclass(frozen=True)
class MethodOption:
    method: str
    reason: str
    example_products: tuple


def feasible_methods(plant_type: str, min_dimension_ft: float, catalog: list) -> list:
    """Rank feasible application methods for one landscape area.

    Turf methods are derived from the catalog: a spray/rotary/rotor
    method is offered only when a current product's published radius
    range can water a strip as narrow as ``min_dimension_ft`` without
    overshooting it (radius min <= dimension) and reach far enough that
    head-to-head spacing is practical (radius max * 2 >= dimension is
    NOT required - multiple rows handle width - but radius min must not
    exceed the dimension). Beds, gardens and trees route to low-volume.
    """
    _require_positive(min_dimension_ft, "min_dimension_ft")
    if plant_type in ("shrubs", "groundcover", "containers", "mixed_planting"):
        return [MethodOption("drip", "Planted beds water at plant level with drip/low-volume "
                             "to keep foliage dry and avoid overspray.", ())]
    if plant_type == "trees":
        return [MethodOption("tree_watering", "Trees need deep watering over the expanding "
                             "root zone, separate from turf schedules.", ())]
    if plant_type != "turf":
        raise ValueError(f"unknown plant_type {plant_type!r}")

    options = []
    by_method = {}
    for p in catalog:
        rr = p.get("radius_range_ft")
        if not rr:
            continue
        method = {"rotary_nozzle": "rotary_nozzle", "rotor": "rotor",
                  "spray_head": "spray"}.get(p["application_type"])
        if not method:
            continue
        if rr["min"] <= min_dimension_ft:
            by_method.setdefault(method, []).append(p["model"])
    # Prefer the method whose products fit with the fewest rows of heads:
    # rotors for large areas, rotary nozzles for mid, sprays for small.
    preference = ["rotor", "rotary_nozzle", "spray"]
    for m in preference:
        if m in by_method:
            options.append(MethodOption(
                m,
                f"Current catalog products can cover a {min_dimension_ft:g} ft dimension "
                "at published radii.",
                tuple(sorted(by_method[m])[:4])))
    if not options:
        options.append(MethodOption(
            "drip",
            f"No cataloged spray/rotary/rotor product has a published minimum radius "
            f"<= {min_dimension_ft:g} ft; use low-volume or add products to the catalog.",
            ()))
    return options


@dataclass(frozen=True)
class Hydrozone:
    key: tuple
    plant_type: str
    sun_exposure: str
    soil_texture: str
    slope: str
    method: str
    areas: tuple
    total_area_sqft: float


def assign_hydrozones(areas: list, catalog: list) -> list:
    """Group landscape areas into hydrozones.

    Each area is a dict with: name, plant_type, sun_exposure,
    soil_texture, slope_percent, area_sqft, min_dimension_ft.
    Areas join the same hydrozone only when plant type, sun, soil,
    slope class and recommended method all match.
    """
    zones = {}
    for a in areas:
        for req in ("name", "plant_type", "sun_exposure", "soil_texture",
                    "slope_percent", "area_sqft", "min_dimension_ft"):
            if req not in a:
                raise ValueError(f"area {a.get('name','?')!r} is missing {req!r}")
        _require_positive(a["area_sqft"], "area_sqft")
        method = feasible_methods(a["plant_type"], a["min_dimension_ft"], catalog)[0].method
        key = (a["plant_type"], a["sun_exposure"], a["soil_texture"],
               slope_class(a["slope_percent"]), method)
        zones.setdefault(key, []).append(a)
    result = []
    for key, group in zones.items():
        result.append(Hydrozone(
            key=key, plant_type=key[0], sun_exposure=key[1], soil_texture=key[2],
            slope=key[3], method=key[4],
            areas=tuple(g["name"] for g in group),
            total_area_sqft=sum(g["area_sqft"] for g in group)))
    result.sort(key=lambda z: z.key)
    return result


@dataclass(frozen=True)
class ValveZone:
    zone_number: int
    hydrozone_key: tuple
    devices: tuple           # indices into the input device list
    total_flow_gpm: float


def group_into_valve_zones(devices: list, max_zone_flow_gpm: float) -> list:
    """Split one hydrozone's devices into valve zones within the flow limit.

    ``devices`` is a list of dicts with flow_gpm and hydrozone_key.
    Devices from different hydrozones are never mixed (docs/04 s.10).
    A single device whose flow exceeds the limit is an error - the
    hydraulic limit is never overridden by grouping (docs/08 s.24).
    """
    _require_positive(max_zone_flow_gpm, "max_zone_flow_gpm")
    by_hz = {}
    for i, d in enumerate(devices):
        if d["flow_gpm"] > max_zone_flow_gpm:
            raise ValueError(
                f"device {i} needs {d['flow_gpm']} gpm, above the safe zone flow "
                f"{max_zone_flow_gpm} gpm; the hydraulic limit cannot be overridden")
        by_hz.setdefault(tuple(d["hydrozone_key"]), []).append(i)
    zones, n = [], 1
    for key in sorted(by_hz):
        current, flow = [], 0.0
        for i in by_hz[key]:
            f = devices[i]["flow_gpm"]
            if flow + f > max_zone_flow_gpm + 1e-9 and current:
                zones.append(ValveZone(n, key, tuple(current), round(flow, 3)))
                n += 1
                current, flow = [], 0.0
            current.append(i)
            flow += f
        if current:
            zones.append(ValveZone(n, key, tuple(current), round(flow, 3)))
            n += 1
    return zones
