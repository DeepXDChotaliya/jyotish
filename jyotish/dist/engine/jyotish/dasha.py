"""
Vimshottari dasha. Seeded off the Moon's nakshatra and the unexpired portion
of that nakshatra at birth.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .engine import Chart

# Order matters. This cycle repeats every 9 nakshatras.
VIMSHOTTARI = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
    ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17),
]

TOTAL_YEARS = 120
YEAR_DAYS = 365.2425  # tropical year, the usual convention


@dataclass
class DashaPeriod:
    lord: str
    start: datetime
    end: datetime
    level: int  # 1 = maha, 2 = antar, 3 = pratyantar
    children: list["DashaPeriod"] = field(default_factory=list)

    @property
    def label(self) -> str:
        return {1: "Mahadasha", 2: "Antardasha", 3: "Pratyantardasha"}[self.level]

    def contains(self, when: datetime) -> bool:
        return self.start <= when < self.end


def _birth_datetime(chart: Chart) -> datetime:
    from zoneinfo import ZoneInfo
    b = chart.birth
    return datetime(b.year, b.month, b.day, b.hour, b.minute, b.second,
                    tzinfo=ZoneInfo(b.resolve_tz()))


def _subdivide(lord: str, start: datetime, span_days: float,
               level: int, max_level: int) -> list[DashaPeriod]:
    """Split a period into sub-periods, starting from the period's own lord."""
    if level > max_level:
        return []
    idx = [n for n, _ in VIMSHOTTARI].index(lord)
    order = VIMSHOTTARI[idx:] + VIMSHOTTARI[:idx]
    out: list[DashaPeriod] = []
    cursor = start
    for sub_lord, years in order:
        sub_days = span_days * years / TOTAL_YEARS
        end = cursor + timedelta(days=sub_days)
        p = DashaPeriod(lord=sub_lord, start=cursor, end=end, level=level)
        p.children = _subdivide(sub_lord, cursor, sub_days, level + 1, max_level)
        out.append(p)
        cursor = end
    return out


def vimshottari(chart: Chart, max_level: int = 3) -> list[DashaPeriod]:
    """Full dasha tree from birth. Level 3 gives pratyantar."""
    moon = chart.grahas["Moon"]
    span = 360 / 27
    # Fraction of the birth nakshatra already elapsed
    elapsed_fraction = (moon.longitude - moon.nakshatra * span) / span

    start_idx = moon.nakshatra % 9
    lord, years = VIMSHOTTARI[start_idx]

    birth_dt = _birth_datetime(chart)
    # The first mahadasha is a partial one: only the unexpired balance runs.
    balance_days = years * YEAR_DAYS * (1 - elapsed_fraction)
    full_days = years * YEAR_DAYS
    # Back-date the notional start so sub-period maths stays proportional.
    notional_start = birth_dt - timedelta(days=full_days - balance_days)

    periods: list[DashaPeriod] = []
    cursor = notional_start
    order = VIMSHOTTARI[start_idx:] + VIMSHOTTARI[:start_idx]

    # Two full cycles covers 240 years, enough for any lifetime.
    for cycle in range(2):
        for l, y in order:
            days = y * YEAR_DAYS
            end = cursor + timedelta(days=days)
            p = DashaPeriod(lord=l, start=cursor, end=end, level=1)
            p.children = _subdivide(l, cursor, days, 2, max_level)
            periods.append(p)
            cursor = end

    return periods


def current_dasha(chart: Chart, when: datetime | None = None) -> list[DashaPeriod]:
    """Returns the active chain, e.g. [Mahadasha, Antardasha, Pratyantardasha]."""
    from zoneinfo import ZoneInfo
    when = when or datetime.now(ZoneInfo(chart.birth.resolve_tz()))
    chain: list[DashaPeriod] = []
    level = vimshottari(chart)
    while level:
        match = next((p for p in level if p.contains(when)), None)
        if not match:
            break
        chain.append(match)
        level = match.children
    return chain


def balance_at_birth(chart: Chart) -> tuple[str, float]:
    """Dasha lord running at birth and the years remaining of it."""
    moon = chart.grahas["Moon"]
    span = 360 / 27
    elapsed = (moon.longitude - moon.nakshatra * span) / span
    lord, years = VIMSHOTTARI[moon.nakshatra % 9]
    return lord, years * (1 - elapsed)


# ---------------------------------------------------------------------------
# Lazy tree. The full four-level tree is 26,000 periods, which is pointless to
# materialise when a reading only ever looks at one branch. These functions
# compute a single level on demand from (lord, start, span) and let the caller
# walk down.
# ---------------------------------------------------------------------------

LEVEL_NAMES = {1: "Mahadasha", 2: "Antardasha", 3: "Pratyantardasha",
               4: "Sookshma dasha", 5: "Prana dasha"}

