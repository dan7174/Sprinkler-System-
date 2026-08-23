# Irrigation Engineering

This file is part of the Sprinkler and Landscape Engineer/Designer AI Agent specification. Root instructions are in [CLAUDE.md](../CLAUDE.md).

## 8. Complete Design Workflow

Use this order for every project:

1. Confirm scope, project mode and jurisdiction.
2. Validate site dimensions and scale.
3. Inventory existing and proposed landscape conditions.
4. Verify water source, flow, dynamic pressure and water quality.
5. Identify code, permit, backflow and water-use requirements.
6. Divide the property into hydrozones based on plant type, sun, soil, slope, exposure and irrigation method.
7. Select the appropriate application method for each hydrozone.
8. Lay out emitters or heads for coverage before dividing them into valve zones.
9. Calculate device flows, precipitation rates and zone demands.
10. Group compatible devices into zones.
11. Size lateral pipes, mainline, valves, filters, regulators, backflow assembly, pump equipment and wiring.
12. Calculate the critical pressure path for every zone.
13. Calculate plant water demand and create an initial schedule.
14. Coordinate irrigation with landscape, grading, drainage, utilities and hardscape.
15. Produce drawings, schedules, details, materials and installation notes.
16. Run quality-control checks.
17. Identify assumptions and field-verification items.
18. Produce commissioning and maintenance procedures.

Do not zone the system first and then force sprinkler placement to fit an arbitrary flow target. Establish correct coverage and application method first, then create hydraulically valid zones.

## 9. Hydraulic Calculation Engine

Build a transparent and unit-tested calculation library for:

- Static and dynamic pressure
- Pressure change from elevation
- Flow demand
- Safe available design flow and reserve
- Pipe velocity
- Pipe friction loss using an identified method or verified table
- Equivalent fitting lengths or published fitting losses
- Water-meter loss
- Backflow-assembly loss
- Master-valve and control-valve loss
- Filter and pressure-regulator loss
- Mainline and lateral loss
- Device operating pressure
- Critical hydraulic path
- Pump total dynamic head
- Pump operating point and pump-curve intersection
- Suction and NPSH concerns when applicable
- Water-hammer risk for large or high-velocity systems
- Electrical voltage drop and conductor sizing

For every zone, show:

`Source pressure -> meter/service loss -> backflow loss -> mainline loss -> master/control valve loss -> lateral loss -> elevation adjustment -> device pressure`

Do not merely report that a zone passes. Show inputs, formula or table source, intermediate values, design margin and pass/fail result.

Use conservative velocity and pressure-loss limits appropriate to the pipe material, system type, manufacturer data and accepted practice. Do not hardcode one universal velocity limit without documenting its source and application.

If a pump is needed, do not select it from horsepower alone. Verify the required flow and total dynamic head against the actual pump curve and expected source conditions.

## 10. Sprinkler and Rotor Layout Rules

- Place heads for complete coverage, beginning with corners and boundaries.
- Use head-to-head spacing unless a verified manufacturer method specifies otherwise.
- Use published performance at the actual proposed operating pressure.
- Account for wind, slope, obstructions and elevation.
- Use correct arcs and edge patterns to reduce overspray.
- Use strip, corner or specialty nozzles for narrow and irregular areas when appropriate.
- Maintain matched precipitation within a zone.
- Do not mix sprays, rotating nozzles, rotors, impact sprinklers and drip on one valve unless compatibility and scheduling are explicitly proven.
- Avoid watering buildings, pavement, vehicles, public sidewalks and neighboring property.
- Use check valves or appropriate devices where low-head drainage is likely.
- Provide safe spacing from walls, windows, utilities and equipment.
- Include maintenance access and expected plant growth.

Calculate precipitation rate for the actual layout pattern. For rectangular or square layouts, support:

`PR = 96.3 x total zone GPM / (row spacing x sprinkler spacing)`

Use the correct triangular-area factor for triangular spacing. Correctly account for part-circle heads and irregular areas. Include automated unit tests for square, rectangular, triangular and mixed-arc examples.

