"""
Chart rendering to inline SVG. No dependencies, returns a string.

North Indian: houses are fixed, signs rotate. Lagna sits top centre.
South Indian: signs are fixed, the lagna is marked.
"""

from __future__ import annotations

from .engine import SIGNS

ABBR = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa",
    "Rahu": "Ra", "Ketu": "Ke",
}

# Fractional centres of each house in the North Indian diamond, house 1 first.
NORTH_CENTRES = [
    (0.50, 0.25), (0.25, 0.11), (0.11, 0.25), (0.25, 0.50),
    (0.11, 0.75), (0.25, 0.89), (0.50, 0.75), (0.75, 0.89),
    (0.89, 0.75), (0.75, 0.50), (0.89, 0.25), (0.75, 0.11),
]

# Grid position of each sign in the South Indian layout, Aries first.
SOUTH_CELLS = [
    (1, 0), (2, 0), (3, 0), (3, 1), (3, 2), (3, 3),
    (2, 3), (1, 3), (0, 3), (0, 2), (0, 1), (0, 0),
]


def _placements(chart, varga_signs=None):
    """Returns {sign_index: [abbr, ...]} and the lagna sign."""
    if varga_signs:
        lagna = varga_signs["_lagna"]
        by_sign: dict[int, list[str]] = {}
        for name, sign in varga_signs.items():
            if name.startswith("_"):
                continue
            by_sign.setdefault(sign, []).append(ABBR[name])
        return by_sign, lagna

    lagna = chart.lagna_sign
    by_sign = {}
    for name, g in chart.grahas.items():
        tag = ABBR[name]
        if g.retrograde and name not in ("Rahu", "Ketu"):
            tag += "\u1d3f"
        by_sign.setdefault(g.sign, []).append(tag)
    return by_sign, lagna


def north_indian(chart, varga_signs=None, size: int = 420,
                 transit_signs: dict | None = None) -> str:
    by_sign, lagna = _placements(chart, varga_signs)
    s = size
    parts = [
        f'<svg viewBox="0 0 {s} {s}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Georgia, serif">',
        f'<rect x="1" y="1" width="{s-2}" height="{s-2}" fill="none" '
        f'stroke="currentColor" stroke-width="1.5"/>',
        f'<line x1="1" y1="1" x2="{s-1}" y2="{s-1}" stroke="currentColor"/>',
        f'<line x1="{s-1}" y1="1" x2="1" y2="{s-1}" stroke="currentColor"/>',
        f'<polygon points="{s/2},1 {s-1},{s/2} {s/2},{s-1} 1,{s/2}" '
        f'fill="none" stroke="currentColor"/>',
    ]

    for house in range(1, 13):
        sign = (lagna + house - 1) % 12
        fx, fy = NORTH_CENTRES[house - 1]
        x, y = fx * s, fy * s
        parts.append(
            f'<text x="{x:.0f}" y="{y-14:.0f}" text-anchor="middle" '
            f'font-size="11" opacity="0.55">{sign + 1}</text>'
        )
        occupants = by_sign.get(sign, [])
        for i, tag in enumerate(occupants):
            parts.append(
                f'<text x="{x:.0f}" y="{y + i*13:.0f}" text-anchor="middle" '
                f'font-size="12.5" font-weight="600">{tag}</text>'
            )
        if transit_signs:
            moving = [ABBR[n] for n, sg in transit_signs.items() if sg == sign]
            if moving:
                parts.append(
                    f'<text x="{x:.0f}" y="{y + len(occupants)*13 + 12:.0f}" '
                    f'text-anchor="middle" font-size="10.5" opacity="0.6" '
                    f'font-style="italic">{" ".join(moving)}</text>'
                )

    parts.append("</svg>")
    return "\n".join(parts)


def south_indian(chart, varga_signs=None, size: int = 420) -> str:
    by_sign, lagna = _placements(chart, varga_signs)
    cell = size / 4
    parts = [
        f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Georgia, serif">'
    ]

    for sign, (col, row) in enumerate(SOUTH_CELLS):
        x, y = col * cell, row * cell
        is_lagna = sign == lagna
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" '
            f'height="{cell:.1f}" fill="none" stroke="currentColor" '
            f'stroke-width="{2.2 if is_lagna else 1}"/>'
        )
        parts.append(
            f'<text x="{x+5:.0f}" y="{y+14:.0f}" font-size="10" '
            f'opacity="0.55">{SIGNS[sign][:3]}</text>'
        )
        if is_lagna:
            parts.append(
                f'<text x="{x+cell-5:.0f}" y="{y+14:.0f}" text-anchor="end" '
                f'font-size="10" font-weight="700">La</text>'
            )
        for i, tag in enumerate(by_sign.get(sign, [])):
            parts.append(
                f'<text x="{x+cell/2:.0f}" y="{y+32+i*14:.0f}" '
                f'text-anchor="middle" font-size="12.5" '
                f'font-weight="600">{tag}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)
