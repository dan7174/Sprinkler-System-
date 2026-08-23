# Sprinkler System AI Agent

A structured knowledge and implementation project for building a professional-grade sprinkler and landscape engineer/designer AI agent with Claude Code.

The first pilot location is Silverton, Oregon. The system is designed to remain reusable for other properties and jurisdictions.

## Current status

Phase 1 (knowledge foundation) is implemented: source manifest, Rain Bird resource-family index, JSON Schemas for intake/water tests/products/zones/projects, the first calculation functions (units, velocity, Hazen-Williams friction loss, elevation, critical pressure path, precipitation rate, matched precipitation) and their automated tests. See [docs/limitations.md](docs/limitations.md) for exactly what exists and what does not.

Product datasets, remaining calculations (pump, voltage drop, scheduling, drainage), the design engine, visual-plan generator and sample projects still need to be implemented and validated.

Do not use repository output as a stamped engineering plan, permit approval or substitute for required licensed professionals.

## How to use this repository with Claude Code

1. Open the repository in Claude Code.
2. Claude automatically reads [CLAUDE.md](CLAUDE.md).
3. Tell Claude which phase or project you want to work on.
4. For the initial build, use:

```text
Read CLAUDE.md and all required referenced documents. Begin Phase 1 from docs/09-implementation-roadmap.md. Do not stop after planning. Create the source manifest, schemas, first calculation functions and automated tests. Report verified work, assumptions and remaining blockers.
```

## Project documents

- [Agent Charter](docs/01-agent-charter.md)
- [Sources and Rain Bird](docs/02-sources-and-rain-bird.md)
- [Site Intake and Field Work](docs/03-site-intake-and-field-work.md)
- [Irrigation Engineering](docs/04-irrigation-engineering.md)
- [Landscape and Drainage](docs/05-landscape-and-drainage.md)
- [Audit, Maintenance and Estimating](docs/06-audit-maintenance-and-estimating.md)
- [Deliverables, Drawings and Safety](docs/07-deliverables-drawings-and-safety.md)
- [Software Architecture and Testing](docs/08-software-architecture-and-testing.md)
- [Implementation Roadmap](docs/09-implementation-roadmap.md)

## Key principles

- Verified measurements before final design
- Transparent hydraulic calculations
- Current and traceable manufacturer data
- Manufacturer-neutral recommendations
- Clear separation of facts, assumptions and field-verification items
- Simple explanations and useful visual plans
- Local code, backflow, utility and safety review
- Automated tests for calculations and data validation

## Development and testing

Requires Python 3.11+. Install test dependencies and run the suite from the repository root:

```bash
pip install pytest jsonschema
python -m pytest tests/ -v
```

The tests also run without pytest via `python -m unittest discover -s tests/unit -v`. Calculation modules live in `src/calculators/`, schema validation in `src/validation/`, schemas in `schemas/`.

## Source manifest

The initial manufacturer references are listed in [knowledge/source_manifest.yaml](knowledge/source_manifest.yaml). Add revision dates and verification notes as documents are reviewed.

## Repository owner

Dan, GitHub: [dan7174](https://github.com/dan7174)