## 11. Drip and Low-Volume Design

Distinguish between:

- Individual point-source emitters
- Multi-outlet emitters
- Inline dripline
- Subsurface dripline
- Bubblers
- Microsprays
- Root-watering devices
- Sparse planting
- Dense planting
- Containers
- Temporary establishment irrigation

Calculate or document:

- Plant water requirement
- Base and non-base plant demand
- Emitter count and flow
- Emitter or dripline spacing
- Percentage of root zone wetted
- Application rate
- Maximum runtime
- Irrigation interval
- Maximum lateral length
- Pressure variation
- Filtration level
- Pressure regulation
- Flush velocity and flush-point placement
- Air/vacuum relief
- Check-valve needs on slopes
- Required inspection and maintenance access

Use a complete drip control-zone assembly when required: compatible valve, filtration, pressure regulation, gauges or test points, and flush provisions.

For trees, do not permanently concentrate all irrigation at the original root ball. Design for the expanding root zone and provide a method to modify or expand irrigation as the tree matures.

When converting a spray zone to drip, verify:

- Existing pressure and flow
- Valve minimum-flow behavior
- Filtration and regulation
- Unused-head closure or removal
- Flush points
- Separate scheduling requirements
- Compatibility with the controller and existing piping

## 12. Hydrozoning and Irrigation Scheduling

Separate zones based on:

- Turf, trees, shrubs, groundcover and containers
- Plant water needs
- Root depth
- Soil texture and intake rate
- Sun and shade
- Slope
- Wind exposure
- Irrigation device type
- Establishment versus mature landscape

Develop schedules using appropriate local information, including:

- Reference evapotranspiration
- Plant or crop coefficient
- Landscape coefficient when appropriate
- Effective rainfall
- Root-zone depth
- Soil water-holding capacity
- Allowable depletion
- Irrigation efficiency
- Precipitation or application rate
- Local watering restrictions

Provide seasonal adjustment guidance. Use cycle-and-soak where the application rate exceeds soil intake or where slope/runoff requires it. Explain that a calculated starting schedule must be adjusted from field observations.

## 13. Controllers, Sensors and Electrical Systems

Design or evaluate:

- Conventional multi-wire controllers
- Modular controllers
- Battery-operated controllers
- Wi-Fi and weather-based controllers
- Rain, freeze and soil-moisture sensors
- Flow sensors and water meters
- Master valves
- Pump-start relays
- Two-wire decoder systems
- Central-control systems when applicable

For flow monitoring, document:

- Sensor size and published flow range
- Required straight-pipe installation conditions
- K-factor and offset
- Normal zone-flow baseline
- High-flow, low-flow and no-flow thresholds
- Alarm, shutdown and master-valve response
- Low-flow bypass analysis where needed

For two-wire systems, include:

- Star, loop or combined topology
- Decoder-address schedule
- Wire-path length and resistance
- Approved waterproof splice details
- Grounding and surge protection
- Sensor and master-valve integration
- Simultaneous-zone flow management
- Commissioning and fault-isolation procedures

Battery controllers may be appropriate where AC power is unavailable, but disclose station-count, communication, battery-maintenance and sensor limitations.

## 14. Water Quality, Filtration and Alternative Sources

For well, pond, surface-water, reclaimed-water, rainwater or cistern systems, evaluate:

- Suspended solids and sediment
- Sand
- Biological material or algae
- Iron and mineral deposits
- Hardness
- pH
- Salinity or plant toxicity
- Filter type and mesh/disc rating
- Filter flow and pressure loss
- Flushing and maintenance interval
- Pump intake and screening
- Water treatment when necessary

For reclaimed or non-potable water:

- Apply local cross-connection and backflow rules.
- Use required purple identification, tags, valve boxes and signage.
- Prevent human-contact and overspray hazards.
- Check material compatibility with disinfectants and water chemistry.
- Identify restrictions for edible plants and public-use areas.
- Require authority approval where applicable.

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

