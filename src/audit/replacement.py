"""Replacement compatibility checks, per docs/06 section 17
(obsolete products, steps 4-6).

Given what is known about the existing device and its zone, classify a
proposed replacement as:

- direct_replacement          — fits and performs within published data
- compatible_with_adjustments — fits, but schedule/nozzle adjustments needed
- redesign_required           — changes hydraulics or method; not a swap

Every classification carries its reasons and the hydraulic/scheduling
consequences (docs/06 step 6). Missing critical facts fail the check
instead of being assumed.
"""

from dataclasses import dataclass

from calculators.units import _require_positive


@dataclass(frozen=True)
class ReplacementCheck:
    classification: str
    reasons: tuple
    consequences: tuple
    field_verification: tuple


def check_replacement(existing: dict, new_model: str, catalog: list) -> ReplacementCheck:
    """Check one proposed swap.

    ``existing`` describes the device being replaced and its zone:
      application_type   (required) e.g. 'spray_head', 'rotary_nozzle', 'rotor'
      zone_pressure_psi  (required) measured or design pressure at the device
      radius_needed_ft   (optional) throw the position must cover
      inlet_size_in      (optional) thread size of the existing connection
      arc_needed_degrees (optional)
    """
    for req in ("application_type", "zone_pressure_psi"):
        if req not in existing:
            raise ValueError(f"existing device is missing {req!r}; measure or identify "
                             "it before checking a replacement")
    _require_positive(existing["zone_pressure_psi"], "zone_pressure_psi")

    rec = next((r for r in catalog if r["model"] == new_model), None)
    if rec is None:
        raise ValueError(f"{new_model!r} has no catalog record; add a current, sourced "
                         "record before proposing it as a replacement")

    reasons, consequences, verify = [], [], []
    redesign = False
    adjustments = False

    if rec["status"] != "current":
        adjustments = True
        reasons.append(f"{new_model} status is {rec['status']!r}; confirm availability "
                       "before specifying it")

    # Method change is a redesign, not a swap (docs/04 s.10: matched
    # precipitation and one method per zone).
    if rec["application_type"] != existing["application_type"]:
        redesign = True
        reasons.append(
            f"application method changes ({existing['application_type']} -> "
            f"{rec['application_type']}): precipitation rate and runtimes change for the "
            "whole zone, and mixed methods on one valve are not allowed")
        consequences.append(
            "The entire zone must convert together and the schedule must be rebuilt "
            "from the new method's precipitation rate")

    pr = rec.get("pressure_range_psi")
    if pr is None:
        adjustments = True
        verify.append(f"{new_model} has no published pressure range on record; verify "
                      "before installation")
    elif not (pr["min"] <= existing["zone_pressure_psi"] <= pr["max"]):
        redesign = True
        reasons.append(
            f"zone pressure {existing['zone_pressure_psi']:g} psi is outside {new_model}'s "
            f"published range {pr['min']:g}-{pr['max']:g} psi")
        consequences.append("Pressure regulation or a different product is required; "
                            "operating outside the published range voids the performance data")

    if existing.get("radius_needed_ft") is not None:
        rr = rec.get("radius_range_ft")
        if rr is None:
            adjustments = True
            verify.append(f"{new_model} has no published radius range; confirm coverage "
                          "for the {0:g} ft position".format(existing["radius_needed_ft"]))
        elif not (rr["min"] <= existing["radius_needed_ft"] <= rr["max"]):
            redesign = True
            reasons.append(
                f"needed radius {existing['radius_needed_ft']:g} ft is outside {new_model}'s "
                f"published range {rr['min']:g}-{rr['max']:g} ft")
            consequences.append("Head spacing no longer works; the layout around this "
                                "position must be reworked")

    if existing.get("inlet_size_in") is not None:
        inlet = rec.get("inlet_size_in")
        if inlet is None:
            verify.append(f"confirm {new_model} thread/inlet size against the existing "
                          f"{existing['inlet_size_in']:g} in connection")
        elif abs(inlet - existing["inlet_size_in"]) > 1e-9:
            adjustments = True
            reasons.append(
                f"inlet size differs ({existing['inlet_size_in']:g} in existing vs "
                f"{inlet:g} in new): an adapter or fitting change is needed")

    if existing.get("arc_needed_degrees") is not None and rec.get("arc_options_degrees"):
        lo, hi = min(rec["arc_options_degrees"]), max(rec["arc_options_degrees"])
        arc = existing["arc_needed_degrees"]
        if not (lo <= arc <= hi):
            redesign = True
            reasons.append(f"needed arc {arc:g} deg is outside {new_model}'s published "
                           f"arc options {lo:g}-{hi:g} deg")

    if redesign:
        classification = "redesign_required"
    elif adjustments or verify:
        classification = "compatible_with_adjustments"
    else:
        classification = "direct_replacement"
        reasons.append(f"{new_model} matches the method and operates within its published "
                       "ranges at this position")
    if classification != "redesign_required" and not consequences:
        consequences.append("Re-check zone flow and matched precipitation after the swap; "
                            "adjust runtimes if the new device's flow differs")
    return ReplacementCheck(
        classification=classification,
        reasons=tuple(reasons),
        consequences=tuple(consequences),
        field_verification=tuple(verify))
