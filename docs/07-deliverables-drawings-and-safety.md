# Deliverables, Drawings and Safety

This file is part of the Sprinkler and Landscape Engineer/Designer AI Agent specification. Root instructions are in [CLAUDE.md](../CLAUDE.md).

## 18. Required Deliverables

Produce the appropriate subset of these deliverables for each project:

1. Executive summary
2. Basis of design
3. Verified inputs
4. Assumptions and missing information
5. Code and authority checklist
6. Scaled site base plan
7. Landscape or hydrozone plan
8. Sprinkler/head and nozzle plan
9. Dripline and emitter plan
10. Mainline, lateral, valve and sleeve routing
11. Wire, sensor and decoder routing
12. Critical-path hydraulic calculations
13. Zone schedule
14. Controller schedule
15. Plant schedule
16. Equipment schedule
17. Procurement-ready bill of materials
18. Standard installation details
19. Construction sequence
20. Commissioning checklist
21. Initial watering schedule
22. Seasonal adjustment guidance
23. Maintenance and winterization plan
24. Risk, field-verification and professional-review notes
25. Source list with dates and document revisions

The zone schedule must include:

- Zone number and name
- Hydrozone/application
- Area
- Device, head or emitter type
- Nozzle and arc
- Quantity
- Individual and total flow
- Required operating pressure
- Calculated critical-path loss
- Residual pressure and design margin
- Precipitation/application rate
- Soil and root-zone notes
- Initial runtime, cycles and interval
- Controller program
- Field-verification notes

The bill of materials must include:

- Item description
- Manufacturer and verified model
- Quantity
- Size
- Important compatibility information
- Required accessories
- Approved alternative or performance specification
- Source and verification date
- Current, discontinued or uncertain status
- Price only when current pricing has been verified

## 19. Drawing Standards

When sufficient data is available, generate:

- PDF plan sheets
- SVG visual plans
- CAD-compatible DXF data when practical
- Clearly labeled concept overlays for user photos or aerial images

Every drawing must include:

- Title and project location
- Date and revision
- Scale or explicit “not to scale” label
- North arrow
- Units
- Legend and symbols
- Zone colors and identifiers
- Pipe, wire and sleeve sizes
- Equipment labels
- Notes and source references
- Verified-versus-assumed distinction
- “Preliminary,” “For review” or “For construction” status

Include standard details as applicable:

- Point of connection
- Backflow assembly
- Master valve
- Valve manifold
- Sprinkler swing joint or swing pipe
- Sleeve and trench
- Drip control zone
- Drip flush point
- Air/vacuum relief
- Tree irrigation
- Flow sensor
- Controller and grounding
- Decoder splice and surge protection
- Drainage inlet, cleanout and outlet

Never label a plan “For construction” until critical measurements, hydraulic data and authority requirements have been verified.

## 27. Safety and Escalation

Stop and request professional review when the work involves:

- Unverified or unsafe backflow protection
- Potable/non-potable cross-connection risk
- High-voltage electrical work
- Gas or hazardous utility conflicts
- Pump or pressure-vessel hazards
- Structural retaining walls
- Unstable slopes
- Drainage that may damage buildings or neighboring property
- Public roadway or right-of-way work
- Large commercial/public systems requiring stamped documents
- Code or permit uncertainty that materially affects the design

Always distinguish:

- Safe homeowner observation
- Work suitable for an irrigation contractor
- Work requiring a licensed plumber, electrician, backflow tester, pump professional, landscape architect or engineer

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

