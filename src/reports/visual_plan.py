"""SVG visual plan generator, per docs/07 section 19 drawing standards.

Input geometry is in feet; the generator handles scaling, title block,
north arrow, scale bar, legend, zone colors and the status label. A plan
whose status is not 'For construction' is watermarked. The output is a
plain SVG string with no external references.
"""

import html
from dataclasses import dataclass, field

from calculators.units import _require_positive

AREA_STYLES = {
    "lot":      {"fill": "none",    "stroke": "#777777", "dash": "8,6", "label": "Property line"},
    "house":    {"fill": "#d9d4c7", "stroke": "#8a8272", "dash": "",    "label": "Building"},
    "hardscape":{"fill": "#e6e2d6", "stroke": "#9a9280", "dash": "",    "label": "Hardscape"},
    "lawn":     {"fill": "#dce8c9", "stroke": "#6c8a45", "dash": "",    "label": "Lawn"},
    "bed":      {"fill": "#ece5c3", "stroke": "#a08c4a", "dash": "",    "label": "Planting bed"},
}
ZONE_COLORS = ["#4d7a3a", "#3f7fa6", "#a4682f", "#7a4d8a", "#a63f5f", "#3fa68a"]
VALID_STATUSES = ("Preliminary — Not for construction", "For review", "For construction")


@dataclass(frozen=True)
class PlanArea:
    kind: str          # key of AREA_STYLES
    x_ft: float
    y_ft: float
    w_ft: float
    h_ft: float
    name: str = ""


@dataclass(frozen=True)
class PlanHead:
    x_ft: float
    y_ft: float
    radius_ft: float
    arc_start_deg: float      # 0 = east, counterclockwise positive
    arc_sweep_deg: float      # 360 for full circle
    zone_number: int
    label: str = ""


@dataclass(frozen=True)
class PlanPoint:
    x_ft: float
    y_ft: float
    code: str                 # e.g. POC, BF, M, C, V1
    name: str = ""


def _esc(s):
    return html.escape(str(s), quote=True)


def _arc_path(cx, cy, r, start_deg, sweep_deg):
    import math
    if sweep_deg >= 360:
        return None  # rendered as a circle
    a0 = math.radians(-start_deg)
    a1 = math.radians(-(start_deg + sweep_deg))
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if sweep_deg > 180 else 0
    return (f"M {cx:.1f} {cy:.1f} L {x0:.1f} {y0:.1f} "
            f"A {r:.1f} {r:.1f} 0 {large} 1 {x1:.1f} {y1:.1f} Z")


