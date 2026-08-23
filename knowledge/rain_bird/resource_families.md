# Rain Bird Professional Resource Families

Index of the Rain Bird resource families required by
[docs/02-sources-and-rain-bird.md](../../docs/02-sources-and-rain-bird.md),
grouped by what each family is trusted for. Full source records, authority
levels and verification dates live in
[knowledge/source_manifest.yaml](../source_manifest.yaml).

Rain Bird is a major reference, not the whole industry. Equivalent
products from other manufacturers are allowed when performance and
compatibility are verified (Agent Charter rule 10).

## 1. Design methodology (fundamentals)

Established design methods. Product tables inside these manuals may be
historical; verify every product against current documents before use.

| Resource | URL | Use for |
| --- | --- | --- |
| Landscape Irrigation Design Manual | https://www.rainbird.com/media/4214 | Hydraulics, site data, head layout, zoning, piping, wiring, final plans |
| Low-Volume Landscape Irrigation Design Manual | https://www.rainbird.com/media/5044 | Drip design, plant water requirements, wetted area, lateral lengths |
| Non-Potable Water Irrigation Design Guide | https://www.rainbird.com/media/8608 | Reclaimed-water components and identification (local rules control) |

## 2. Current technical data (engineering values)

The only Rain Bird family trusted for current performance numbers,
pressure losses and specifications.

| Resource | URL | Use for |
| --- | --- | --- |
| Professional Specifier Resources | https://www.rainbird.com/landscape/specifier-home-page-new | Design guides, performance charts, calculators |
| Professional Document Library | https://www.rainbird.com/documents/professionals | Current manuals, charts, specifications, replacement data |
| Friction-Loss Charts | https://www.rainbird.com/landscape/friction-loss-charts | Meter and pipe friction-loss references |
| CAD Installation Drawings | https://www.rainbird.com/professionals/specifier-documents | Product-specific installation details |
| Landscape Calculators | https://www.rainbird.com/landscape/calculators | Cross-checking calculation results |

## 3. Education and homeowner guidance

Background education; never a substitute for technical specifications.

| Resource | URL | Use for |
| --- | --- | --- |
| Learn Center | https://store.rainbird.com/learn | Residential product education |
| Knowledge Center | https://store.rainbird.com/learn/knowledge-center | Articles, videos, product guidance |
| Professional Training Topics | https://rainbirdservices.com/ | Competency curriculum topics (docs/08, section 25) |

## 4. Troubleshooting and lifecycle

| Resource | URL | Use for |
| --- | --- | --- |
| Troubleshooting | https://store.rainbird.com/repair/troubleshooting | Residential system troubleshooting |
| Product Information and Support | https://store.rainbird.com/repair/product-information-support | Product support lookups |
| Repair FAQ | https://store.rainbird.com/repair/faq | Common repair questions |
| Product Upgrade Guide | https://store.rainbird.com/upgrade-guide | Discontinued-product and replacement discovery |

## 5. Design services and rebates (context only)

| Resource | URL | Use for |
| --- | --- | --- |
| Residential Design Service | https://store.rainbird.com/design-service | Awareness of manufacturer design offerings |
| Professional Design Service | https://store.rainbird.com/design-service-for-professionals | Same, professional tier |
| Residential Rebates | https://www.rainbird.com/residential-rebates | Rebate discovery (verify terms with the program) |
| Commercial Rebates | https://www.rainbird.com/commercial-rebates | Same, commercial |

## Product dataset rules

Structured product records go in `data/manufacturers/rain_bird/` and must
validate against [schemas/product.schema.json](../../schemas/product.schema.json):
every record needs a source URL and retrieval date, and performance data
must come from family 2 (current technical data) — never from marketing
pages or the historical design manuals.
