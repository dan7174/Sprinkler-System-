# Implementation Roadmap

This file is part of the Sprinkler and Landscape Engineer/Designer AI Agent specification. Root instructions are in [CLAUDE.md](../CLAUDE.md).

## 28. Implementation Plan

Work in phases and keep the repository functional after every phase.

### Phase 0: Inspect and plan

- Inspect the repository and existing instructions.
- Identify the current technology stack and user-facing goal.
- List useful existing files and constraints.
- Create a concise implementation plan.
- Ask only questions that materially change the architecture or first deliverable.

### Phase 1: Knowledge foundation

- Create the source hierarchy and source manifest.
- Index the Rain Bird professional resource families.
- Define the product and project schemas.
- Document current limitations and source freshness rules.

### Phase 2: Calculation library

- Implement unit handling.
- Implement hydraulic, precipitation, scheduling, pump, voltage-drop and drainage calculations.
- Add formulas, citations, validation and tests.

### Phase 3: Design engine

- Implement intake validation.
- Implement hydrozoning and zone grouping.
- Implement compatibility checks.
- Implement product selection based on performance requirements.
- Implement assumption and risk tracking.

### Phase 4: Deliverables

- Build report, schedule, bill-of-materials and drawing templates.
- Generate visual plans and standard details.
- Add commissioning and maintenance outputs.

### Phase 5: Audit and retrofit

- Add troubleshooting decision trees.
- Add existing-product identification and lifecycle status.
- Add replacement compatibility checks.

### Phase 6: Pilot validation

- Build a Silverton, Oregon test project from verified information.
- Run all quality-control checks.
- Document anything that still requires field measurement or professional review.

## 29. Acceptance Criteria

The first usable release is complete only when it can:

- Reject an incomplete project instead of fabricating missing data.
- Calculate and explain a complete critical pressure path.
- Produce a valid zone schedule with flow, pressure and precipitation rate.
- Keep incompatible irrigation methods in separate zones.
- Generate a preliminary schedule based on plants, soil and climate.
- Create a traceable material list from current product data.
- Produce a readable plan with assumptions and verification notes.
- Diagnose common hydraulic, mechanical and electrical failures systematically.
- Identify when code, backflow, electrical, pump, drainage or licensed-professional review is required.
- Cite the source and revision behind important technical values.
- Pass the calculation and integration tests.

## 30. Begin Now

Start by inspecting the repository. Then report:

1. What already exists
2. What should be retained
3. The proposed architecture
4. The first implementation milestone
5. Any truly blocking questions

If nothing is blocking, begin Phase 1 immediately. Do not stop after writing a plan. Implement the source manifest, schemas, initial calculation library and tests, then report exactly what was created, what was verified and what remains.

## Related documents

- [Agent Charter](01-agent-charter.md)
- [Sources and Rain Bird](02-sources-and-rain-bird.md)
- [Site Intake and Field Work](03-site-intake-and-field-work.md)
- [Irrigation Engineering](04-irrigation-engineering.md)
- [Landscape and Drainage](05-landscape-and-drainage.md)
- [Audit, Maintenance and Estimating](06-audit-maintenance-and-estimating.md)
- [Deliverables, Drawings and Safety](07-deliverables-drawings-and-safety.md)
- [Software Architecture and Testing](08-software-architecture-and-testing.md)
- [Implementation Roadmap](09-implementation-roadmap.md)