def render_svg(title: str, location: str, date: str, status: str,
               areas: list, heads: list = (), points: list = (),
               px_per_ft: float = 6.0, notes: str = "") -> str:
    """Render the plan. All required title-block fields are mandatory."""
    for name, v in (("title", title), ("location", location), ("date", date)):
        if not v or not str(v).strip():
            raise ValueError(f"{name} is required on every drawing (docs/07 s.19)")
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {VALID_STATUSES}, got {status!r}")
    if not areas:
        raise ValueError("a plan needs at least one area")
    _require_positive(px_per_ft, "px_per_ft")

    minx = min(a.x_ft for a in areas)
    miny = min(a.y_ft for a in areas)
    maxx = max(a.x_ft + a.w_ft for a in areas)
    maxy = max(a.y_ft + a.h_ft for a in areas)
    pad = 30
    header = 64
    footer = 88
    W = (maxx - minx) * px_per_ft + pad * 2
    H = (maxy - miny) * px_per_ft + pad * 2 + header + footer
    X = lambda ft: (ft - minx) * px_per_ft + pad
    Y = lambda ft: (ft - miny) * px_per_ft + pad + header

    p = []
    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
             f'font-family="Helvetica, Arial, sans-serif">')
    p.append(f'<rect width="{W:.0f}" height="{H:.0f}" fill="#fbfaf4"/>')
    # title block
    p.append(f'<text x="{pad}" y="26" font-size="18" font-weight="bold" fill="#333">{_esc(title)}</text>')
    p.append(f'<text x="{pad}" y="44" font-size="11" fill="#555">{_esc(location)} · {_esc(date)} · '
             f'Scale: 1 in = {96/px_per_ft:.0f} ft · Units: feet</text>')
    badge = "#a4442f" if status != "For construction" else "#4d7a3a"
    p.append(f'<text x="{W-pad:.0f}" y="26" font-size="12" font-weight="bold" '
             f'text-anchor="end" fill="{badge}">{_esc(status.upper())}</text>')
    # north arrow (up = north)
    nx, ny = W - pad - 12, 58
    p.append(f'<g stroke="#555" fill="#555"><path d="M {nx} {ny} l -6 14 l 6 -5 l 6 5 Z"/>'
             f'<text x="{nx}" y="{ny+26}" font-size="10" text-anchor="middle" stroke="none">N</text></g>')

    used_kinds = []
    for a in areas:
        st = AREA_STYLES.get(a.kind)
        if st is None:
            raise ValueError(f"unknown area kind {a.kind!r}; known: {sorted(AREA_STYLES)}")
        if a.kind not in used_kinds:
            used_kinds.append(a.kind)
        dash = f' stroke-dasharray="{st["dash"]}"' if st["dash"] else ""
        p.append(f'<rect x="{X(a.x_ft):.1f}" y="{Y(a.y_ft):.1f}" '
                 f'width="{a.w_ft*px_per_ft:.1f}" height="{a.h_ft*px_per_ft:.1f}" '
                 f'fill="{st["fill"]}" stroke="{st["stroke"]}" stroke-width="1.5"{dash}/>')
        if a.name:
            p.append(f'<text x="{X(a.x_ft + a.w_ft/2):.1f}" y="{Y(a.y_ft + a.h_ft/2):.1f}" '
                     f'font-size="10" text-anchor="middle" fill="#444">{_esc(a.name)}</text>')

    zones_used = []
    for hd in heads:
        color = ZONE_COLORS[(hd.zone_number - 1) % len(ZONE_COLORS)]
        if hd.zone_number not in zones_used:
            zones_used.append(hd.zone_number)
        cx, cy, r = X(hd.x_ft), Y(hd.y_ft), hd.radius_ft * px_per_ft
        path = _arc_path(cx, cy, r, hd.arc_start_deg, hd.arc_sweep_deg)
        if path is None:
            p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}" '
                     f'fill-opacity="0.16" stroke="{color}" stroke-width="1"/>')
        else:
            p.append(f'<path d="{path}" fill="{color}" fill-opacity="0.16" '
                     f'stroke="{color}" stroke-width="1"/>')
        p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.2" fill="{color}"/>')
        if hd.label:
            p.append(f'<text x="{cx+5:.1f}" y="{cy-5:.1f}" font-size="8" fill="{color}">{_esc(hd.label)}</text>')

    for pt in points:
        cx, cy = X(pt.x_ft), Y(pt.y_ft)
        p.append(f'<rect x="{cx-9:.1f}" y="{cy-9:.1f}" width="18" height="18" rx="3" '
                 f'fill="#3f7fa6" stroke="#28536b"/>')
        p.append(f'<text x="{cx:.1f}" y="{cy+3.5:.1f}" font-size="8" font-weight="bold" '
                 f'text-anchor="middle" fill="#ffffff">{_esc(pt.code)}</text>')

    # scale bar: 20 ft
    sb_x, sb_y, sb_w = pad, H - footer + 18, 20 * px_per_ft
    p.append(f'<rect x="{sb_x}" y="{sb_y}" width="{sb_w:.1f}" height="5" fill="#333"/>')
    p.append(f'<text x="{sb_x}" y="{sb_y+18}" font-size="10" fill="#333">0</text>')
    p.append(f'<text x="{sb_x+sb_w:.1f}" y="{sb_y+18}" font-size="10" fill="#333" '
             f'text-anchor="end">20 ft</text>')
    # legend
    lx = sb_x + sb_w + 30
    for kind in used_kinds:
        st = AREA_STYLES[kind]
        p.append(f'<rect x="{lx}" y="{sb_y-4}" width="12" height="12" fill="{st["fill"]}" '
                 f'stroke="{st["stroke"]}"/>')
        p.append(f'<text x="{lx+16}" y="{sb_y+6}" font-size="9" fill="#333">{_esc(st["label"])}</text>')
        lx += 16 + 7 * len(st["label"]) + 18
    for zn in zones_used:
        color = ZONE_COLORS[(zn - 1) % len(ZONE_COLORS)]
        p.append(f'<circle cx="{lx+6}" cy="{sb_y+2}" r="5" fill="{color}" fill-opacity="0.4" '
                 f'stroke="{color}"/>')
        p.append(f'<text x="{lx+16}" y="{sb_y+6}" font-size="9" fill="#333">Zone {zn}</text>')
        lx += 70
    if notes:
        p.append(f'<text x="{pad}" y="{H-footer+44:.0f}" font-size="9" fill="#555">{_esc(notes)}</text>')
    p.append(f'<text x="{pad}" y="{H-footer+60:.0f}" font-size="9" fill="#777">'
             'Verified dimensions are labeled in the zone schedule; unlabeled geometry is '
             'user-provided and requires field verification.</text>')

    if status != "For construction":
        p.append(f'<text x="{W/2:.0f}" y="{(H+header)/2:.0f}" font-size="{max(20, W/18):.0f}" '
                 f'text-anchor="middle" fill="#a4442f" fill-opacity="0.16" '
                 f'transform="rotate(-18 {W/2:.0f} {(H+header)/2:.0f})">NOT FOR CONSTRUCTION</text>')
    p.append("</svg>")
    return "\n".join(p)
