# Rain Bird Product Records

One JSON file per product, validating against
[schemas/product.schema.json](../../../schemas/product.schema.json).
Records are loaded and checked by `src/validation/product_data.py`.

## Status: Initial residential dataset

The first manufacturer-verified records cover:

- R-VAN14, R-VAN18 and R-VAN24 adjustable and full-circle nozzles
- 1804, 1806 and 1812 spray bodies, including PRS-30, PRS-45 and SAM-PRS models
- 5004-PC rotor and its standard Rain Curtain nozzle tree
- 100-DV and 100-DVF valves and their published pressure-loss table

Full published performance rows are under `performance/`. The source
PDFs are not stored in this repository. Spray-body CSVs are intentionally
absent because Rain Bird does not publish flow, radius or precipitation
performance for the body without a nozzle.

This is not a complete Rain Bird catalog. Product selection must remain
limited to models with a current, schema-valid record and the required
performance data for the proposed operating condition.

## Rules for every record

- Source URL and `retrieved_on` date are required (schema-enforced).
- Performance numbers only from current manufacturer technical
  documents — never marketing copy, never retailer listings.
- Record the document revision date when published.
- Records older than 12 months are flagged stale and excluded from
  product selection until re-verified (`docs/limitations.md`).
