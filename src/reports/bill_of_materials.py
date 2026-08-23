"""Procurement-ready bill of materials per docs/07 section 18.

Every line joins back to a catalog record so manufacturer, status,
source URL and verification date are never typed by hand. Prices appear
only when a verified current price is supplied (docs/06 s.21: never
assume pricing). A model with no catalog record fails loudly instead of
producing an untraceable line.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class BomLine:
    description: str
    manufacturer: str
    model: str
    quantity: int
    size: str
    compatibility: str
    accessories: str
    alternative_or_spec: str
    status: str
    source_url: str
    verified_on: str
    unit_price: str = ""          # only when verified; otherwise empty


def build_bom(items: list, catalog: list) -> list:
    """Build BOM lines from item requests.

    Each item: {model, quantity, description?, size?, accessories?,
    alternative_or_spec?, verified_unit_price?}. The model must exist in
    the catalog; status other than 'current' is carried through so the
    reader sees it needs attention.
    """
    by_model = {r["model"]: r for r in catalog}
    lines = []
    for item in items:
        model = item["model"]
        qty = item["quantity"]
        if qty < 1:
            raise ValueError(f"{model}: quantity must be at least 1")
        rec = by_model.get(model)
        if rec is None:
            raise ValueError(
                f"{model!r} has no record in the product catalog; add a current, "
                "sourced record before it can appear on a bill of materials")
        size_bits = []
        if rec.get("inlet_size_in"):
            size_bits.append(f'{rec["inlet_size_in"]:g}" inlet')
        lines.append(BomLine(
            description=item.get("description", rec.get("product_family", model)),
            manufacturer=rec["manufacturer"],
            model=model,
            quantity=qty,
            size=item.get("size", ", ".join(size_bits) or "—"),
            compatibility=rec.get("compatibility_notes", ""),
            accessories=item.get("accessories", ""),
            alternative_or_spec=item.get(
                "alternative_or_spec",
                "Verified equivalent permitted if performance and compatibility match"),
            status=rec["status"],
            source_url=rec["source"]["url"],
            verified_on=rec["source"]["retrieved_on"],
            unit_price=item.get("verified_unit_price", ""),
        ))
    return lines


def to_markdown(lines: list) -> str:
    if not lines:
        raise ValueError("a bill of materials needs at least one line")
    show_price = any(l.unit_price for l in lines)
    head = "| Item | Manufacturer / Model | Qty | Size | Status | Verified |"
    sep = "|---|---|---|---|---|---|"
    if show_price:
        head = head[:-1] + " Price |"
        sep += "---|"
    out = [head, sep]
    for l in lines:
        status = l.status if l.status == "current" else f"**{l.status}**"
        row = (f"| {l.description} | {l.manufacturer} {l.model} | {l.quantity} | "
               f"{l.size} | {status} | {l.verified_on} |")
        if show_price:
            row += f" {l.unit_price or '—'} |"
        out.append(row)
    notes = []
    for l in lines:
        bits = []
        if l.compatibility:
            bits.append(f"compatibility: {l.compatibility}")
        if l.accessories:
            bits.append(f"accessories: {l.accessories}")
        bits.append(f"alternatives: {l.alternative_or_spec}")
        bits.append(f"source: {l.source_url}")
        notes.append(f"- **{l.model}** — " + "; ".join(bits))
    if not show_price:
        out.append("")
        out.append("Prices are omitted: no current pricing has been verified.")
    return "\n".join(out) + "\n\n" + "\n".join(notes) + "\n"
