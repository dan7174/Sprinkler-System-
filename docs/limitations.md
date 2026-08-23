# Current Limitations and Source Freshness Rules

This file records what the repository can and cannot do right now, so no
output is trusted beyond what has actually been built and verified.

## What exists and is tested (as of 2026-08-23)

- JSON Schemas for site intake, water tests, products, zones and design
  projects (`schemas/`), with automated validation tests.
- Deterministic calculators (`src/calculators/`) with unit tests:
  - Unit conversions (pressure/head, flow, exact metric factors)
  - Pipe velocity and Hazen-Williams friction loss
  - Elevation pressure change
  - Critical pressure path with step-by-step breakdown
  - Precipitation rate (square, rectangular, triangular, area-based)
  - Part-circle normalization and matched-precipitation screening
  - Scheduling: ETc, net demand, readily available water, interval,
    gross depth, runtime, cycle-and-soak splitting
  - Pump: total dynamic head, pump-curve interpolation (no
    extrapolation), operating-point check, NPSH available and check
  - Electrical: two-wire voltage drop, solenoid-voltage check with
    required source citation, smallest-adequate-wire selection
  - Drainage screening: rational-method peak flow, grade, Manning
    full-flow pipe capacity
- Source manifest (`knowledge/source_manifest.yaml`) and Rain Bird
  resource-family index (`knowledge/rain_bird/resource_families.md`).
- Initial Rain Bird residential product records and published performance
  tables for R-VAN rotary nozzles, 1800 Series spray bodies, the 5004-PC
  rotor, and 100-DV/100-DVF valves (`data/manufacturers/rain_bird/`).

## What does NOT exist yet

- The product dataset is not a complete Rain Bird catalog and contains no
  other manufacturers. Product selection is limited to the listed,
  current records and their published operating conditions.
- No general fitting-loss, meter-loss, backflow-loss, filter-loss or
  regulator-loss tables. Valve-loss data currently covers only 100-DV
  and 100-DVF. The pressure-path calculator accepts other losses as
  caller-supplied values; the caller must cite their source.
- No water-hammer/surge analysis yet. No local agronomic data: ETo, Kc,
  soil AWHC, intake rates, rainfall intensities and runoff coefficients
  are required inputs from cited sources, not supplied by the library.
- The NEC wire-resistance table and typical Manning n values are
  reference values pending verification against the adopted code
  edition and actual product data (status noted in the manifest).
- No layout engine, hydrozoning engine, compatibility checker, report or
  drawing generator (Phases 3-4).
- No Oregon/Silverton code, backflow or water-provider data has been
  verified (see `verification_queue` in the source manifest).
- No integration-test sample projects yet; only unit tests and schema
  fixtures exist.

## Standing output rules

- Repository output is never a stamped engineering plan, permit approval
  or substitute for required licensed professionals.
- Any project whose intake lists `missing_critical_inputs` is
  preliminary and **Not for construction**.
- Final hydraulics require at least one dynamic pressure test at a
  measured flow; static pressure alone is insufficient.
- Velocity and pressure-margin limits are design policy: every check
  must record the limit used and its source (enforced by
  `check_velocity`, which refuses an unsourced limit).

## Source freshness rules

1. Every source used for a technical value must have a record in
   `knowledge/source_manifest.yaml` with authority level, status and
   `last_verified` date.
2. Product performance data must come from current manufacturer
   technical documents (authority level 3). Records must carry the
   source URL, revision date where published, and retrieval date
   (enforced by `schemas/product.schema.json`).
3. Design-manual content (authority level 6, status
   `historical_foundation`) may be used for methods and formulas only —
   never for product numbers, prices or availability.
4. Re-verify a source before relying on it when its `last_verified`
   date is older than 12 months, when the manufacturer publishes a new
   revision, or when a product's status is anything other than
   `current`. Codes and utility rules must be re-checked per project —
   jurisdiction data is never assumed portable between projects.
5. When sources conflict, record the conflict and use the most recent,
   authoritative, jurisdictionally applicable source. Never silently
   merge incompatible data.
6. Marketing and store pages (authority level 8) are for product
   discovery only, never for engineering values.
