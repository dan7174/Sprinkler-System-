"""Troubleshooting decision trees, per docs/06 section 17.

Each tree is data: ordered steps in the system trace order, each with a
test, expected result, and branch interpretations with next actions.
Content follows standard irrigation troubleshooting practice as indexed
by the Rain Bird Troubleshooting hub (see knowledge/source_manifest.yaml);
it describes safe homeowner-level observation and 24 VAC metering only.
Anything at line voltage stops with a licensed-electrician escalation
(docs/07 s.27).

A step:
  id            unique within its tree
  test          what to do, in plain English
  expected      what a healthy system shows
  if_expected   (interpretation, next) when the expected result is seen
  if_not        (interpretation, next) when it is not
'next' is another step id, or one of the terminal actions:
  RESOLVED, ESCALATE_ELECTRICIAN, ESCALATE_BACKFLOW_TESTER,
  ESCALATE_PLUMBER, ESCALATE_IRRIGATION_CONTRACTOR, ESCALATE_UTILITY
"""

from dataclasses import dataclass

TERMINALS = {
    "RESOLVED": "Problem identified and correctable at this step.",
    "ESCALATE_ELECTRICIAN": "Stop: line-voltage work requires a licensed electrician.",
    "ESCALATE_BACKFLOW_TESTER": "Stop: backflow assemblies require a certified tester.",
    "ESCALATE_PLUMBER": "Stop: service-line or potable-plumbing work requires a licensed plumber.",
    "ESCALATE_IRRIGATION_CONTRACTOR": "Beyond safe DIY scope; use an irrigation contractor.",
    "ESCALATE_UTILITY": "Contact the water provider; the issue is upstream of the meter.",
}


@dataclass(frozen=True)
class Step:
    id: str
    test: str
    expected: str
    if_expected: tuple  # (interpretation, next)
    if_not: tuple       # (interpretation, next)


def _t(id, test, expected, ok, bad):
    return Step(id, test, expected, ok, bad)


