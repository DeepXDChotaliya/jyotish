"""
Plain language. What is happening now, why, and what changes next.

Three sources have to be combined before any of this means anything, and they
are combined in a fixed order because that is how the tradition reasons:

  1. The natal chart says what is possible. A house that is structurally weak
     cannot be made strong by a good transit.
  2. The dasha says what is active. A house is only delivering results while
     some period lord connected to it is running.
  3. The transit says when, within that, it actually lands.

Saturn crossing your 10th house does nothing much if no period lord touches
your 10th. The same transit during the dasha of your 10th lord is the year the
career changes. Everything in this module is that rule applied.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import dasha, gochar, interpret, phala
from .engine import (
    DUSTHANA, KENDRA, NAKSHATRAS, NATURAL_BENEFIC, SIGNS, TRIKONA, Chart,
    graha_strength, sign_lord,
)
from .lords import _ord, analyse_house, functional_nature, houses_ruled

# Houses in language a person can act on.
HOUSE_PLAIN = {
    1: "your body, energy and how you come across",
    2: "money you have put aside, family and what you say",
    3: "your own effort, siblings and short trips",
    4: "home, your mother, property and peace of mind",
    5: "children, creative work, study and romance",
    6: "work routine, health, debts and people who oppose you",
    7: "marriage, business partners and anyone you deal with openly",
    8: "sudden change, joint money, inheritance and what stays hidden",
    9: "luck, your father, belief, teachers and long journeys",
    10: "career, standing and the people above you",
    11: "income, gains, friends and what you are aiming at",
    12: "expenses, foreign matters, sleep and letting go",
}

# The life areas a person actually asks about, and the houses behind each.
AREAS = [
    {"key": "body", "name": "Body and energy", "houses": [1, 6, 8],
     "plain": "physical health, stamina and how well you are holding up"},
    {"key": "money", "name": "Money and security", "houses": [2, 11],
     "plain": "income, savings and whether money stays once it arrives"},
    {"key": "work", "name": "Work and standing", "houses": [10, 6],
     "plain": "career, reputation and your position at work"},
    {"key": "home", "name": "Home and family", "houses": [4, 2],
     "plain": "the house, the family and whether home feels restful"},
    {"key": "partner", "name": "Marriage and partnership", "houses": [7],
     "plain": "the marriage, the business partner, and close dealings"},
    {"key": "children", "name": "Children and creativity", "houses": [5],
     "plain": "children, creative output, study and romance"},
    {"key": "mind", "name": "Mind and inner peace", "houses": [4, 12],
     "plain": "mental steadiness, sleep and how settled you feel"},
    {"key": "meaning", "name": "Belief, learning and travel", "houses": [9, 12],
     "plain": "faith, teachers, higher study and long journeys"},
]

VERDICT_SCORE = {"Very strong": 2.0, "Strong": 1.0, "Mixed": 0.0,
                 "Under pressure": -1.0, "Weak": -2.0}


def _now(chart: Chart, when: datetime = None) -> datetime:
    tz = chart.birth.resolve_tz()
    when = when or datetime.now(ZoneInfo(tz))
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(tz))
    return when


def _touches(chart: Chart, graha: str, houses: list) -> list:
    """How a graha connects to a set of houses: rules, sits in, or aspects."""
    hits = []
    ruled = houses_ruled(chart, graha)
    g = chart.grahas[graha]
    for h in houses:
        if h in ruled:
            hits.append(("rules", h))
        if g.house == h:
            hits.append(("sits in", h))
        if h in chart.aspects_from(graha):
            hits.append(("aspects", h))
    return hits


def life_areas(chart: Chart, when: datetime = None) -> list:
    """Every area of life with a current status and the reason for it."""
    when = _now(chart, when)
    chain = dasha.running_chain(chart, when, depth=3)
    transits = gochar.current_positions(when, chart)
    houses = {h: analyse_house(chart, h) for h in range(1, 13)}
    slow = {p["graha"]: p for p in transits
            if p["graha"] in ("Saturn", "Jupiter", "Rahu", "Ketu")}

    out = []
    for area in AREAS:
        hs = area["houses"]
        natal = sum(VERDICT_SCORE.get(houses[h]["verdict"], 0)
                    for h in hs) / len(hs)

        reasons, dasha_hits, transit_hits = [], [], []

        # Natal baseline.
        for h in hs:
            info = houses[h]
            reasons.append(
                "Natally, your %s house (%s) reads as %s. Its lord %s sits in "
                "the %s at %d out of 100 strength." % (
                    _ord(h), HOUSE_PLAIN[h], info["verdict"].lower(),
                    info["lord"], _ord(info["lord_house"]),
                    round(info["strength"]["score"])))

        # Is any running period lord connected to this area?
        dscore = 0.0
        for level in chain:
            lord = level["lord"]
            hits = _touches(chart, lord, hs)
            if not hits:
                continue
            strength = graha_strength(chart, lord)["score"]
            nature = functional_nature(chart, lord)
            weight = {1: 1.0, 2: 0.7, 3: 0.4}.get(level["level"], 0.3)
            direction = 1 if nature["class"] in (
                "yogakaraka", "benefic", "kendra_malefic") else \
                -1 if nature["class"] in ("malefic", "maraka") else 0
            dscore += weight * direction * ((strength - 50) / 25 + direction * 0.5)
            verb = ", ".join("%s your %s" % (k, _ord(h)) for k, h in hits[:2])
            dasha_hits.append({
                "lord": lord, "level": level["level_name"],
                "until": level["end_date"],
                "text": "Your %s lord is %s, which %s. That is why this area is "
                        "live right now rather than dormant. It runs until %s." % (
                            level["level_name"].lower(), lord, verb,
                            level["end_date"])})

        # Which slow transits are crossing this area's houses?
        tscore = 0.0
        for gname, p in slow.items():
            if p["house"] not in hs:
                continue
            ph = phala.transit_phala(gname, p["house"])
            good = gname == "Jupiter" and p["house"] not in (6, 8, 12)
            hard = gname in ("Saturn", "Rahu", "Ketu") and p["house"] in (1, 4, 7, 8, 12)
            tscore += 1.0 if good else -1.0 if hard else -0.2
            transit_hits.append({
                "graha": gname, "house": p["house"], "sign": p["sign"],
                "area": ph.get("area", ""), "what": ph.get("what", ""),
                "watch": ph.get("watch", ""), "helps": ph.get("helps", ""),
                "duration": phala.TRANSIT_DURATION.get(gname, "")})

        total = natal + dscore + tscore
        status = ("Going well" if total >= 1.5 else
                  "Steady" if total >= 0.2 else
                  "Mixed" if total >= -0.8 else
                  "Under strain" if total >= -2.2 else "Difficult")

        out.append({
            "key": area["key"], "name": area["name"], "plain": area["plain"],
            "houses": hs, "status": status,
            "score": round(total, 2),
            "natal_score": round(natal, 2),
            "dasha_score": round(dscore, 2),
            "transit_score": round(tscore, 2),
            "reasons": reasons,
            "dasha": dasha_hits,
            "transits": transit_hits,
            "headline": _area_headline(area, status, dasha_hits, transit_hits),
        })

    out.sort(key=lambda a: a["score"])
    return out


def _area_headline(area, status, dasha_hits, transit_hits) -> str:
    if status in ("Under strain", "Difficult"):
        if transit_hits:
            t = transit_hits[0]
            return ("%s is under pressure, and the immediate cause is %s "
                    "crossing this part of the chart. %s" % (
                        area["name"], t["graha"], t["watch"]))
        if dasha_hits:
            return ("%s is under pressure because the period now running is "
                    "tied to it. %s" % (area["name"], dasha_hits[0]["text"]))
        return ("%s is structurally weak in this chart. Nothing is currently "
                "making it worse, but it will not carry much load." % area["name"])
    if status == "Going well":
        if transit_hits:
            return ("%s is well supported. %s" % (
                area["name"], transit_hits[0]["what"]))
        return ("%s is well supported both natally and by the period now "
                "running." % area["name"])
    if dasha_hits:
        return ("%s is active. %s" % (area["name"], dasha_hits[0]["text"]))
    return ("%s is quiet at the moment. No period lord is connected to it and "
            "no slow transit is crossing it, so expect little movement either "
            "way." % area["name"])


def current_situation(chart: Chart, when: datetime = None) -> dict:
    """What the running dasha is actually doing, in plain words."""
    when = _now(chart, when)
    chain = dasha.running_chain(chart, when, depth=4)
    if not chain:
        return {"text": "No dasha is running at this date.", "levels": []}

    paras, levels = [], []
    for level in chain[:3]:
        lord = level["lord"]
        g = chart.grahas[lord]
        ruled = houses_ruled(chart, lord)
        nature = functional_nature(chart, lord)
        strength = graha_strength(chart, lord)
        info = interpret.GRAHAS_INFO[lord]

        if ruled:
            owns = " and ".join("your %s house (%s)" % (_ord(h), HOUSE_PLAIN[h])
                                for h in ruled)
            what = ("In your chart %s owns %s, and it sits in your %s house. "
                    "So while it runs, %s the parts of life that move." % (
                        lord, owns, _ord(g.house),
                        "those are" if len(ruled) > 1 else "that is"))
        else:
            disp = sign_lord(g.sign)
            what = ("%s owns nothing in your chart. It works through %s, the "
                    "lord of the sign it sits in, and it amplifies whatever "
                    "house it occupies, which for you is the %s: %s." % (
                        lord, disp, _ord(g.house), HOUSE_PLAIN[g.house]))

        tone = ("This is one of the better periods in your chart."
                if nature["class"] in ("yogakaraka", "benefic") and strength["score"] >= 55
                else "This period carries difficulty. It is not a punishment, "
                     "it is the part of the cycle where these matters get "
                     "worked through."
                if nature["class"] in ("malefic", "maraka") or strength["score"] < 40
                else "This is a mixed period. Some of it delivers and some of "
                     "it grinds.")

        paras.append("%s %s %s %s" % (
            "%s (%s), %s of it done, ending %s." % (
                level["level_name"], lord, "%d%%" % level["percent"],
                level["end_date"]),
            what, tone,
            "%s is at %d out of 100 strength here, which is %s." % (
                lord, round(strength["score"]), strength["band"].lower())))

        levels.append({
            "level": level["level"], "level_name": level["level_name"],
            "lord": lord, "percent": level["percent"],
            "start": level["start_date"], "end": level["end_date"],
            "remaining": level["remaining"],
            "rules": ruled,
            "rules_plain": [HOUSE_PLAIN[h] for h in ruled],
            "sits_in": g.house,
            "sits_in_plain": HOUSE_PLAIN[g.house],
            "sign": SIGNS[g.sign],
            "strength": strength["score"], "band": strength["band"],
            "functional": nature["label"],
            "karaka": info["karaka"],
            "text": what, "tone": tone,
        })

    interaction = dasha.dasha_reading(chart, [c["lord"] for c in chain])
    return {
        "text": " ".join(paras),
        "levels": levels,
        "interaction": interaction["interaction"],
        "chain": chain,
    }


def whats_next(chart: Chart, when: datetime = None, count: int = 6) -> list:
    """Upcoming period changes, and what each one shifts.

    Antardasha changes are the ones a person actually feels, so those are what
    this returns rather than the mahadasha changes that arrive once a decade.
    """
    when = _now(chart, when)
    chain = dasha.running_chain(chart, when, depth=2)
    if len(chain) < 2:
        return []

    maha = chain[0]["lord"]
    events = []

    # Walk forward through antardashas, crossing into the next mahadasha when
    # the current one runs out. Children are computed from the period itself
    # rather than by lord name, because the same lord recurs across cycles.
    mahas = dasha.level_periods(chart, [])
    maha_index = next((i for i, p in enumerate(mahas)
                       if p["lord"] == maha), 0)

    while len(events) < count and maha_index < len(mahas):
        current_maha = mahas[maha_index]
        for s in dasha._children(current_maha, 2):
            if s["start"] <= when:
                continue          # already started or finished
            events.append(_change_event(chart, current_maha["lord"], s))
            if len(events) >= count:
                break
        maha_index += 1
    return events


def _change_event(chart: Chart, maha: str, sub: dict) -> dict:
    lord = sub["lord"]
    g = chart.grahas[lord]
    ruled = houses_ruled(chart, lord)
    nature = functional_nature(chart, lord)
    strength = graha_strength(chart, lord)
    end = sub["start"] + timedelta(days=sub["days"])

    if ruled:
        shifts = ("Attention moves to %s, because %s owns %s in your chart." % (
            "; and to ".join(HOUSE_PLAIN[h] for h in ruled), lord,
            " and ".join("the %s" % _ord(h) for h in ruled)))
    else:
        shifts = ("%s owns no house, so it amplifies wherever it sits, which "
                  "for you is %s." % (lord, HOUSE_PLAIN[g.house]))

    distance = ((g.house - chart.grahas[maha].house) % 12) + 1
    if lord == maha:
        tone, tone_text = "concentrated", (
            "%s runs inside its own mahadasha. Whatever %s means in your chart "
            "arrives undiluted here, for better and for worse." % (lord, lord))
    elif distance in (6, 8, 12):
        tone, tone_text = "difficult", (
            "%s sits in the %s from %s, which is the classical marker of a "
            "hard sub-period. Expect the two agendas to work against each "
            "other." % (lord, _ord(distance), maha))
    elif distance in (1, 5, 9):
        tone, tone_text = "supportive", (
            "%s sits in the %s from %s, a trinal relationship, so the two "
            "lords cooperate and this period tends to deliver." % (
                lord, _ord(distance), maha))
    elif distance in (4, 7, 10):
        tone, tone_text = "active", (
            "%s sits in the %s from %s, an angular relationship, so events "
            "here are external and visible rather than internal." % (
                lord, _ord(distance), maha))
    else:
        tone, tone_text = "neutral", (
            "%s sits in the %s from %s, so neither lord dominates." % (
                lord, _ord(distance), maha))

    return {
        "maha": maha, "lord": lord,
        "start": sub["start"].strftime("%d %b %Y"),
        "end": end.strftime("%d %b %Y"),
        "start_iso": sub["start"].isoformat(),
        "duration": dasha._duration(sub["days"]),
        "label": "%s / %s" % (maha, lord),
        "rules": ruled,
        "sits_in": g.house,
        "strength": strength["score"],
        "band": strength["band"],
        "functional": nature["label"],
        "tone": tone,
        "shifts": shifts,
        "tone_text": tone_text,
        "delivers": [interpret.LORD_IN_HOUSE[h][g.house] for h in ruled],
    }


# ---------------------------------------------------------------------------
# Sade Sati, told properly
# ---------------------------------------------------------------------------

SADE_SATI_PHASES = {
    11: {
        "name": "First phase, Saturn in the 12th from your Moon",
        "plain": "The opening two and a half years.",
        "what": "This phase works on expense, sleep and whatever you have been "
                "carrying past its time. Costs rise, often for legitimate "
                "reasons: medical, family, education, travel. Sleep gets worse "
                "before it gets better. Things you should have let go of start "
                "falling away whether or not you agree.",
        "watch": "Money leaving faster than it arrives, insomnia, isolation, "
                 "and a sense of quiet loss with nothing dramatic to point at.",
        "helps": "Cut discretionary spending now rather than in the middle "
                 "phase. Fix your sleep deliberately. Let go of the "
                 "commitments you already know are finished.",
    },
    0: {
        "name": "Second phase, Saturn over your natal Moon",
        "plain": "The middle two and a half years, and the hardest of the three.",
        "what": "Saturn sits directly on the Moon, which is the mind. This is "
                "where the reorganisation actually happens. Mood is heavy, "
                "energy is low, and the things that were structurally wrong in "
                "your life become impossible to ignore. It is also where the "
                "real rebuilding gets done, though that is only visible "
                "afterwards.",
        "watch": "Low mood that does not lift, exhaustion, withdrawal from "
                 "people, and decisions made from a flat emotional state that "
                 "look wrong two years later.",
        "helps": "Keep a fixed daily structure even when it feels pointless: "
                 "sleep, food and exercise at set times. Do not make "
                 "irreversible decisions about marriage, home or career from "
                 "inside this phase. Tell someone what is going on.",
    },
    1: {
        "name": "Third phase, Saturn in the 2nd from your Moon",
        "plain": "The closing two and a half years.",
        "what": "Pressure moves off the mind and onto resources: money, "
                "family and speech. Finances need restructuring rather than "
                "rescue. Family obligations surface. What you say and do not "
                "say starts to matter more than usual. The weight lifts "
                "steadily through this phase.",
        "watch": "Money worries, friction with family over money, and speech "
                 "that has become blunt or bitter from the previous five years.",
        "helps": "Restructure debt rather than servicing it. Say the "
                 "reconciling thing to family. Watch the tone you have picked "
                 "up; it outlasts the transit if you let it.",
    },
}


def sade_sati(chart: Chart, when: datetime = None) -> dict:
    """The full seven and a half years, with all three phases dated."""
    when = _now(chart, when)
    base = gochar.sade_sati_window(chart, when)
    moon_sign = chart.grahas["Moon"].sign
    tz = chart.birth.resolve_tz()

    phases = []
    for offset in (11, 0, 1):
        sign = (moon_sign + offset) % 12
        start = gochar._first_entry_into(
            sign, "Saturn", when - timedelta(days=3600), tz)
        meta = SADE_SATI_PHASES[offset]
        phases.append({
            "offset": offset,
            "sign": SIGNS[sign],
            "start": start,
            "active": base.get("offset") == offset,
            **meta,
        })

    out = dict(base)
    out["phases"] = phases
    out["moon_nakshatra"] = chart.grahas["Moon"].nakshatra_name

    if base["active"]:
        meta = SADE_SATI_PHASES[base["offset"]]
        out["plain"] = (
            "You are in Sade Sati, the seven and a half years Saturn spends "
            "crossing the three signs around your natal Moon. Your Moon is in "
            "%s, so the cycle runs from Saturn entering %s to Saturn leaving "
            "%s. You are in the %s: %s" % (
                SIGNS[moon_sign], SIGNS[(moon_sign + 11) % 12],
                SIGNS[(moon_sign + 1) % 12],
                meta["name"].split(",")[0].lower(),
                meta["plain"][:1].lower() + meta["plain"][1:]))
    else:
        out["plain"] = (
            "You are not in Sade Sati. Your natal Moon is in %s and Saturn is "
            "currently in %s, which is not one of the three signs that count. "
            "%s" % (SIGNS[moon_sign], base["saturn_sign"],
                    "The next cycle opens %s." % base["window_start"]
                    if base.get("window_start") else ""))

    if base.get("ashtama"):
        out["extra"] = ("Saturn is transiting the 8th from your natal Moon, "
                        "which the tradition calls Ashtama Shani. It is short "
                        "compared with Sade Sati and often harder while it "
                        "runs: sudden obstruction, low energy and matters that "
                        "were buried resurfacing.")
    elif base.get("kantaka"):
        out["extra"] = ("Saturn is in the 4th or 10th from your natal Moon, "
                        "which the tradition calls Kantaka or Ardha Ashtama "
                        "Shani. Home and career come under pressure at the "
                        "same time, which is what makes it wearing.")
    return out


def brief(chart: Chart, when: datetime = None) -> dict:
    """Everything the plain-language view needs, in one call."""
    when = _now(chart, when)
    return {
        "moment": when.isoformat(),
        "moment_label": when.strftime("%d %B %Y"),
        "headlines": headlines(chart, when),
        "now": current_situation(chart, when),
        "areas": life_areas(chart, when),
        "next": whats_next(chart, when),
        "sade_sati": sade_sati(chart, when),
    }


# ---------------------------------------------------------------------------
# Headlines. The half dozen things worth knowing before anything else.
#
# Ranked so the page can be read top down and stopped at any point without
# missing something more important further down. Every headline carries its
# own evidence line, so nothing here is an assertion you cannot check.
# ---------------------------------------------------------------------------

HEADLINE_KINDS = {
    "core": "who this is",
    "strength": "what is working",
    "pressure": "what is under strain",
    "now": "what is running",
    "prediction": "what is coming",
    "work": "what to work on",
}


def headlines(chart: Chart, when: datetime = None, limit: int = 7) -> list:
    """The main findings, ranked, each with the evidence that produced it."""
    from . import character, nakshatra, psyche, yogas

    when = _now(chart, when)
    out = []

    # Who this is: lagna plus the Moon's nakshatra, which is the real person.
    janma = chart.grahas["Moon"].nakshatra
    moon_n = nakshatra.data(janma)
    lagna_lord = sign_lord(chart.lagna_sign)
    out.append({
        "kind": "core", "rank": 0,
        "title": "%s lagna, Moon in %s" % (
            SIGNS[chart.lagna_sign], NAKSHATRAS[janma]),
        "text": "%s %s" % (moon_n["drive"], moon_n["gift"]),
        "evidence": "Lagna %s ruled by %s in the %s. Moon at %.2f degrees %s, "
                    "%s pada %d, lord %s." % (
                        SIGNS[chart.lagna_sign], lagna_lord,
                        _ord(chart.grahas[lagna_lord].house),
                        chart.grahas["Moon"].degree_in_sign,
                        SIGNS[chart.grahas["Moon"].sign],
                        NAKSHATRAS[janma], chart.grahas["Moon"].pada,
                        moon_n["lord"]),
    })

    # The strongest supportive combination in the chart.
    ys = [y for y in yogas.all_yogas(chart)
          if y["kind"] in ("mahapurusha", "raja", "dhana", "viparita")]
    if ys:
        best = max(ys, key=lambda y: y["strength"])
        out.append({
            "kind": "strength", "rank": 1,
            "title": best["name"],
            "text": best["effect"],
            "evidence": best["reason"],
        })

    # The area of life currently under most strain.
    areas = life_areas(chart, when)
    worst = areas[0]
    if worst["score"] < 0.2:
        out.append({
            "kind": "pressure", "rank": 2,
            "title": "%s is %s" % (worst["name"], worst["status"].lower()),
            "text": worst["headline"],
            "evidence": " ".join(worst["reasons"]),
        })

    # What the running period is doing.
    chain = dasha.running_chain(chart, when, depth=2)
    if chain:
        maha, antar = chain[0], (chain[1] if len(chain) > 1 else chain[0])
        ruled = houses_ruled(chart, maha["lord"])
        out.append({
            "kind": "now", "rank": 3,
            "title": "%s / %s until %s" % (
                maha["lord"], antar["lord"], antar["end_date"]),
            "text": "%s runs the whole period to %s. %s" % (
                maha["lord"], maha["end_date"],
                "It owns %s, so that is what moves." % (
                    "; and ".join(HOUSE_PLAIN[h] for h in ruled))
                if ruled else
                "It owns no house, so it amplifies the %s where it sits." %
                _ord(chart.grahas[maha["lord"]].house)),
            "evidence": "%s mahadasha %s to %s, %d%% elapsed. %s antardasha "
                        "%s to %s." % (
                            maha["lord"], maha["start_date"], maha["end_date"],
                            maha["percent"], antar["lord"],
                            antar["start_date"], antar["end_date"]),
        })

    # Sade Sati, if it is running or close.
    ss = sade_sati(chart, when)
    if ss["active"]:
        out.append({
            "kind": "prediction", "rank": 4,
            "title": "Sade Sati, %s, until %s" % (
                ss["phase"].lower(), ss.get("window_end", "")),
            "text": ss["plain"],
            "evidence": "Natal Moon in %s. Saturn in %s. Cycle %s to %s." % (
                ss["moon_sign"], ss["saturn_sign"],
                ss.get("window_start", "?"), ss.get("window_end", "?")),
        })

    # The next period change.
    nxt = whats_next(chart, when, count=1)
    if nxt:
        e = nxt[0]
        out.append({
            "kind": "prediction", "rank": 5,
            "title": "From %s: %s" % (e["start"], e["label"]),
            "text": "%s %s" % (e["shifts"], e["tone_text"]),
            "evidence": "%s to %s, %s. %s is %s here at %d out of 100." % (
                e["start"], e["end"], e["duration"], e["lord"],
                e["functional"].lower(), round(e["strength"])),
        })

    # The single most actionable piece of character work.
    edges = character.growth_edges(chart)
    if edges:
        top = edges[0]
        out.append({
            "kind": "work", "rank": 6,
            "title": "Work on %s" % top["trait"],
            "text": top["work"],
            "evidence": " ".join(l["text"] for l in top["links"]),
        })

    out.sort(key=lambda h: h["rank"])
    return out[:limit]
