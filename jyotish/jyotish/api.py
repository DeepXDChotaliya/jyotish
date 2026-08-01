"""
Assembly layer. Turns a birth record into the JSON the console renders.

Nothing here computes anything on its own. It calls the engine, the lord
analysis, the yoga detectors, the dasha tree and gochar, and arranges the
results. Keeping it separate means the engine stays usable from a REPL.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from . import (
    ashtakavarga, character, dasha, gochar, interpret, lords, narrative,
    nakshatra, places, psyche, varga, yogas,
)
from .engine import (
    AYANAMSAS, NAKSHATRAS, SIGNS, SIGNS_SA, BirthData, Chart, compute_chart,
    graha_strength, nakshatra_lord, panchanga, sign_lord,
)

GRAHA_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
               "Rahu", "Ketu"]


def birth_from_dict(d: dict) -> BirthData:
    """Build BirthData from the UI payload, resolving a place name if given."""
    lat = d.get("latitude")
    lon = d.get("longitude")
    tz = d.get("tz_name") or None
    place = d.get("place", "")

    if (lat is None or lon is None) and place:
        hit = places.resolve(place)
        if hit is None:
            raise ValueError("Could not resolve the place %r. Type "
                             "coordinates instead." % place)
        lat, lon, tz = hit["latitude"], hit["longitude"], tz or hit["timezone"]

    if lat is None or lon is None:
        raise ValueError("A chart needs coordinates or a place name.")

    ayanamsa = d.get("ayanamsa", "Lahiri")
    if ayanamsa not in AYANAMSAS:
        raise ValueError("Unknown ayanamsa %r" % ayanamsa)

    missing = [k for k in ("year", "month", "day") if d.get(k) in (None, "")]
    if missing:
        raise ValueError("A chart needs a full date of birth. Missing: %s."
                         % ", ".join(missing))
    try:
        y, mo, dy = int(d["year"]), int(d["month"]), int(d["day"])
    except (TypeError, ValueError):
        raise ValueError("Year, month and day must be whole numbers.")
    if not (1800 <= y <= 2200) or not (1 <= mo <= 12) or not (1 <= dy <= 31):
        raise ValueError("Date out of range. Swiss Ephemeris is loaded for "
                         "1800 to 2200 here.")

    return BirthData(
        name=d.get("name", "Unnamed"),
        year=y, month=mo, day=dy,
        hour=int(d.get("hour", 12) or 0), minute=int(d.get("minute", 0) or 0),
        second=int(d.get("second", 0) or 0),
        latitude=float(lat), longitude=float(lon),
        place=place, tz_name=tz, ayanamsa=ayanamsa,
    )


def _deg_label(deg: float) -> str:
    d = int(deg)
    m = int((deg - d) * 60)
    s = int((((deg - d) * 60) - m) * 60)
    return "%02d° %02d' %02d\"" % (d, m, s)


def chart_grid(chart: Chart) -> list[dict]:
    """One entry per house, shaped for drawing a North or South chart."""
    out = []
    for h in range(1, 13):
        sign = chart.sign_of_house(h)
        out.append({
            "house": h,
            "sign_index": sign,
            "sign": SIGNS[sign],
            "sign_sanskrit": SIGNS_SA[sign],
            "lord": sign_lord(sign),
            "grahas": [
                {"name": g.name,
                 "degree": round(g.degree_in_sign, 2),
                 "retrograde": g.retrograde,
                 "combust": g.combust,
                 "dignity": g.dignity}
                for g in sorted(chart.grahas_in_house(h),
                                key=lambda x: x.longitude)
            ],
        })
    return out


def varga_grid(chart: Chart, name: str) -> dict:
    """A divisional chart in the same shape as the rasi grid."""
    result = varga.varga_chart(chart, name)
    lagna_sign = result.pop("_lagna")
    houses = []
    for h in range(1, 13):
        sign = (lagna_sign + h - 1) % 12
        occupants = [g for g, s in result.items() if s == sign]
        houses.append({
            "house": h,
            "sign_index": sign,
            "sign": SIGNS[sign],
            "lord": sign_lord(sign),
            "grahas": [{"name": g, "degree": None, "retrograde": False,
                        "combust": False, "dignity": ""}
                       for g in sorted(occupants,
                                       key=lambda x: GRAHA_ORDER.index(x))],
        })
    return {
        "name": name,
        "lagna_sign": SIGNS[lagna_sign],
        "houses": houses,
        "purpose": (varga.VARGAS[name].__doc__ or "").strip(),
    }


def reading(birth: BirthData, when: datetime = None) -> dict:
    """The whole chart, assembled once."""
    chart = compute_chart(birth)
    tz = birth.resolve_tz()
    when = when or datetime.now(ZoneInfo(tz))
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(tz))

    chain = dasha.running_chain(chart, when, depth=4)
    seed = dasha.seed(chart)
    lagna_sign = chart.lagna_sign

    janma = chart.grahas["Moon"].nakshatra
    # Computed once and shared: psyche and ashtakavarga both need it, and the
    # ephemeris calls are the expensive part of building this payload.
    positions = gochar.current_positions(when, chart)
    grahas = [lords.graha_report(chart, n) for n in GRAHA_ORDER]
    for g in grahas:
        g["degree_label"] = _deg_label(g["degree"])
        g["nakshatra_detail"] = nakshatra.nakshatra_report(
            chart.grahas[g["name"]].longitude, janma)
        g["nakshatra_chain"] = nakshatra.dispositor_chain(chart, g["name"])

    houses = lords.all_houses(chart)
    ysum = yogas.summary(chart)

    return {
        "birth": {
            "name": birth.name,
            "date": "%04d-%02d-%02d" % (birth.year, birth.month, birth.day),
            "date_label": datetime(birth.year, birth.month, birth.day)
                          .strftime("%d %B %Y"),
            "time": "%02d:%02d" % (birth.hour, birth.minute),
            "place": birth.place,
            "latitude": birth.latitude,
            "longitude": birth.longitude,
            "timezone": tz,
            "utc_offset": datetime(birth.year, birth.month, birth.day,
                                   birth.hour, birth.minute,
                                   tzinfo=ZoneInfo(tz)).strftime("%z"),
            "ayanamsa": birth.ayanamsa,
            "ayanamsa_value": round(chart.ayanamsa_value, 6),
            "ayanamsa_label": _deg_label(chart.ayanamsa_value),
            "julian_day": round(chart.jd, 6),
        },
        "lagna": {
            "longitude": round(chart.ascendant, 4),
            "sign": SIGNS[lagna_sign],
            "sign_sanskrit": SIGNS_SA[lagna_sign],
            "sign_index": lagna_sign,
            "degree": round(chart.ascendant - lagna_sign * 30, 4),
            "degree_label": _deg_label(chart.ascendant - lagna_sign * 30),
            "lord": sign_lord(lagna_sign),
            "lord_house": chart.grahas[sign_lord(lagna_sign)].house,
            "nakshatra": NAKSHATRAS[int(chart.ascendant // (360 / 27))],
            "nakshatra_lord": nakshatra_lord(int(chart.ascendant // (360 / 27))),
            "temperament": interpret.SIGNS_INFO[lagna_sign]["temperament"],
            "element": interpret.SIGNS_INFO[lagna_sign]["element"],
            "mode": interpret.SIGNS_INFO[lagna_sign]["mode"],
        },
        "panchanga": panchanga(chart),
        "grid": chart_grid(chart),
        "grahas": grahas,
        "houses": houses,
        "lord_map": lords.lord_map(chart),
        "yogas": ysum,
        "dasha": {
            "seed": {
                "lord": seed["lord"],
                "nakshatra": seed["nakshatra"],
                "pada": seed["pada"],
                "balance_years": round(seed["balance_years"], 4),
                "balance_label": dasha._duration(seed["balance_days"]),
                "note": "The dasha clock starts from the Moon in %s. %.1f%% of "
                        "that nakshatra was already spent at birth, so %s "
                        "opened with %s remaining of its %d year period." % (
                            seed["nakshatra"], seed["elapsed_fraction"] * 100,
                            seed["lord"], dasha._duration(seed["balance_days"]),
                            seed["full_years"]),
            },
            "mahadashas": dasha.periods_json(chart),
            "chain": chain,
            "reading": dasha.dasha_reading(chart, [c["lord"] for c in chain]),
        },
        "transits": gochar.transit_report(chart, when),
        "character": character.profile(chart),
        "brief": narrative.brief(chart, when),
        "nakshatras": {
            "janma": nakshatra.nakshatra_report(
                chart.grahas["Moon"].longitude, janma),
            "lagna": nakshatra.nakshatra_report(chart.ascendant, janma),
            "taras": nakshatra.TARAS,
            "all": [dict(nakshatra.NAKSHATRA_DATA[i], index=i,
                         range="%s to %s" % (
                             nakshatra._deg(i * nakshatra.SPAN),
                             nakshatra._deg((i + 1) * nakshatra.SPAN)),
                         tara=nakshatra.tara_bala(janma, i))
                    for i in range(27)],
        },
        "psyche": psyche.profile(chart, positions),
        "ashtakavarga": ashtakavarga.report(chart, positions),
        "vargas": [varga_grid(chart, n) for n in
                   ["D9 Navamsa", "D10 Dasamsa", "D7 Saptamsa", "D4 Chaturthamsa",
                    "D12 Dwadasamsa", "D3 Drekkana", "D2 Hora", "D16 Shodasamsa",
                    "D20 Vimsamsa", "D24 Siddhamsa", "D30 Trimsamsa"]],
        "vargottama": varga.vargottama(chart),
        "reference": {
            "houses": interpret.HOUSES,
            "signs": interpret.SIGNS_INFO,
            "grahas": interpret.GRAHAS_INFO,
            "nakshatras": NAKSHATRAS,
            "ayanamsas": list(AYANAMSAS),
            "varga_names": list(varga.VARGAS),
        },
        "computed_at": when.isoformat(),
    }


def dasha_branch(birth: BirthData, path: list) -> dict:
    """One level of the dasha tree, plus the reading for that branch."""
    chart = compute_chart(birth)
    periods = dasha.periods_json(chart, path)
    return {
        "path": path,
        "level": len(path) + 1,
        "level_name": dasha.LEVEL_NAMES.get(len(path) + 1, "Sub period"),
        "periods": periods,
        "reading": dasha.dasha_reading(chart, path) if path else None,
    }


def dasha_at(birth: BirthData, when: datetime) -> dict:
    chart = compute_chart(birth)
    tz = birth.resolve_tz()
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(tz))
    chain = dasha.running_chain(chart, when, depth=4)
    return {
        "moment": when.isoformat(),
        "moment_label": when.strftime("%d %b %Y"),
        "chain": chain,
        "reading": dasha.dasha_reading(chart, [c["lord"] for c in chain]),
    }


def transits_at(birth: BirthData, when: datetime) -> dict:
    chart = compute_chart(birth)
    return gochar.transit_report(chart, when)


def segments(birth: BirthData, start: datetime, end: datetime,
             level: int = 2) -> dict:
    """Flat dated bands over a window. The scan view."""
    chart = compute_chart(birth)
    tz = birth.resolve_tz()
    if start.tzinfo is None:
        start = start.replace(tzinfo=ZoneInfo(tz))
    if end.tzinfo is None:
        end = end.replace(tzinfo=ZoneInfo(tz))
    rows = dasha.timeline(chart, start, end, level)

    # Attach the parent chain so a band can be read without extra calls.
    for r in rows:
        r["strength"] = graha_strength(chart, r["lord"])["score"]
        r["functional"] = lords.functional_nature(chart, r["lord"])["label"]
        r["rules"] = lords.houses_ruled(chart, r["lord"])
        r["sits_in"] = chart.grahas[r["lord"]].house
    return {
        "start": start.isoformat(), "end": end.isoformat(),
        "level": level, "level_name": dasha.LEVEL_NAMES[level],
        "segments": rows,
    }