TREES = {
    "low_pressure_all_zones": [
        _t("static", "Close all water use and read static pressure at a hose bib with a gauge.",
           "Static pressure near the historical/city-reported value.",
           ("Supply is normal at rest; the loss appears under flow.", "poc_valves"),
           ("Whole-property supply is low.", "provider")),
        _t("provider", "Ask neighbors or the water provider whether area pressure changed; "
           "check any pressure-reducing valve (PRV) setting on the house line.",
           "Provider reports normal pressure and no PRV is present or it is set correctly.",
           ("Low static with normal supply suggests a service-line restriction or failing PRV.",
            "ESCALATE_PLUMBER"),
           ("Area pressure is down or the PRV drifted.", "ESCALATE_UTILITY")),
        _t("poc_valves", "Confirm every shutoff between meter and manifold "
           "(house shutoff, POC ball valve, backflow shutoffs) is fully open.",
           "All isolation valves fully open.",
           ("Valves are open; test dynamic pressure next.", "dynamic"),
           ("A partially closed valve throttles the system.", "RESOLVED")),
        _t("dynamic", "Run the worst zone and read pressure at the gauge while flowing; "
           "compare with the design dynamic pressure.",
           "Dynamic pressure within a few psi of the design value.",
           ("Pressure is fine flowing; the symptom is zone-specific, not supply.", "zone_leak"),
           ("Large drop under flow: suspect an undersized or restricted line, "
            "a clogged backflow screen, or a mainline leak.", "backflow")),
        _t("backflow", "Inspect the backflow assembly: test cocks closed, no visible leak; "
           "screens/strainers (where the model has them) clean.",
           "Assembly clean, open and dry.",
           ("Assembly is not the restriction; look for a mainline leak.", "mainline"),
           ("A fouled or failing assembly restricts flow; service/testing is certified work.",
            "ESCALATE_BACKFLOW_TESTER")),
        _t("mainline", "With all zones off, watch the water meter's leak dial for movement; "
           "look for unusually green or soggy areas along the mainline route.",
           "No meter movement, no wet spots.",
           ("No leak found; remaining causes need pro measurement.",
            "ESCALATE_IRRIGATION_CONTRACTOR"),
           ("Constant flow with zones off indicates a mainline or valve leak.", "RESOLVED")),
        _t("zone_leak", "Inspect the low zone while running: look for gushing water, a sunken "
           "area, or several adjacent weak heads.",
           "A localized break or missing/broken head is visible.",
           ("Repair the break or head; retest pressure after.", "RESOLVED"),
           ("Too many heads or the wrong nozzles can overload a zone; count heads and "
            "compare zone flow with the design.", "ESCALATE_IRRIGATION_CONTRACTOR")),
    ],
    "zone_dead": [
        _t("controller", "Run the zone manually FROM THE CONTROLLER; listen at the valve.",
           "Controller shows the station running and the valve clicks/opens.",
           ("Electrical side works; the problem is water-side.", "manual_bleed"),
           ("No click: test the controller output next.", "output")),
        _t("output", "With a multimeter set to VAC, measure the controller terminal for this "
           "station while it runs (24 VAC circuit only; never open line-voltage wiring).",
           "Roughly 24-28 VAC on the station terminal.",
           ("Controller output good; the fault is in field wiring or the solenoid.", "solenoid"),
           ("No output: check the transformer/fuse; if house wiring is suspect, stop.",
            "ESCALATE_ELECTRICIAN")),
        _t("solenoid", "At the valve, measure solenoid resistance with the meter (ohms), "
           "wires disconnected.",
           "Typically about 20-60 ohms (check the manufacturer's published value).",
           ("Solenoid is plausible; suspect the field wire run or splices.", "wiring"),
           ("Open (infinite) or near-zero ohms: replace the solenoid.", "RESOLVED")),
        _t("wiring", "Check continuity of the station wire and common from controller to valve; "
           "inspect splices for corrosion (waterproof connectors required).",
           "Continuity good, splices clean.",
           ("Electrical path verified end-to-end; re-test at the controller. If it still "
            "fails, the valve internals need service.", "manual_bleed"),
           ("Repair the broken wire or corroded splice with waterproof connectors.", "RESOLVED")),
        _t("manual_bleed", "Open the valve manually (bleed screw or solenoid quarter-turn).",
           "Zone runs when manually opened.",
           ("Water side is fine: diaphragm ports or solenoid plunger are likely fouled; "
            "clean or rebuild the valve.", "RESOLVED"),
           ("No water even when opened manually: an upstream isolation valve is closed "
            "or the lateral is blocked/broken.", "RESOLVED")),
    ],
    "heads_not_rising": [
        _t("pressure", "Check whether the whole zone is weak or only some heads.",
           "Only some heads fail to rise; others pop up fully.",
           ("Localized: those heads are worn, jammed with debris, or below grade.", "head"),
           ("Whole zone weak: treat as a pressure/flow problem.", "low_pressure_all_zones")),
        _t("head", "Remove the affected head's internals; check for grit in the riser seal, "
           "a torn wiper seal, or a body sunk below grade.",
           "Debris or a worn seal found; body at grade.",
           ("Clean or replace internals; raise low bodies to grade.", "RESOLVED"),
           ("Head is clean but weak: check lateral for a leak between the last good "
            "head and this one.", "RESOLVED")),
    ],
    "misting_fogging": [
        _t("pressure", "Observe the zone: fine fog and drift instead of droplets means the "
           "nozzle pressure is above its published range.",
           "Visible fog/drift at the heads.",
           ("Pressure too high at the nozzle: install pressure-regulated bodies "
            "(e.g. 30/45 psi PRS) or regulate the zone.", "RESOLVED"),
           ("No fog: distribution problems have another cause (spacing, arcs, wind).",
            "RESOLVED")),
    ],
    "dry_spots": [
        _t("coverage", "Run the zone and watch the dry area: is it reached by adjacent heads' "
           "streams at all?",
           "Adjacent heads throw water to (head-to-head) or past the dry area.",
           ("Coverage geometry is fine; look at application uniformity.", "catchcan"),
           ("A gap in coverage: blocked stream, wrong arc/nozzle, plant growth in the "
            "way, or spacing beyond published radius.", "RESOLVED")),
        _t("catchcan", "Set out equal containers across the area and run the zone; compare "
           "collected depths.",
           "Depths within roughly 25% of each other.",
           ("Uniformity is fine; the dry spot is soil (compaction, repellency, slope "
            "runoff) or schedule depth. Aerate/wet, then adjust schedule.", "RESOLVED"),
           ("Poor uniformity: check nozzle sizes match the plan, heads are vertical, "
            "arcs correct, and pressure in range.", "RESOLVED")),
    ],
    "valve_weeps_when_off": [
        _t("meter", "With the controller off, check whether water seeps from the lowest head "
           "continuously or only briefly after a run.",
           "Brief seep after runs that stops on its own.",
           ("Low-head drainage: laterals drain through the lowest head after each run. "
            "Install check valves (e.g. SAM bodies) at low heads.", "RESOLVED"),
           ("Continuous seep: the valve is not sealing.", "valve")),
        _t("valve", "Shut the zone's isolation or master valve; open the suspect valve's bowl; "
           "inspect the diaphragm and seat for grit, tears or mineral buildup.",
           "Debris or a torn diaphragm found.",
           ("Clean the seat or replace the diaphragm kit for this model.", "RESOLVED"),
           ("Valve looks good but still weeps: replace the valve or get it serviced.",
            "ESCALATE_IRRIGATION_CONTRACTOR")),
    ],
    "drip_zone_failure": [
        _t("pressure", "Read pressure at the zone's test point or at the far flush point "
           "while running.",
           "Within the dripline/emitter published range (often 20-50 psi region; "
           "check the actual product spec).",
           ("Pressure is fine; look for clogging.", "filter"),
           ("Low: clogged filter or failed regulator; high: failed/missing regulator.",
            "filter")),
        _t("filter", "Close the water, open and inspect the drip zone filter.",
           "Filter clean or lightly fouled.",
           ("Filter is not the cause; flush the lateral ends.", "flush"),
           ("Clean the filter; if it fouls quickly, the water needs better filtration.",
            "RESOLVED")),
        _t("flush", "Open the flush points/end caps and run water until it flows clear.",
           "Water runs clear quickly and emitters recover.",
           ("Line sediment was the issue; add regular flushing to maintenance.", "RESOLVED"),
           ("Persistent debris or slime: check emitter outputs plant-by-plant and "
            "consider water treatment; verify the regulator and filter match the "
            "product's published requirements.", "RESOLVED")),
    ],
    "runoff_or_overspray": [
        _t("overspray", "Watch the zone: is water landing on pavement/buildings, or is it "
           "landing correctly but then flowing off?",
           "Water lands in the planted area but runs off before the cycle ends.",
           ("Application rate exceeds soil intake: use cycle-and-soak (split the "
            "runtime) and re-check the schedule.", "RESOLVED"),
           ("Overspray: fix arcs, radius adjustment, or nozzle selection; use strip "
            "or corner nozzles for narrow areas.", "RESOLVED")),
    ],
}


