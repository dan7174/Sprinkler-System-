"""Load and validate the manufacturer product catalog.

Product records live under data/manufacturers/<manufacturer>/ as JSON
files, one product per file, validating against
schemas/product.schema.json. This module refuses invalid records and
flags stale ones so no design ever selects a product from unverified or
outdated data (docs/02 and docs/limitations.md freshness rules).
"""

import datetime
import json
from dataclasses import dataclass
from pathlib import Path

from .schema_validation import validation_errors

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "manufacturers"

# Freshness rule 4 in docs/limitations.md: re-verify sources older than 12 months.
MAX_SOURCE_AGE_DAYS = 365


@dataclass(frozen=True)
class CatalogIssue:
    file: str
    problem: str


def load_catalog(data_dir: Path = DATA_DIR):
    """Load every product record under data_dir.

    Returns (records, issues). A record with schema violations is NOT
    included in ``records``; it appears in ``issues`` instead. An empty
    data directory returns ([], []) — an empty catalog is a valid state
    (it simply means product selection is not yet possible).
    """
    records, issues = [], []
    if not data_dir.is_dir():
        return records, issues
    for path in sorted(data_dir.rglob("*.json")):
        rel = str(path.relative_to(data_dir))
        try:
            record = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            issues.append(CatalogIssue(rel, f"invalid JSON: {exc}"))
            continue
        errors = validation_errors("product.schema.json", record)
        if errors:
            issues.append(CatalogIssue(rel, "; ".join(errors)))
            continue
        record["_file"] = rel
        records.append(record)
    return records, issues


def stale_records(records, as_of: datetime.date, max_age_days: int = MAX_SOURCE_AGE_DAYS):
    """Records whose source retrieval date is older than the freshness rule.

    A stale record is not automatically wrong, but it must be re-verified
    against the manufacturer's current documents before use in a design.
    """
    stale = []
    for record in records:
        retrieved = datetime.date.fromisoformat(record["source"]["retrieved_on"])
        if (as_of - retrieved).days > max_age_days:
            stale.append(record)
    return stale


def usable_for_design(records, as_of: datetime.date):
    """Records allowed into product selection: schema-valid, status
    'current', and within the source-freshness window. Everything else
    needs human re-verification first."""
    stale = {id(r) for r in stale_records(records, as_of)}
    return [r for r in records if r["status"] == "current" and id(r) not in stale]
