# Rain Bird Product Records

One JSON file per product, validating against
[schemas/product.schema.json](../../../schemas/product.schema.json).
Records are loaded and checked by `src/validation/product_data.py`.

## Status: EMPTY — data retrieval blocked

No product records exist yet. The Claude Code remote environment's
network egress policy currently blocks `rainbird.com` and
`store.rainbird.com`, so current manufacturer performance data cannot be
retrieved from inside a session. Per the Agent Charter, performance data
is never invented and never taken from retailer/marketing pages.

To unblock, either:

1. Allow `www.rainbird.com` and `store.rainbird.com` in the Claude Code
   environment's network policy (claude.ai/code environment settings), or
2. Download the technical spec PDFs (e.g. R-VAN, 1800 Series, 5000
   Series, DV Series tech specs from the Professional Document Library)
   and commit them under `knowledge/rain_bird/` or attach them to a
   session, and Claude will extract structured records from them.

## Rules for every record

- Source URL and `retrieved_on` date are required (schema-enforced).
- Performance numbers only from current manufacturer technical
  documents — never marketing copy, never retailer listings.
- Record the document revision date when published.
- Records older than 12 months are flagged stale and excluded from
  product selection until re-verified (`docs/limitations.md`).