# Some lineages use a 360 day savana year instead of the tropical year. The
# difference reaches several months over a long mahadasha, so it is a setting
# rather than a constant.
YEAR_LENGTHS = {"tropical": 365.2425, "savana": 360.0}


def _order_from(lord: str):
    idx = [n for n, _ in VIMSHOTTARI].index(lord)
    return VIMSHOTTARI[idx:] + VIMSHOTTARI[:idx]


def seed(chart: Chart, year_days: float = YEAR_DAYS) -> dict:
    """Where the dasha clock starts. Everything else derives from this."""
    moon = chart.grahas["Moon"]
    span = 360 / 27
    elapsed = (moon.longitude - moon.nakshatra * span) / span
    lord, years = VIMSHOTTARI[moon.nakshatra % 9]
    birth_dt = _birth_datetime(chart)
    balance_days = years * year_days * (1 - elapsed)
    return {
        "lord": lord,
        "nakshatra": moon.nakshatra_name,
        "pada": moon.pada,
        "elapsed_fraction": elapsed,
        "balance_years": years * (1 - elapsed),
        "balance_days": balance_days,
        "full_years": years,
        "birth": birth_dt,
        # Back-dated so every sub-period stays proportional to a full cycle.
        "notional_start": birth_dt - timedelta(days=years * year_days - balance_days),
        "year_days": year_days,
    }


def level_periods(chart: Chart, path: list, year_days: float = YEAR_DAYS) -> list:
    """The periods one level below `path`.

    path == []                -> the mahadashas
    path == ["Venus"]         -> the antardashas inside Venus mahadasha
    path == ["Venus", "Sun"]  -> the pratyantardashas inside Venus/Sun
    """
    s = seed(chart, year_days)
    cursor = s["notional_start"]
    order = _order_from(s["lord"])

    # Level 1 always comes from the seed, and runs two cycles to cover any life.
    periods = []
    for _ in range(2):
        for lord, years in order:
            days = years * year_days
            periods.append({"lord": lord, "start": cursor,
                            "days": days, "level": 1})
            cursor = cursor + timedelta(days=days)

    for depth, want in enumerate(path, start=1):
        match = next((p for p in periods if p["lord"] == want), None)
        if match is None:
            return []
        periods = _children(match, depth + 1)
    return periods


def _children(period: dict, level: int) -> list:
    out = []
    cursor = period["start"]
    for lord, years in _order_from(period["lord"]):
        days = period["days"] * years / TOTAL_YEARS
        out.append({"lord": lord, "start": cursor, "days": days, "level": level})
        cursor = cursor + timedelta(days=days)
    return out


def _as_dict(p: dict) -> dict:
    end = p["start"] + timedelta(days=p["days"])
    return {
        "lord": p["lord"],
        "level": p["level"],
        "level_name": LEVEL_NAMES[p["level"]],
        "start": p["start"].isoformat(),
        "end": end.isoformat(),
        "start_date": p["start"].strftime("%d %b %Y"),
        "end_date": end.strftime("%d %b %Y"),
        "days": round(p["days"], 2),
        "years": round(p["days"] / 365.2425, 3),
        "duration": _duration(p["days"]),
    }


def _duration(days: float) -> str:
    if days < 1:
        return "%d hours" % round(days * 24)
    if days < 60:
        return "%d days" % round(days)
    if days < 400:
        return "%d months" % round(days / 30.44)
    y = days / 365.2425
    whole = int(y)
    months = round((y - whole) * 12)
    if months == 12:
        whole, months = whole + 1, 0
    return "%dy" % whole + (" %dm" % months if months else "")


def periods_json(chart: Chart, path: list = None,
                 year_days: float = YEAR_DAYS) -> list:
    """Serialisable periods one level below path, with dates already formatted."""
    return [_as_dict(p) for p in level_periods(chart, path or [], year_days)]


def running_chain(chart: Chart, when: datetime = None, depth: int = 4,
                  year_days: float = YEAR_DAYS) -> list:
    """The dasha chain active at a moment, with elapsed percentage per level."""
    from zoneinfo import ZoneInfo
    when = when or datetime.now(ZoneInfo(chart.birth.resolve_tz()))
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(chart.birth.resolve_tz()))

    chain = []
    path = []
    for level in range(1, depth + 1):
        periods = level_periods(chart, path, year_days)
        match = None
        for p in periods:
            if p["start"] <= when < p["start"] + timedelta(days=p["days"]):
                match = p
                break
        if match is None:
            break
        d = _as_dict(match)
        elapsed = (when - match["start"]).total_seconds() / 86400
        d["percent"] = round(100 * elapsed / match["days"], 1)
        d["elapsed"] = _duration(elapsed)
        d["remaining"] = _duration(match["days"] - elapsed)
        chain.append(d)
        path = path + [match["lord"]]
    return chain