def list_symptoms():
    return sorted(TREES)


def get_tree(symptom: str):
    if symptom not in TREES:
        raise ValueError(f"unknown symptom {symptom!r}; known: {list_symptoms()}")
    return TREES[symptom]


def validate_tree(symptom: str):
    """Integrity check: every 'next' resolves to a step in this tree, a
    terminal action, or another tree's name; the first step is reachable
    root; no step references itself."""
    steps = get_tree(symptom)
    ids = {s.id for s in steps}
    if len(ids) != len(steps):
        raise ValueError(f"{symptom}: duplicate step ids")
    for s in steps:
        for _, nxt in (s.if_expected, s.if_not):
            if nxt == s.id:
                raise ValueError(f"{symptom}/{s.id}: step points to itself")
            if nxt not in ids and nxt not in TERMINALS and nxt not in TREES:
                raise ValueError(f"{symptom}/{s.id}: unknown next {nxt!r}")
    return True


def to_markdown(symptom: str) -> str:
    """Render one tree as a numbered test/expected/interpretation guide."""
    steps = get_tree(symptom)
    out = [f"### Troubleshooting: {symptom.replace('_', ' ')}", ""]
    for i, s in enumerate(steps, 1):
        out.append(f"**{i}. {s.test}**")
        out.append(f"   - Expected: {s.expected}")
        for label, (interp, nxt) in (("If as expected", s.if_expected),
                                     ("If not", s.if_not)):
            if nxt in TERMINALS:
                dest = TERMINALS[nxt]
            elif nxt in TREES:
                dest = f"continue with the '{nxt.replace('_',' ')}' checklist"
            else:
                idx = next(j for j, st in enumerate(steps, 1) if st.id == nxt)
                dest = f"go to step {idx}"
            out.append(f"   - {label}: {interp} → {dest}")
        out.append("")
    return "\n".join(out)
