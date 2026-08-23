"""Design report assembler, following the Agent Charter's required
response order (docs/01 s.26) and the deliverables list (docs/07 s.18).

The assembler formats what it is given: calculations arrive as computed
result objects (e.g. PressurePathResult), never as numbers invented
here. Sections with no verified content say so explicitly instead of
being silently dropped.
"""

from dataclasses import dataclass, field

from reports import bill_of_materials, commissioning, zone_schedule


@dataclass(frozen=True)
class ReportInputs:
    project_name: str
    location: str
    date: str                       # supplied by caller; never generated here
    status: str                     # e.g. "Preliminary — Not for construction"
    understanding: str
    missing_information: list       # strings; [] means none known
    assumptions: list               # dicts: description/impact_if_wrong/how_to_verify
    concept: str
    pressure_paths: list            # (zone_name, PressurePathResult)
    zone_rows: list                 # ZoneRow
    bom_lines: list                 # BomLine
    installation_sequence: list
    methods: set
    winterization_note: str
    risks_and_field_items: list
    sources: list                   # dicts: title/url/revision_or_verified_date


def render_markdown(r: ReportInputs) -> str:
    for name in ("project_name", "location", "date", "status",
                 "understanding", "concept"):
        if not getattr(r, name) or not str(getattr(r, name)).strip():
            raise ValueError(f"{name} is required")
    if not r.sources:
        raise ValueError("a report must cite its sources (Charter rule: cite the "
                         "source and revision behind important technical values)")

    out = [f"# {r.project_name}",
           f"**{r.location}** · {r.date} · **{r.status}**", ""]
    if "construction" not in r.status.lower() or "not for" in r.status.lower():
        out.append("> This document is not a stamped engineering plan and is not "
                   "approved for permits or construction.")
        out.append("")

    out += ["## 1. What we understand", r.understanding, ""]

    out.append("## 2. Missing critical information")
    if r.missing_information:
        out += [f"- {m}" for m in r.missing_information]
    else:
        out.append("- None known at this revision.")
    out.append("")

    out.append("## 3. Assumptions")
    if r.assumptions:
        for a in r.assumptions:
            out.append(f"- **{a['description']}** — if wrong: {a['impact_if_wrong']}; "
                       f"verify by: {a['how_to_verify']}")
    else:
        out.append("- No assumptions recorded; every input is verified or user-provided.")
    out.append("")

    out += ["## 4. Recommended concept", r.concept, ""]

    out.append("## 5. Hydraulic calculations (critical pressure path)")
    if r.pressure_paths:
        for zone_name, path in r.pressure_paths:
            out += [f"**{zone_name}**", "```", path.explain(), "```", ""]
    else:
        out += ["No pressure path calculated yet — a dynamic pressure test at a "
                "measured flow is required first.", ""]

    out.append("## 6. Zone schedule")
    out.append(zone_schedule.to_markdown(r.zone_rows) if r.zone_rows
               else "No zones defined yet.")
    out.append("")

    out.append("## 7. Visual plan")
    out.append("See the accompanying SVG plan sheet for this revision.")
    out.append("")

    out.append("## 8. Bill of materials")
    out.append(bill_of_materials.to_markdown(r.bom_lines) if r.bom_lines
               else "No materials selected yet.")
    out.append("")

    out.append("## 9. Installation sequence")
    if r.installation_sequence:
        out += [f"{i}. {s}" for i, s in enumerate(r.installation_sequence, 1)]
    else:
        out.append("To be issued with the construction revision.")
    out.append("")

    out.append("## 10. Commissioning and maintenance")
    out.append(commissioning.to_markdown(r.methods, r.winterization_note))

    out.append("## 11. Risks and field verification")
    if r.risks_and_field_items:
        out += [f"- {item}" for item in r.risks_and_field_items]
    else:
        out.append("- None recorded. Re-check before any construction release.")
    out.append("")

    out.append("## 12. Sources")
    for s in r.sources:
        rev = s.get("revision_or_verified_date", "")
        url = s.get("url", "")
        out.append(f"- {s['title']}" + (f" ({rev})" if rev else "") + (f" — {url}" if url else ""))
    out.append("")
    return "\n".join(out)