def timeline(chart: Chart, start: datetime, end: datetime, level: int = 2,
             year_days: float = YEAR_DAYS) -> list:
    """Every period at `level` overlapping a date window, flattened.

    This is the segment view: a straight list of dated bands you can scan for
    a decade at a time without walking the tree by hand.
    """
    out = []

    def walk(path, depth):
        for p in level_periods(chart, path, year_days):
            p_end = p["start"] + timedelta(days=p["days"])
            if p_end < start or p["start"] > end:
                continue
            if depth == level:
                out.append(_as_dict(p))
            else:
                walk(path + [p["lord"]], depth + 1)

    walk([], 1)
    return out


def dasha_reading(chart: Chart, lords_in_chain: list) -> dict:
    """What a dasha chain actually means for this specific chart.

    A dasha lord delivers the houses it rules, from the house it sits in. The
    relationship between the mahadasha lord and the antardasha lord sets the
    tone: an antardasha lord in the 6th, 8th or 12th from the mahadasha lord is
    the classical marker of a difficult sub-period.
    """
    from . import interpret
    from .engine import SIGNS, full_dignity, graha_strength, sign_lord
    from .lords import _ord, functional_nature, houses_ruled

    out = {"levels": [], "interaction": []}

    for i, lord in enumerate(lords_in_chain):
        g = chart.grahas[lord]
        nature = functional_nature(chart, lord)
        ruled = houses_ruled(chart, lord)
        strength = graha_strength(chart, lord)
        dignity = full_dignity(chart, lord)
        info = interpret.GRAHAS_INFO[lord]

        delivers = []
        for h in ruled:
            delivers.append({
                "house": h,
                "title": interpret.HOUSES[h - 1]["title"],
                "text": interpret.LORD_IN_HOUSE[h][g.house],
            })
        if not delivers:
            disp = chart.grahas[sign_lord(g.sign)]
            delivers.append({
                "house": None,
                "title": interpret.HOUSES[g.house - 1]["title"],
                "text": "%s rules nothing, so it delivers the matters of the "
                        "%s where it sits, filtered through its dispositor in "
                        "the %s." % (lord, _ord(g.house), _ord(disp.house)),
            })

        out["levels"].append({
            "level": i + 1,
            "level_name": LEVEL_NAMES[i + 1],
            "lord": lord,
            "sanskrit": info["sanskrit"],
            "house": g.house,
            "sign": SIGNS[g.sign],
            "nakshatra": g.nakshatra_name,
            "rules": ruled,
            "functional": nature["label"],
            "functional_class": nature["class"],
            "functional_reason": nature["reason"],
            "dignity": dignity["label"],
            "dignity_reason": dignity["reason"],
            "strength": strength["score"],
            "band": strength["band"],
            "karaka": info["karaka"],
            "behaviour": info["behaviour"],
            "delivers": delivers,
            "headline": "%s runs the %s from the %s in %s" % (
                lord,
                " and ".join(_ord(h) for h in ruled) if ruled
                else "matters of the %s" % _ord(g.house),
                _ord(g.house), SIGNS[g.sign]),
        })

    for i in range(len(lords_in_chain) - 1):
        a, b = lords_in_chain[i], lords_in_chain[i + 1]
        if a == b:
            out["interaction"].append({
                "pair": [a, b],
                "tone": "concentrated",
                "text": "%s runs inside its own period. Whatever %s means in "
                        "this chart arrives undiluted here." % (b, a),
            })
            continue
        ga, gb = chart.grahas[a], chart.grahas[b]
        distance = ((gb.house - ga.house) % 12) + 1
        if distance in (6, 8, 12):
            tone = "difficult"
            text = ("%s sits in the %s from %s. The classical marker of a hard "
                    "sub-period: the two lords are working against each other, "
                    "and the matters of both are obstructed while it runs." % (
                        b, _ord(distance), a))
        elif distance in (1, 5, 9):
            tone = "supportive"
            text = ("%s sits in the %s from %s, a trinal relationship. The two "
                    "lords cooperate and the period tends to deliver what it "
                    "promises." % (b, _ord(distance), a))
        elif distance in (4, 7, 10):
            tone = "active"
            text = ("%s sits in the %s from %s, an angular relationship. Events "
                    "are visible and external rather than internal." % (
                        b, _ord(distance), a))
        else:
            tone = "neutral"
            text = ("%s sits in the %s from %s. Neither lord dominates; read "
                    "the houses each rules on their own terms." % (
                        b, _ord(distance), a))
        out["interaction"].append({"pair": [a, b], "tone": tone,
                                   "distance": distance, "text": text})

    return out
