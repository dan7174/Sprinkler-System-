# Sources and Rain Bird

This file is part of the Sprinkler and Landscape Engineer/Designer AI Agent specification. Root instructions are in [CLAUDE.md](../CLAUDE.md).

## 3. Source Hierarchy

Use sources in this order:

1. Applicable laws, adopted codes, permits, water-purveyor rules and authority requirements.
2. Verified field measurements, survey information and as-built information.
3. Current manufacturer technical specifications, performance charts, pressure-loss charts and installation manuals.
4. Recognized professional standards and technical references, including Irrigation Association methods where applicable.
5. University Extension, USDA/NRCS, regional climate, horticulture and arboriculture sources.
6. Manufacturer design manuals and professional design guides.
7. Educational articles and troubleshooting guides.
8. Store descriptions and marketing pages only for product discovery.

When sources conflict, document the conflict and use the most recent, authoritative and jurisdictionally applicable source. Do not silently merge incompatible information.

Maintain `knowledge/source_manifest.yaml` with these fields:

- Title
- URL or document identifier
- Publisher/manufacturer
- Document type
- Product family or subject
- Publication/revision date
- Retrieval date
- Geographic or jurisdictional scope
- Current, historical or superseded status
- Authority level
- Calculations or recommendations that depend on the source
- Notes and known limitations

Do not bulk-copy copyrighted manuals into the repository unless their license clearly allows it. Store structured facts, short summaries, formulas, metadata and links to the original documents. Preserve attribution.

## 4. Required Rain Bird Curriculum

Use the following Rain Bird resources as a manufacturer-specific curriculum and data source:

- Learn Center: https://store.rainbird.com/learn
- Knowledge Center: https://store.rainbird.com/learn/knowledge-center
- Residential Design Service: https://store.rainbird.com/design-service
- Professional Design Service: https://store.rainbird.com/design-service-for-professionals
- Professional Specifier Resources: https://www.rainbird.com/landscape/specifier-home-page-new
- Professional Document Library: https://www.rainbird.com/documents/professionals
- Landscape Irrigation Design Manual: https://www.rainbird.com/media/4214
- Low-Volume Landscape Irrigation Design Manual: https://www.rainbird.com/media/5044
- Non-Potable Water Irrigation Design Guide: https://www.rainbird.com/media/8608
- Friction-Loss Charts: https://www.rainbird.com/landscape/friction-loss-charts
- CAD Installation Drawings: https://www.rainbird.com/professionals/specifier-documents
- Landscape Calculators: https://www.rainbird.com/landscape/calculators
- Product Upgrade Guide: https://store.rainbird.com/upgrade-guide
- Troubleshooting: https://store.rainbird.com/repair/troubleshooting
- Product Information and Support: https://store.rainbird.com/repair/product-information-support
- Repair FAQ: https://store.rainbird.com/repair/faq
- Professional Training Topics: https://rainbirdservices.com/
- Residential Rebates: https://www.rainbird.com/residential-rebates
- Commercial Rebates: https://www.rainbird.com/commercial-rebates

The Rain Bird design manuals contain valuable fundamentals but may contain historical product information. Use them for established design methods, then verify all products, performance data, regulations and compatibility against current documents.

Create a structured Rain Bird product dataset only from current, traceable sources. Include:

- Manufacturer and product family
- Model and SKU
- Current, discontinued or replacement status
- Application type
- Inlet and outlet sizes
- Recommended and allowable pressure range
- Flow range
- Radius or throw
- Arc options
- Precipitation rate where published
- Filtration and regulation requirements
- Check-valve or pressure-regulation options
- Controller, decoder and sensor compatibility
- Published pressure losses
- Installation constraints
- Source URL and revision date

Never assume Rain Bird products are automatically the best choice. Permit equivalent products when performance and compatibility are verified.

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

