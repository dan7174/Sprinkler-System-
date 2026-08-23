# Sprinkler System AI Agent

A structured knowledge and implementation project for building a professional-grade sprinkler and landscape engineer/designer AI agent with Claude Code.

The first pilot location is Silverton, Oregon. The system is designed to remain reusable for other properties and jurisdictions.

## Current status

This repository begins with the complete design requirements and implementation roadmap. The calculation engine, schemas, product datasets, visual-plan generator and sample projects still need to be implemented and validated.

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
- [Automation and Control](docs/10-automation-and-control.md)

## Key principles

- Verified measurements before final design
- Transparent hydraulic calculations
- Current and traceable manufacturer data
- Manufacturer-neutral recommendations
- Clear separation of facts, assumptions and field-verification items
- Simple explanations and useful visual plans
- Local code, backflow, utility and safety review
- Automated tests for calculations and data validation
- Deterministic controller logic with bounded weather adjustments and fail-safe shutdowns

## Source manifest

The initial manufacturer and external project references are listed in [knowledge/source_manifest.yaml](knowledge/source_manifest.yaml). Add revision dates and verification notes as documents are reviewed. Evaluations of useful external projects are stored under `knowledge/external-projects/`.

## Repository owner

Dan, GitHub: [dan7174](https://github.com/dan7174)
