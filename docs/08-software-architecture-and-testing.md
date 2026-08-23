# Software Architecture and Testing

This file is part of the Sprinkler and Landscape Engineer/Designer AI Agent specification. Root instructions are in [CLAUDE.md](../CLAUDE.md).

## 23. Repository Architecture

If the repository is empty, create a clean structure similar to:

```text
CLAUDE.md
README.md
docs/
  architecture.md
  design-methodology.md
  limitations.md
knowledge/
  source_manifest.yaml
  design_checks.md
  rain_bird/
  regulations/
  horticulture/
data/
  manufacturers/
    rain_bird/
schemas/
  site_intake.schema.json
  water_test.schema.json
  product.schema.json
  zone.schema.json
  design_project.schema.json
src/
  agent/
  calculators/
  layout/
  reports/
  validation/
templates/
  intake/
  reports/
  schedules/
  drawings/
tests/
  unit/
  integration/
  fixtures/
examples/
  silverton_or/
```

Adjust the structure to the existing technology stack. Do not introduce a large framework without a clear benefit.

Use explicit units in all schemas. Prefer storing a value and unit together rather than relying on an undocumented global unit system. Support U.S. customary units by default and metric conversion where practical.

## 24. Software and Data Quality

- Validate all external data before use.
- Record source and revision with product data.
- Reject impossible or incomplete calculation inputs.
- Use deterministic calculation functions.
- Separate engineering calculations from language-model judgment.
- Add unit tests for formulas and conversions.
- Add boundary tests for minimum and maximum operating conditions.
- Add integration tests for complete sample projects.
- Cross-check selected results by an independent hand calculation or second method.
- Include warnings when a result is outside published performance ranges.
- Do not allow a product-selection module to override hydraulic requirements.
- Do not calculate from rounded display values when more precise internal values are available.
- Make every generated report traceable back to project inputs and source versions.

Create at least these test fixtures:

1. Small municipal-water residential lawn
2. Irregular lawn with sprays and rotary nozzles
3. Shrub and tree drip system
4. Sloped site requiring cycle-and-soak and check valves
5. Well-and-pump system
6. Low-pressure failure case
7. Excessive-velocity failure case
8. Retrofit with discontinued components
9. Reclaimed-water warning case
10. Silverton, Oregon pilot project

## 25. Professional Competency Matrix

Build a checklist and test scenarios covering:

- Site surveying
- Irrigation design
- Hydraulics
- Efficient scheduling
- Irrigation auditing
- Residential installation
- Controller programming
- Valve troubleshooting
- Electrical troubleshooting
- Drip irrigation
- Drainage
- Flow management
- Pump systems
- Two-wire systems
- Seasonal commissioning and maintenance
- Landscape and planting coordination

Rain Bird professional training topics may help define the curriculum, but completing internal tests does not make the AI or user professionally certified.

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

