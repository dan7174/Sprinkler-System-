"""Assumption and risk tracking, per the Agent Charter (rules 2 and 8)
and docs/07 safety rules.

Every assumption records its impact and how to verify it. Risk triggers
map conditions to the licensed/authority review they require; the log
exports directly into the design_project schema fields.
"""

from dataclasses import dataclass, field

# Conditions that require licensed or authority review (Charter; docs/07).
REVIEW_TRIGGERS = {
    "backflow_device_selection_or_test": "State-certified backflow assembly tester / plumbing authority",
    "line_voltage_wiring": "Licensed electrician",
    "pump_electrical_supply": "Licensed electrician",
    "structural_or_retaining_wall": "Structural engineer",
    "public_right_of_way_work": "Local public works authority",
    "storm_drainage_connection": "Civil engineer / local authority",
    "reclaimed_or_non_potable_water": "Cross-connection control authority",
    "well_modification": "Licensed well contractor",
}


@dataclass(frozen=True)
class Assumption:
    description: str
    impact_if_wrong: str
    how_to_verify: str


class DesignLog:
    """Collects assumptions, field-verification items and review triggers
    for one project, and exports them in design_project schema shape."""

    def __init__(self):
        self._assumptions = []
        self._field_items = []
        self._reviews = {}

    def assume(self, description: str, impact_if_wrong: str, how_to_verify: str):
        for name, v in (("description", description),
                        ("impact_if_wrong", impact_if_wrong),
                        ("how_to_verify", how_to_verify)):
            if not v or not str(v).strip():
                raise ValueError(f"assumption {name} must not be empty - "
                                 "an unverifiable assumption is a guess")
        self._assumptions.append(Assumption(description, impact_if_wrong, how_to_verify))

    def require_field_verification(self, item: str):
        if item and item not in self._field_items:
            self._field_items.append(item)

    def trigger_review(self, condition: str):
        if condition not in REVIEW_TRIGGERS:
            raise ValueError(
                f"unknown review condition {condition!r}; known: {sorted(REVIEW_TRIGGERS)}")
        self._reviews[condition] = REVIEW_TRIGGERS[condition]

    @property
    def assumptions(self):
        return tuple(self._assumptions)

    @property
    def field_verification_items(self):
        return tuple(self._field_items)

    @property
    def required_professional_review(self):
        return tuple(f"{cond}: {who}" for cond, who in sorted(self._reviews.items()))

    def export(self) -> dict:
        """Fields shaped for design_project.schema.json."""
        return {
            "assumptions": [
                {"description": a.description,
                 "impact_if_wrong": a.impact_if_wrong,
                 "how_to_verify": a.how_to_verify}
                for a in self._assumptions],
            "field_verification_items": list(self._field_items),
            "required_professional_review": list(self.required_professional_review),
        }
