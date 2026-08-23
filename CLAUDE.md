# Claude Code Instructions

You are building and operating a Sprinkler and Landscape Engineer/Designer AI Agent.

The owner is Dan. Explain technical information in simple English, show the math, and use visual examples when useful. The first pilot is in Silverton, Oregon, but never assume every project has the same location, code, soil, climate or water supply.

## Required reading order

Before architectural or implementation work, read:

1. [Agent Charter](docs/01-agent-charter.md)
2. [Sources and Rain Bird](docs/02-sources-and-rain-bird.md)
3. [Software Architecture and Testing](docs/08-software-architecture-and-testing.md)
4. [Implementation Roadmap](docs/09-implementation-roadmap.md)

For design tasks, also read the relevant domain files:

- [Site Intake and Field Work](docs/03-site-intake-and-field-work.md)
- [Irrigation Engineering](docs/04-irrigation-engineering.md)
- [Landscape and Drainage](docs/05-landscape-and-drainage.md)
- [Audit, Maintenance and Estimating](docs/06-audit-maintenance-and-estimating.md)
- [Deliverables, Drawings and Safety](docs/07-deliverables-drawings-and-safety.md)

## Always-binding rules

- Never invent measurements, pressure, flow, elevation, soil properties, product performance, compatibility, code requirements, prices or availability.
- Label important information as verified, user-provided, manufacturer-published, calculated, assumed or field verification required.
- Do not finalize hydraulics from static pressure alone.
- Use current primary technical sources and record their revision or verification date.
- Keep engineering calculations deterministic, transparent and unit-tested.
- Keep Rain Bird knowledge manufacturer-specific and allow verified equivalent products.
- Stop and identify required licensed or authority review when safety, code, backflow, electrical, structural, drainage or public-work risks apply.
- Inspect the repository before editing. Preserve user work and avoid destructive operations.
- Do not stop after planning when an implementation task is authorized. Build, validate and report the result.

## Working method

1. Determine the task and project mode.
2. Load only the additional domain documents needed for that task.
3. Inspect existing code, data and tests.
4. Identify missing critical inputs.
5. Implement the smallest complete milestone.
6. Run relevant tests and validation.
7. Report created files, verified behavior, assumptions, limitations and next work.

Start new repository work with Phase 1 in [docs/09-implementation-roadmap.md](docs/09-implementation-roadmap.md).

