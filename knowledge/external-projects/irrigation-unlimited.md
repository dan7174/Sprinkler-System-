# External Project Review: Irrigation Unlimited

## Source

- Repository: https://github.com/rgc99/irrigation_unlimited
- Author: Robert Cook, GitHub `rgc99`
- Reviewed branch: `master`
- Reviewed integration version: `2025.12.0`
- Review date: 2026-08-22
- License: MIT

This review records architectural ideas that may improve the Sprinkler System AI Agent. It does not treat the project as an irrigation engineering authority.

## What the project does

Irrigation Unlimited is a Home Assistant integration that schedules and operates irrigation controllers, zones and valve switches. It supports multiple controllers, schedules, sequences, manual operations, runtime adjustments, history, physical-switch feedback and measured water volume.

It is an operations and automation reference. It does not design sprinkler layouts, size pipes, calculate pressure loss, select nozzles or create planting plans.

## Patterns to adopt

### Controller hierarchy

Use a clear hierarchy:

```text
System
  Controller
    Master valve or pump control
    Zones
      Schedules
    Sequences
      Ordered zone steps
```

Keep physical zones separate from references to those zones in a sequence. A sequence may use a zone more than once for cycle-and-soak.

### Flexible schedule grammar

Support:

- Fixed start time
- Required finish time
- Sunrise or sunset offset
- Weekday filters
- Day-of-month filters
- Odd or even days
- Month filters
- Every-N-days intervals
- Valid date ranges
- Local watering restrictions

### Sequence engine

Support ordered zones, individual durations, inter-zone delays, repeats, disabled steps and proportional runtime changes. Use this for cycle-and-soak and water-supply limits.

### Runtime adjustment

Allow an approved base runtime to be adjusted by actual duration, percentage, increase or decrease. Always apply configured minimum and maximum values. Adjust the original approved runtime rather than compounding one adjustment on another.

### Operational commands

Model enable, disable, pause, resume, suspend, cancel, manual run and temporary schedule changes as separate commands with clear rules.

### Feedback and resynchronization

Compare requested actuator state with reported device state after a reasonable delay. Record discrepancies and retry only within a bounded policy. Escalate persistent mismatches as faults.

### Water-volume monitoring

Use a cumulative water meter to calculate run volume and average flow. Compare actual readings with a learned or engineered range for each zone.

### Events and history

Emit structured events for starts, finishes, valve transitions, synchronization errors and abnormal water volume. Retain enough history to compare scheduled, commanded and actual performance.

### Virtual-time testing

Use a virtual clock to test long schedules, seasonal transitions, sunrise and sunset behavior, overlapping events and controller restarts without waiting in real time.

## Patterns to adapt carefully

### Weather adjustment

The example weighted-rain and temperature thresholds are personal rules, not validated irrigation science. Our system may use the workflow but must calculate adjustments from accepted ET, rainfall, soil and plant methods with bounded outputs.

### Soil-moisture adjustment

A simple moisture threshold is not enough. Sensor type, depth, placement, calibration, soil texture, root zone and failure behavior must be documented.

### Negative delays and anti-hammer timing

Overlapping valves or changing master-valve timing may reduce pressure transients, but the result depends on pumps, check valves, pipe velocity and total flow. Do not use negative delays without hydraulic verification and equipment-specific safeguards.

### Device state

A switch reporting `on` does not prove water is flowing. Track commanded state, device-reported state and flow-confirmed state separately.

### Home Assistant limitations

Home Assistant may be an optional interface, scheduler or reporting layer. It is not a safety-rated control system. Critical pump, pressure, backflow and shutoff protections must not depend only on Home Assistant, Wi-Fi or cloud access.

## Patterns not to adopt

- Australian seasonal month examples for Oregon projects
- Unbounded weather-based runtime changes
- Blind retries of a valve or pump command
- Assuming switch feedback confirms irrigation delivery
- Treating the project as a source for hydraulics, electrical code or landscape design
- Copying the large monolithic controller module into this project

## License and attribution

The repository uses the MIT License. If source code or substantial portions are copied or modified, retain its copyright and license notice. Concepts may be independently implemented, but source inspiration should remain documented here.

## Key source paths

- `README.md`: behavior, configuration and examples
- `custom_components/irrigation_unlimited/irrigation_unlimited.py`: scheduling and control model
- `custom_components/irrigation_unlimited/schema.py`: configuration validation
- `custom_components/irrigation_unlimited/history.py`: run history and totals
- `custom_components/irrigation_unlimited/entity.py`: state restoration
- `tests/README.md`: virtual-time testing method
- `tests/configs/timing_anti_hammering.yaml`: valve-transition timing examples
- `tests/configs/test_volume_fault.yaml`: volume and flow test configuration
- `packages/irrigation_unlimited_adjustment.yaml`: example weather adjustment

## Recommended use in this project

Use the project as a reference when implementing:

- `src/control/scheduler/`
- `src/control/state_machine/`
- `src/control/flow_monitor/`
- `src/control/faults/`
- `src/control/history/`
- `integrations/home_assistant/`
- `tests/control/virtual_clock/`

Keep control execution separate from the design agent. The agent may prepare a program, explain it and validate it, but approved deterministic code must operate physical equipment.
