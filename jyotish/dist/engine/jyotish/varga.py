"""
Divisional charts. Pure arithmetic on D1 longitudes, no ephemeris calls.

Every function takes a sidereal longitude and returns a sign index 0-11.
"""

from __future__ import annotations

MOVABLE = (0, 3, 6, 9)
FIXED = (1, 4, 7, 10)
DUAL = (2, 5, 8, 11)


def _split(longitude: float, divisions: int) -> tuple[int, int]:
    sign = int(longitude // 30)
    deg = longitude - sign * 30
    part = int(deg // (30 / divisions))
    return sign, min(part, divisions - 1)


def d1(longitude: float) -> int:
    return int(longitude // 30)


def d2_hora(longitude: float) -> int:
    """Wealth. Leo and Cancer only."""
    sign, part = _split(longitude, 2)
    odd = sign % 2 == 0
    if odd:
        return 4 if part == 0 else 3   # Leo then Cancer
    return 3 if part == 0 else 4       # Cancer then Leo


def d3_drekkana(longitude: float) -> int:
    """Siblings, courage."""
    sign, part = _split(longitude, 3)
    return (sign + part * 4) % 12


def d4_chaturthamsa(longitude: float) -> int:
    """Property, fixed assets."""
    sign, part = _split(longitude, 4)
    return (sign + part * 3) % 12


def d7_saptamsa(longitude: float) -> int:
    """Children, progeny."""
    sign, part = _split(longitude, 7)
    start = sign if sign % 2 == 0 else (sign + 6) % 12
    return (start + part) % 12


def d9_navamsa(longitude: float) -> int:
    """Marriage, dharma, the strength test for every graha."""
    sign, part = _split(longitude, 9)
    return (sign * 9 + part) % 12


def d10_dasamsa(longitude: float) -> int:
    """Career, karma, public standing."""
    sign, part = _split(longitude, 10)
    start = sign if sign % 2 == 0 else (sign + 8) % 12
    return (start + part) % 12


def d12_dwadasamsa(longitude: float) -> int:
    """Parents, ancestry."""
    sign, part = _split(longitude, 12)
    return (sign + part) % 12


def d16_shodasamsa(longitude: float) -> int:
    """Vehicles, comforts, mental happiness."""
    sign, part = _split(longitude, 16)
    if sign in MOVABLE:
        start = 0
    elif sign in FIXED:
        start = 4
    else:
        start = 8
    return (start + part) % 12


def d20_vimsamsa(longitude: float) -> int:
    """Spiritual practice, upasana."""
    sign, part = _split(longitude, 20)
    if sign in MOVABLE:
        start = 0
    elif sign in FIXED:
        start = 8
    else:
        start = 4
    return (start + part) % 12


def d24_siddhamsa(longitude: float) -> int:
    """Learning, education."""
    sign, part = _split(longitude, 24)
    start = 4 if sign % 2 == 0 else 3
    return (start + part) % 12


def d30_trimsamsa(longitude: float) -> int:
    """Misfortune, weaknesses. Unequal divisions, no Moon or Sun rulership."""
    sign = int(longitude // 30)
    deg = longitude - sign * 30
    odd = sign % 2 == 0
    if odd:
        bounds = [(5, 0), (10, 10), (18, 8), (25, 2), (30, 6)]   # Mars Sat Jup Mer Ven
    else:
        bounds = [(5, 1), (12, 5), (20, 11), (25, 9), (30, 7)]   # Ven Mer Jup Sat Mars
    for limit, s in bounds:
        if deg < limit:
            return s
    return bounds[-1][1]


VARGAS = {
    "D1 Rasi": d1,
    "D2 Hora": d2_hora,
    "D3 Drekkana": d3_drekkana,
    "D4 Chaturthamsa": d4_chaturthamsa,
    "D7 Saptamsa": d7_saptamsa,
    "D9 Navamsa": d9_navamsa,
    "D10 Dasamsa": d10_dasamsa,
    "D12 Dwadasamsa": d12_dwadasamsa,
    "D16 Shodasamsa": d16_shodasamsa,
    "D20 Vimsamsa": d20_vimsamsa,
    "D24 Siddhamsa": d24_siddhamsa,
    "D30 Trimsamsa": d30_trimsamsa,
}


def varga_chart(chart, varga_name: str) -> dict:
    """Returns {graha_name: sign_index} plus the varga lagna."""
    fn = VARGAS[varga_name]
    out = {name: fn(g.longitude) for name, g in chart.grahas.items()}
    out["_lagna"] = fn(chart.ascendant)
    return out


def vargottama(chart) -> list[str]:
    """Grahas occupying the same sign in D1 and D9. A strength marker."""
    return [
        name for name, g in chart.grahas.items()
        if d1(g.longitude) == d9_navamsa(g.longitude)
    ]
