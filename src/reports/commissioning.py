"""Commissioning checklist and seasonal maintenance plan, per docs/06
section 20.

The checklists adapt to the application methods actually present in
the design. Winterization guidance requires an explicit climate note
from the caller — freeze practice is climate-specific and never assumed
(docs/06: no compressed-air blowout advice without climate justification
and equipment limits).
"""

BASE_COMMISSIONING = [
    "Pressure-test and inspect the mainline for leaks before backfilling",
    "Flush the mainline, then each lateral, before installing nozzles or emitters",
    "Identify and label every valve and controller station",
    "Program the controller from the zone schedule and record the program",
    "Test rain/freeze or soil-moisture sensors if installed",
    "Verify each zone's operating pressure and compare with the design values",
    "Document the as-built layout: valves, wire routing, sleeves and pipe runs",
]
SPRINKLER_COMMISSIONING = [
    "Level heads, set arcs and confirm nozzles match the plan on every zone",
    "Check for overspray onto buildings, pavement or neighboring property and correct",
    "Run a catch-can distribution check on representative zones and record results",
]
DRIP_COMMISSIONING = [
    "Verify drip-zone filter, pressure regulator and check operating pressure at the far end",
    "Open flush points and flush dripline until water runs clear",
    "Inspect emitter output at representative plants",
]

BASE_MAINTENANCE = [
    ("Spring startup", "Inspect for winter damage, restore water slowly, re-test each zone, "
                       "reset the controller schedule from current weather"),
    ("Monthly in season", "Walk each zone: look for leaks, dry or soggy spots, misting, "
                          "blocked or misaligned heads; adjust the schedule seasonally"),
    ("Mid-season", "Clean filters; verify sensor operation; review runtimes against plant response"),
    ("Establishment changes", "Reduce establishment watering as new plants root in; "
                              "expand tree irrigation outward as canopies grow"),
]


def commissioning_checklist(methods: set) -> list:
    """Ordered commissioning steps for the methods present in the design."""
    if not methods:
        raise ValueError("at least one application method is required")
    steps = list(BASE_COMMISSIONING)
    if methods & {"spray", "rotary_nozzle", "rotor", "impact"}:
        steps[2:2] = SPRINKLER_COMMISSIONING
    if methods & {"drip", "tree_watering", "microspray", "bubbler"}:
        steps[2:2] = DRIP_COMMISSIONING
    return steps


def maintenance_plan(methods: set, winterization_note: str) -> list:
    """Seasonal maintenance rows (season/task pairs).

    ``winterization_note`` must state the climate-based requirement for
    this project (e.g. from the local jurisdiction/climate source);
    an empty note is refused rather than guessed.
    """
    if not winterization_note or not winterization_note.strip():
        raise ValueError(
            "winterization_note is required: freeze protection practice is "
            "climate-specific and must come from a cited local source")
    rows = list(BASE_MAINTENANCE)
    if methods & {"drip", "tree_watering", "microspray", "bubbler"}:
        rows.append(("Drip care", "Flush dripline seasonally; clean drip filters; "
                                  "inspect emitters and flush points"))
    rows.append(("Winterization", winterization_note))
    return rows


def to_markdown(methods: set, winterization_note: str) -> str:
    steps = commissioning_checklist(methods)
    plan = maintenance_plan(methods, winterization_note)
    out = ["### Commissioning checklist", ""]
    out += [f"{i}. {s}" for i, s in enumerate(steps, 1)]
    out += ["", "### Seasonal maintenance", ""]
    out += [f"- **{season}** — {task}" for season, task in plan]
    return "\n".join(out) + "\n"
