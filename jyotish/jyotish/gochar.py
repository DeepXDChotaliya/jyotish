"""
Gochar. Transits read against a natal chart, and the dates they change.

The useful question is never "where is Saturn". It is "when does Saturn leave
this house, and what does it touch on the way through". Everything here is
solved against the ephemeris by bisection rather than estimated from mean
motion, so retrograde loops produce the three real crossings and not one
average one.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import swisseph as swe

from . import interpret, nakshatra, phala
from .engine import (
    AYANAMSAS, DUSTHANA, GRAHAS, KENDRA, NAKSHATRAS, SIGNS, SPECIAL_ASPECTS,
    TRIKONA, UPACHAYA, Chart, _flags, _nakshatra_pada, sign_lord,
)
from .lords import _ord, functional_nature

# How far ahead it is worth scanning each graha for a sign change, in days.
SCAN_WINDOW = {
    "Sun": 400, "Moon": 40, "Mercury": 400, "Venus": 500,
    "Mars": 900, "Jupiter": 2000, "Saturn": 4000, "Rahu": 2000, "Ketu": 2000,
}

# Step size for the coarse scan. Small enough that no sign is skipped.
SCAN_STEP = {
    "Sun": 2.0, "Moon": 0.2, "Mercury": 1.0, "Venus": 1.5,
    "Mars": 3.0, "Jupiter": 8.0, "Saturn": 15.0, "Rahu": 10.0, "Ketu": 10.0,
}


def _jd(when: datetime) -> float:
    ut = when.astimezone(ZoneInfo("UTC"))
    return swe.julday(ut.year, ut.month, ut.day,
                      ut.hour + ut.minute / 60 + ut.second / 3600,
                      swe.GREG_CAL)


def _from_jd(jd: float, tz: str) -> datetime:
    y, m, d, frac = swe.revjul(jd, swe.GREG_CAL)
    hours = int(frac)
    minutes = int((frac - hours) * 60)
    dt = datetime(y, m, d, hours, min(minutes, 59), tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo(tz))


def _longitude(jd: float, graha: str) -> float:
    if graha == "Ketu":
        values, _ = swe.calc_ut(jd, GRAHAS["Rahu"], _flags())
        return (values[0] + 180) % 360
    values, _ = swe.calc_ut(jd, GRAHAS[graha], _flags())
    return values[0] % 360


def _sign_at(jd: float, graha: str) -> int:
    return int(_longitude(jd, graha) // 30)


def ingresses(graha: str, start: datetime, count: int = 6,
              ayanamsa: str = "Lahiri", tz: str = "UTC") -> list[dict]:
    """The next `count` sign changes for a graha, solved to the minute.

    Retrograde grahas cross the same boundary up to three times. All three are
    returned, in order, because the middle one is usually the interesting date.
    """
    swe.set_sid_mode(AYANAMSAS[ayanamsa], 0, 0)
    jd = _jd(start)
    step = SCAN_STEP[graha]
    limit = jd + SCAN_WINDOW[graha]

    out = []
    current = _sign_at(jd, graha)
    cursor = jd
    while cursor < limit and len(out) < count:
        nxt = cursor + step
        if nxt > limit:
            break
        s = _sign_at(nxt, graha)
        if s != current:
            lo, hi = cursor, nxt
            for _ in range(40):                # bisect to under a minute
                mid = (lo + hi) / 2
                if _sign_at(mid, graha) == current:
                    lo = mid
                else:
                    hi = mid
            when = _from_jd(hi, tz)
            speed = swe.calc_ut(hi, GRAHAS["Rahu" if graha == "Ketu" else graha],
                                _flags())[0][3]
            retro = speed < 0 if graha not in ("Rahu", "Ketu") else True
            out.append({
                "graha": graha,
                "from_sign": SIGNS[current],
                "to_sign": SIGNS[s],
                "date": when.isoformat(),
                "date_label": when.strftime("%d %b %Y, %H:%M"),
                "day": when.strftime("%d %b %Y"),
                "retrograde": retro,
                "direction": "back into" if retro else "into",
            })
            current = s
        cursor = nxt
    return out


def station_dates(graha: str, start: datetime, count: int = 4,
                  ayanamsa: str = "Lahiri", tz: str = "UTC") -> list[dict]:
    """When a graha turns retrograde or direct. Nodes are always retrograde."""
    if graha in ("Rahu", "Ketu", "Sun", "Moon"):
        return []
    swe.set_sid_mode(AYANAMSAS[ayanamsa], 0, 0)
    jd = _jd(start)
    limit = jd + SCAN_WINDOW[graha]
    step = 2.0

    def speed(t):
        return swe.calc_ut(t, GRAHAS[graha], _flags())[0][3]

    out = []
    cursor = jd
    prev = speed(cursor)
    while cursor < limit and len(out) < count:
        nxt = cursor + step
        s = speed(nxt)
        if (prev < 0) != (s < 0):
            lo, hi = cursor, nxt
            for _ in range(40):
                mid = (lo + hi) / 2
                if (speed(mid) < 0) == (prev < 0):
                    lo = mid
                else:
                    hi = mid
            when = _from_jd(hi, tz)
            out.append({
                "graha": graha,
                "event": "turns direct" if prev < 0 else "turns retrograde",
                "date": when.isoformat(),
                "day": when.strftime("%d %b %Y"),
                "sign": SIGNS[_sign_at(hi, graha)],
            })
        prev = s
        cursor = nxt
    return out


def current_positions(when: datetime, natal: Chart) -> list[dict]:
    """Where every graha is now, and what that means against the natal chart."""
    swe.set_sid_mode(AYANAMSAS[natal.birth.ayanamsa], 0, 0)
    jd = _jd(when)
    lagna_sign = natal.lagna_sign
    moon_sign = natal.grahas["Moon"].sign

    out = []
    for graha in list(GRAHAS) + ["Ketu"]:
        lon = _longitude(jd, graha)
        sign = int(lon // 30)
        nak, pada = _nakshatra_pada(lon)
        house = ((sign - lagna_sign) % 12) + 1
        from_moon = ((sign - moon_sign) % 12) + 1
        if graha in ("Rahu", "Ketu"):
            speed, retro = 0.0, True
        else:
            speed = swe.calc_ut(jd, GRAHAS[graha], _flags())[0][3]
            retro = speed < 0

        natal_hits = []
        for nname, ng in natal.grahas.items():
            sep = abs((lon - ng.longitude + 180) % 360 - 180)
            if sep <= 3:
                natal_hits.append({
                    "graha": nname, "kind": "conjunction",
                    "orb": round(sep, 2),
                    "note": "Transiting %s is within %.1f degrees of natal %s." % (
                        graha, sep, nname)})
            elif abs(sep - 180) <= 3:
                natal_hits.append({
                    "graha": nname, "kind": "opposition",
                    "orb": round(abs(sep - 180), 2),
                    "note": "Transiting %s opposes natal %s within %.1f "
                            "degrees." % (graha, nname, abs(sep - 180))})

        aspected = [((house - 1 + d - 1) % 12) + 1
                    for d in SPECIAL_ASPECTS.get(graha, (7,))]

        out.append({
            "graha": graha,
            "longitude": round(lon, 4),
            "sign": SIGNS[sign],
            "sign_index": sign,
            "degree": round(lon - sign * 30, 2),
            "nakshatra": NAKSHATRAS[nak],
            "pada": pada,
            "house": house,
            "house_title": interpret.HOUSES[house - 1]["title"],
            "from_moon": from_moon,
            "retrograde": retro,
            "speed": round(speed, 4),
            "aspecting_houses": aspected,
            "natal_contacts": natal_hits,
            "note": _transit_note(natal, graha, house, from_moon),
            "phala": phala.transit_phala(graha, house),
            "duration": phala.TRANSIT_DURATION.get(graha, ""),
            "slow": graha in phala.SLOW,
            # Tara bala from the natal Moon. A graha crossing the Vipat or
            # Vadha tara behaves quite differently from the same graha in
            # Sampat, and it is the cheapest useful refinement there is.
            "tara": nakshatra.tara_bala(natal.grahas["Moon"].nakshatra, nak),
            "nakshatra_lord": nakshatra.data(nak)["lord"],
        })
    return out


def _transit_note(natal: Chart, graha: str, house: int, from_moon: int) -> str:
    nature = functional_nature(natal, graha)
    h = interpret.HOUSES[house - 1]
    ruled = nature["ruled"]
    base = "%s is transiting your %s, the house of %s." % (
        graha, _ord(house), h["title"].lower())
    if ruled:
        base += " In your chart %s rules the %s, so those matters are being " \
                "stirred as it passes." % (
                    graha, " and ".join(_ord(r) for r in ruled))
    if house in DUSTHANA:
        base += " This is a dusthana, so expect friction rather than reward " \
                "while it sits here."
    elif house in TRIKONA:
        base += " A trine, so the transit is supportive."
    elif house in KENDRA:
        base += " An angle, so whatever it does will be visible."
    elif house in UPACHAYA:
        base += " An upachaya, where even malefics do useful work."
    base += " Counted from your natal Moon it is the %s, %s." % (
        _ord(from_moon),
        "which is where the mind actually registers it"
        if from_moon in (1, 4, 7, 10) else
        "a supportive position from the mind" if from_moon in (5, 9)
        else "a position the mind reads as pressure"
        if from_moon in (6, 8, 12) else "a neutral position from the mind")
    return base


def sade_sati_window(natal: Chart, when: datetime) -> dict:
    """Saturn against the natal Moon, with the actual entry and exit dates."""
    swe.set_sid_mode(AYANAMSAS[natal.birth.ayanamsa], 0, 0)
    tz = natal.birth.resolve_tz()
    moon_sign = natal.grahas["Moon"].sign
    jd = _jd(when)
    sat_sign = _sign_at(jd, "Saturn")
    offset = (sat_sign - moon_sign) % 12

    phases = {11: ("Rising phase", "12th from the Moon",
                   "The first two and a half years. Losses and expenses "
                   "surface, and things that were carried past their time "
                   "start to fall away."),
              0: ("Peak phase", "over the natal Moon",
                  "The middle stretch. Saturn sits on the mind itself. This is "
                  "where the reorganisation actually happens, and where it "
                  "costs the most."),
              1: ("Setting phase", "2nd from the Moon",
                  "The last two and a half years. Pressure moves to resources, "
                  "family and speech, then lifts.")}

    active = offset in phases
    result = {
        "active": active,
        "moon_sign": SIGNS[moon_sign],
        "saturn_sign": SIGNS[sat_sign],
        "offset": offset,
        "kantaka": offset in (3, 9),
        "ashtama": offset == 7,
    }

    if active:
        name, position, text = phases[offset]
        result.update({"phase": name, "position": position, "text": text})

    # Solve the full window: Saturn entering the 12th and leaving the 2nd.
    start_sign = (moon_sign + 11) % 12
    end_sign = (moon_sign + 2) % 12
    search_from = when - timedelta(days=3000) if active else when

    entry = _first_entry_into(start_sign, "Saturn", search_from, tz)
    exit_ = _first_entry_into(end_sign, "Saturn", search_from, tz)
    if entry:
        result["window_start"] = entry
    if exit_:
        result["window_end"] = exit_

    if not active:
        nxt = _first_entry_into(start_sign, "Saturn", when, tz)
        if nxt:
            result["next_start"] = nxt
    return result


def _first_entry_into(sign: int, graha: str, start: datetime,
                      tz: str) -> str | None:
    """The next moment `graha` enters `sign`, scanning up to 30 years."""
    jd = _jd(start)
    step = SCAN_STEP[graha]
    limit = jd + 11000
    cursor = jd
    current = _sign_at(cursor, graha)
    while cursor < limit:
        nxt = cursor + step
        s = _sign_at(nxt, graha)
        if s != current and s == sign:
            lo, hi = cursor, nxt
            for _ in range(40):
                mid = (lo + hi) / 2
                if _sign_at(mid, graha) == current:
                    lo = mid
                else:
                    hi = mid
            return _from_jd(hi, tz).strftime("%d %b %Y")
        current = s
        cursor = nxt
    return None


def upcoming(natal: Chart, when: datetime, grahas: list = None) -> list[dict]:
    """A merged, dated list of every transition worth knowing about."""
    tz = natal.birth.resolve_tz()
    grahas = grahas or ["Jupiter", "Saturn", "Rahu", "Ketu", "Mars",
                        "Sun", "Venus", "Mercury"]
    events = []
    for g in grahas:
        for ing in ingresses(g, when, count=3 if g in ("Sun", "Mercury", "Venus")
                             else 4, ayanamsa=natal.birth.ayanamsa, tz=tz):
            sign_index = SIGNS.index(ing["to_sign"])
            house = ((sign_index - natal.lagna_sign) % 12) + 1
            from_moon = ((sign_index - natal.grahas["Moon"].sign) % 12) + 1
            events.append({
                "kind": "ingress",
                "graha": g,
                "date": ing["date"],
                "day": ing["day"],
                "label": "%s moves %s %s" % (g, ing["direction"], ing["to_sign"]),
                "house": house,
                "from_moon": from_moon,
                "retrograde": ing["retrograde"],
                "note": _transit_note(natal, g, house, from_moon),
                "phala": phala.transit_phala(g, house),
                "duration": phala.TRANSIT_DURATION.get(g, ""),
                "slow": g in phala.SLOW,
            })
        for st in station_dates(g, when, count=2,
                                ayanamsa=natal.birth.ayanamsa, tz=tz):
            events.append({
                "kind": "station",
                "graha": g,
                "date": st["date"],
                "day": st["day"],
                "label": "%s %s in %s" % (g, st["event"], st["sign"]),
                "note": "A station is where a graha's effect is strongest. "
                        "Matters ruled by %s stall or restart around this "
                        "date." % g,
            })
    events.sort(key=lambda e: e["date"])
    return events


def transit_report(natal: Chart, when: datetime = None) -> dict:
    tz = natal.birth.resolve_tz()
    when = when or datetime.now(ZoneInfo(tz))
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(tz))
    return {
        "moment": when.isoformat(),
        "moment_label": when.strftime("%d %b %Y, %H:%M"),
        "timezone": tz,
        "positions": current_positions(when, natal),
        "sade_sati": sade_sati_window(natal, when),
        "upcoming": upcoming(natal, when),
    }
