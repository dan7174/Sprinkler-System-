"""Intake review: decide whether a project has the critical inputs for
final design, per docs/03 (Required Project Intake) and the Agent
Charter (rules 1-3).

The reviewer never fills gaps. It returns exactly what is missing, why
it matters, and forces status 'preliminary_not_for_construction' until
the critical items are verified.
"""

from dataclasses import dataclass, field

from validation.schema_validation import validation_errors


@dataclass(frozen=True)
class MissingItem:
    item: str
    why_it_matters: str


@dataclass(frozen=True)
class IntakeReview:
    schema_errors: tuple
    missing_critical: tuple
    warnings: tuple
    ready_for_final_design: bool

    @property
    def required_status(self) -> str:
        return "design_in_progress" if self.ready_for_final_design \
            else "preliminary_not_for_construction"


def review_intake(intake: dict) -> IntakeReview:
    """Deterministic review of a site-intake record.

    Schema-invalid intakes are returned with the schema errors and are
    never ready for design. Schema-valid intakes are then checked for
    the critical design inputs.
    """
    errors = validation_errors("site_intake.schema.json", intake)
    if errors:
        return IntakeReview(tuple(errors), (), (), False)

    missing, warnings = [], []
    ws = intake.get("water_supply", {})

    dynamic = [t for t in ws.get("dynamic_tests", []) if t.get("test_type") == "dynamic"]
    if not dynamic:
        missing.append(MissingItem(
            "Dynamic pressure test at a measured flow",
            "Final hydraulics cannot be based on static pressure alone (Charter rule 3); "
            "static readings overstate what is available while water is flowing."))
    if not ws.get("static_pressure"):
        missing.append(MissingItem(
            "Static pressure reading",
            "Needed as the baseline and to sanity-check the dynamic test."))
    if not ws.get("meter_size") and ws.get("source_type") == "municipal":
        missing.append(MissingItem(
            "Water meter size",
            "The meter limits safe flow and adds pressure loss; both come from its size."))
    if not ws.get("safe_design_flow"):
        warnings.append(
            "Safe design flow not established; it must be derived from the dynamic "
            "test, meter limits and household demand before zones are sized.")
    if not ws.get("elevation_source_to_highest_outlet"):
        missing.append(MissingItem(
            "Elevation change from source to highest outlet",
            "Every foot of rise costs 0.433 psi; ignoring it overstates device pressure."))

    geo = intake.get("site_geometry", {})
    if geo.get("plan_source") in (None, "aerial_estimate_unverified"):
        missing.append(MissingItem(
            "Verified site dimensions (scaled plan or field measurements)",
            "Head spacing and coverage are wrong if the plan is not to scale."))
    if not geo.get("irrigated_area"):
        warnings.append("Irrigated area not recorded; zone counts and totals cannot be checked.")

    soil = intake.get("soil_and_plants", {})
    if not soil.get("soil_texture"):
        missing.append(MissingItem(
            "Soil texture",
            "Soil texture sets intake rate, cycle-and-soak need and schedule depth."))

    prop = intake.get("property", {})
    if prop.get("utility_locate_status") in (None, "not_requested"):
        warnings.append("Utility locate not requested; call 811 before any excavation.")
    if not prop.get("water_provider") and ws.get("source_type") == "municipal":
        warnings.append(
            "Water provider not identified; backflow and watering rules come from the provider.")

    declared = intake.get("missing_critical_inputs", [])
    for item in declared:
        missing.append(MissingItem(item, "Declared missing in the intake record."))

    return IntakeReview(
        schema_errors=(),
        missing_critical=tuple(missing),
        warnings=tuple(warnings),
        ready_for_final_design=not missing,
    )
