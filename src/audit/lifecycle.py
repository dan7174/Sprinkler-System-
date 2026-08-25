"""Existing-product identification and lifecycle status, per docs/06
section 17 (obsolete products, steps 1-3).

Identification matches a user-reported model string against the catalog
without guessing: an ambiguous or unknown string returns instructions
for verifying against the manufacturer's upgrade guide instead of a
forced match.
"""

import re
from dataclasses import dataclass

# From knowledge/source_manifest.yaml: Rain Bird Product Upgrade Guide.
UPGRADE_GUIDE_URL = "https://store.rainbird.com/upgrade-guide"


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


@dataclass(frozen=True)
class Identification:
    matched: bool
    record: dict = None
    candidates: tuple = ()
    guidance: str = ""


def identify(model_text: str, catalog: list) -> Identification:
    """Match a reported model string to catalog records.

    Exact normalized match wins; otherwise all records whose normalized
    model contains (or is contained by) the query become candidates. One
    candidate = a match; several = ambiguous with the list returned;
    none = unknown with verification guidance.
    """
    if not model_text or not model_text.strip():
        raise ValueError("model_text must not be empty")
    q = _norm(model_text)
    if not q:
        raise ValueError(f"model_text {model_text!r} contains no identifiable characters")

    exact = [r for r in catalog if _norm(r["model"]) == q]
    if exact:
        return Identification(True, exact[0])
    partial = [r for r in catalog
               if q in _norm(r["model"]) or _norm(r["model"]) in q]
    if len(partial) == 1:
        return Identification(True, partial[0])
    if partial:
        return Identification(
            False, None, tuple(sorted(r["model"] for r in partial)),
            "Several catalog models match; identify the exact model from the "
            "product's cap, body stamp or nozzle marking and retry.")
    return Identification(
        False, None, (),
        f"No catalog record matches {model_text!r}. Identify the exact model from "
        f"the product itself, then check the manufacturer's upgrade guide "
        f"({UPGRADE_GUIDE_URL}) for current/discontinued status, and add a sourced "
        "record to the catalog before designing around it.")


def lifecycle_status(model: str, catalog: list) -> dict:
    """Status report for one identified model.

    Returns status plus what it means for a retrofit. Unknown models get
    'unknown_requires_verification' with the upgrade-guide instruction —
    never an assumed status.
    """
    ident = identify(model, catalog)
    if not ident.matched:
        return {"model": model, "status": "unknown_requires_verification",
                "action": ident.guidance, "candidates": list(ident.candidates)}
    rec = ident.record
    status = rec["status"]
    action = {
        "current": "Current product: replacement parts and published data available.",
        "discontinued": "Discontinued: verify replacement guidance in the upgrade guide "
                        f"({UPGRADE_GUIDE_URL}) and treat as a replacement-check case.",
        "replacement_available": "Superseded: a designated replacement exists"
                                 + (f" ({rec.get('replacement_model')})" if rec.get("replacement_model") else "")
                                 + "; run the replacement compatibility check.",
        "unknown_requires_verification": "Status unverified: confirm against the "
                                         "manufacturer's current documents before use.",
    }[status]
    return {"model": rec["model"], "status": status, "action": action,
            "source_url": rec["source"]["url"],
            "verified_on": rec["source"]["retrieved_on"]}
