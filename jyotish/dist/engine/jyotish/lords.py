"""
House lord analysis. The main reading surface.

For every house this answers four questions in order:
  1. Which sign falls on it, and therefore who rules it.
  2. Where that ruler actually sits, and in what condition.
  3. What the tradition says about that lord in that house.
  4. What modifies the reading here: dignity, combustion, aspect, dispositor.

Nothing is asserted without the chain of reasoning that produced it.
"""

from __future__ import annotations

from . import interpret, phala
from .engine import (
    DUSTHANA, KENDRA, MARAKA, NATURAL_BENEFIC, NATURAL_MALEFIC, SIGNS,
    TRIKONA, UPACHAYA, Chart, aspecting_grahas, full_dignity, graha_strength,
    has_dig_bala, nakshatra_lord, sign_lord,
)
from . import varga


def houses_ruled(chart: Chart, graha: str) -> list[int]:
    """Which houses a graha rules in this chart. Nodes rule nothing."""
    if graha in ("Rahu", "Ketu"):
        return []
    return [h for h in range(1, 13) if sign_lord(chart.sign_of_house(h)) == graha]


def functional_nature(chart: Chart, graha: str) -> dict:
    """What this graha actually does in this chart, given what it rules.

    Natural benefic and malefic labels are close to useless on their own. A
    graha's behaviour is set by its lordships relative to the lagna.
    """
    ruled = houses_ruled(chart, graha)

    if not ruled:
        disp = sign_lord(chart.grahas[graha].sign)
        return {
            "class": "node",
            "label": "Shadow graha",
            "ruled": [],
            "reason": "%s rules no sign. It takes its function from %s, the "
                      "lord of the sign it occupies, and from any graha it sits "
                      "with." % (graha, disp),
        }

    in_kendra = [h for h in ruled if h in KENDRA]
    in_trikona = [h for h in ruled if h in TRIKONA]
    in_dusthana = [h for h in ruled if h in DUSTHANA]
    in_maraka = [h for h in ruled if h in MARAKA]

    # Yogakaraka outranks everything else. The 1st house counts as both an
    # angle and a trine, so it cannot supply both halves on its own: a real
    # yogakaraka needs one of 4, 7, 10 and one of 5, 9.
    strict_kendra = [h for h in ruled if h in (4, 7, 10)]
    strict_trikona = [h for h in ruled if h in (5, 9)]
    if strict_kendra and strict_trikona:
        return {
            "class": "yogakaraka", "label": "Yogakaraka",
            "ruled": ruled,
            "reason": "%s rules the %s and the %s, catching an angle and a "
                      "trine at once. %s" % (
                          graha, _ord(strict_kendra[0]), _ord(strict_trikona[0]),
                          interpret.FUNCTIONAL_RULES["yogakaraka"]),
        }

    if in_trikona:
        # A trikona lordship cancels a simultaneous dusthana lordship.
        note = ""
        if in_dusthana:
            note = (" It also rules the %s, but a trikona lordship outranks a "
                    "dusthana one and the difficulty is largely cancelled." %
                    " and the ".join(_ord(h) for h in in_dusthana))
        return {
            "class": "benefic", "label": "Functional benefic",
            "ruled": ruled,
            "reason": "%s rules the %s, a trine. %s%s" % (
                graha, " and the ".join(_ord(h) for h in in_trikona),
                interpret.FUNCTIONAL_RULES["benefic"], note),
        }

    if in_dusthana:
        return {
            "class": "malefic", "label": "Functional malefic",
            "ruled": ruled,
            "reason": "%s rules the %s. %s" % (
                graha, " and the ".join(_ord(h) for h in in_dusthana),
                interpret.FUNCTIONAL_RULES["malefic"]),
        }

    if in_kendra:
        which = " and the ".join(_ord(h) for h in in_kendra)
        if graha in NATURAL_BENEFIC:
            return {
                "class": "kendra_benefic", "label": "Kendradhipatya dosha",
                "ruled": ruled,
                "reason": "%s is a natural benefic ruling the %s. %s" % (
                    graha, which,
                    interpret.FUNCTIONAL_RULES["kendra_benefic"]),
            }
        if graha in NATURAL_MALEFIC:
            return {
                "class": "kendra_malefic", "label": "Neutralised malefic",
                "ruled": ruled,
                "reason": "%s is a natural malefic ruling the %s. %s" % (
                    graha, which,
                    interpret.FUNCTIONAL_RULES["kendra_malefic"]),
            }

    if in_maraka:
        return {
            "class": "maraka", "label": "Maraka",
            "ruled": ruled,
            "reason": "%s rules the %s. %s" % (
                graha, _ord(in_maraka[0]),
                interpret.FUNCTIONAL_RULES["maraka"]),
        }

    return {
        "class": "neutral", "label": "Neutral",
        "ruled": ruled,
        "reason": "%s rules the %s. %s" % (
            graha, ", ".join(_ord(h) for h in ruled),
            interpret.FUNCTIONAL_RULES["neutral"]),
    }


def _ord(n: int) -> str:
    return "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}.get(
        n if n < 20 else n % 10, "th"))


def sign_effect(chart: Chart, house: int) -> dict:
    """Why the sign on a house changes how that house behaves.

    This is the 'lord in a certain zodiac' question: the same lord in the same
    house reads differently depending on the sign it stands in, because the
    sign sets the tempo and the method.
    """
    lord = sign_lord(chart.sign_of_house(house))
    g = chart.grahas[lord]
    occupied = interpret.SIGNS_INFO[g.sign]
    on_house = interpret.SIGNS_INFO[chart.sign_of_house(house)]
    h = interpret.HOUSES[house - 1]

    return {
        "house_sign": on_house["name"],
        "house_sign_sanskrit": on_house["sanskrit"],
        "house_sign_note": "%s falls on the %s, the house of %s. %s is %s %s, "
                           "and that %s." % (
                               on_house["name"], _ord(house), h["title"].lower(),
                               on_house["name"], on_house["mode"].lower(),
                               on_house["element"].lower(), on_house["effect"]),
        "lord_sign": occupied["name"],
        "lord_sign_note": "Its lord %s stands in %s, %s %s, which %s." % (
            lord, occupied["name"], occupied["mode"].lower(),
            occupied["element"].lower(), occupied["effect"]),
        "element": occupied["element"],
        "mode": occupied["mode"],
        "temperament": occupied["temperament"],
    }


def analyse_house(chart: Chart, house: int) -> dict:
    """The full reading for one house. Everything the UI needs for one card."""
    sign = chart.sign_of_house(house)
    lord = sign_lord(sign)
    lg = chart.grahas[lord]
    h = interpret.HOUSES[house - 1]

    dignity = full_dignity(chart, lord)
    strength = graha_strength(chart, lord)
    nature = functional_nature(chart, lord)

    base = interpret.LORD_IN_HOUSE[house][lg.house]

    # Modifiers, in the order an astrologer would actually check them.
    modifiers = []
    dm = interpret.DIGNITY_MODIFIER.get(dignity["label"])
    if dm:
        modifiers.append({"kind": "dignity", "label": dignity["label"],
                          "text": dm})
    if lg.combust:
        modifiers.append({"kind": "state", "label": "Combust",
                          "text": interpret.STATE_MODIFIER["combust"]})
    if lg.retrograde and lord not in ("Rahu", "Ketu"):
        modifiers.append({"kind": "state", "label": "Retrograde",
                          "text": interpret.STATE_MODIFIER["retrograde"]})
    if lord in varga.vargottama(chart):
        modifiers.append({"kind": "state", "label": "Vargottama",
                          "text": interpret.STATE_MODIFIER["vargottama"]})
    if has_dig_bala(lord, lg.house):
        modifiers.append({"kind": "state", "label": "Dig bala",
                          "text": interpret.STATE_MODIFIER["dig_bala"]})
    if lg.degree_in_sign < 1 or lg.degree_in_sign > 29:
        modifiers.append({"kind": "state", "label": "Sign boundary",
                          "text": interpret.STATE_MODIFIER["sandhi"]})

    # Who else is involved with this house.
    occupants = []
    for g in chart.grahas_in_house(house):
        occupants.append({
            "graha": g.name,
            "sign": SIGNS[g.sign],
            "degree": round(g.degree_in_sign, 2),
            "nakshatra": g.nakshatra_name,
            "pada": g.pada,
            "retrograde": g.retrograde,
            "combust": g.combust,
            "nature": functional_nature(chart, g.name)["label"],
            "note": _occupant_note(chart, g.name, house),
        })

    aspects = []
    for a in aspecting_grahas(chart, house):
        if any(o["graha"] == a["graha"] for o in occupants):
            continue  # a graha does not aspect its own house
        aspects.append({
            "graha": a["graha"],
            "aspect": "%s aspect" % _ord(a["aspect"]),
            "benefic": a["benefic"],
            "note": _aspect_note(chart, a["graha"], a["aspect"], house),
        })

    # A verdict has to be reconstructable from the parts above.
    verdict, verdict_reason = _verdict(chart, house, strength, nature,
                                       occupants, aspects, lg)

    return {
        "house": house,
        "name": h["name"],
        "title": h["title"],
        "theme": h["theme"],
        "keywords": h["keywords"],
        "category": h["category"],
        "kind": h["kind"],
        "sign": SIGNS[sign],
        "sign_index": sign,
        "sign_sanskrit": interpret.SIGNS_INFO[sign]["sanskrit"],
        "lord": lord,
        "lord_house": lg.house,
        "lord_sign": SIGNS[lg.sign],
        "lord_degree": round(lg.degree_in_sign, 2),
        "lord_nakshatra": lg.nakshatra_name,
        "lord_nakshatra_lord": nakshatra_lord(lg.nakshatra),
        "lord_pada": lg.pada,
        "lord_retrograde": lg.retrograde,
        "lord_combust": lg.combust,
        "dignity": dignity,
        "strength": strength,
        "functional": nature,
        "reading": base,
        "headline": "Lord of the %s in the %s" % (_ord(house), _ord(lg.house)),
        "modifiers": modifiers,
        "occupants": occupants,
        "aspects": aspects,
        "sign_effect": sign_effect(chart, house),
        "verdict": verdict,
        "verdict_reason": verdict_reason,
    }


def _occupant_note(chart: Chart, graha: str, house: int) -> str:
    nature = functional_nature(chart, graha)
    ruled = nature["ruled"]
    if ruled:
        carry = ("It also carries the %s into this house." %
                 " and ".join(_ord(r) for r in ruled))
    else:
        carry = "It carries no house here, only its own nature."
    return "%s %s" % (phala.graha_in_house(graha, house), carry)


def _aspect_note(chart: Chart, graha: str, distance: int, house: int) -> str:
    nature = functional_nature(chart, graha)
    g = chart.grahas[graha]
    h = interpret.HOUSES[house - 1]
    kind = ("supports" if nature["class"] in ("yogakaraka", "benefic",
                                              "kendra_malefic")
            else "pressures" if nature["class"] in ("malefic", "maraka")
            else "touches")
    return "%s throws its %s aspect from the %s onto the %s, which %s %s." % (
        graha, _ord(distance), _ord(g.house), _ord(house), kind,
        h["title"].lower())


def _verdict(chart, house, strength, nature, occupants, aspects, lg):
    """A single-word verdict plus the arithmetic that produced it."""
    points = 0.0
    lines = []

    s = strength["score"]
    points += (s - 50) / 10
    lines.append("Lord strength %.0f of 100 (%s)." % (s, strength["band"]))

    if nature["class"] in ("yogakaraka", "benefic"):
        points += 2
        lines.append("The lord is a functional benefic, which supports the house.")
    elif nature["class"] == "malefic":
        points -= 1.5
        lines.append("The lord also rules a dusthana, which drags on the house.")

    if lg.house in DUSTHANA:
        points -= 2
        lines.append("The lord has fallen into the %s, a dusthana. Houses whose "
                     "lords sit in 6, 8 or 12 deliver late and partially." %
                     _ord(lg.house))
    elif lg.house in TRIKONA:
        points += 1.5
        lines.append("The lord sits in a trine, which is supportive ground.")
    elif lg.house in KENDRA:
        points += 1
        lines.append("The lord sits in an angle, so the matter is active in the "
                     "visible life.")
    elif lg.house in UPACHAYA:
        points += 0.5
        lines.append("The lord sits in an upachaya, so this improves with age.")

    ben = sum(1 for o in occupants if o["graha"] in NATURAL_BENEFIC
              and not o["combust"])
    mal = sum(1 for o in occupants if o["graha"] in NATURAL_MALEFIC)
    if ben:
        points += ben
        lines.append("%d natural benefic%s occupying the house." %
                     (ben, "" if ben == 1 else "s"))
    if mal:
        points -= mal * 0.75
        lines.append("%d natural malefic%s occupying the house." %
                     (mal, "" if mal == 1 else "s"))

    jup = [a for a in aspects if a["graha"] == "Jupiter"]
    if jup:
        points += 1.5
        lines.append("Jupiter aspects the house, which is the single most "
                     "protective influence available.")
    sat = [a for a in aspects if a["graha"] == "Saturn"]
    if sat:
        points -= 0.75
        lines.append("Saturn aspects the house, which delays it and then makes "
                     "it durable.")

    verdict = ("Very strong" if points >= 5 else "Strong" if points >= 2.5
               else "Mixed" if points >= -1 else "Under pressure"
               if points >= -3.5 else "Weak")
    return verdict, lines


def all_houses(chart: Chart) -> list[dict]:
    return [analyse_house(chart, h) for h in range(1, 13)]


def lord_map(chart: Chart) -> list[dict]:
    """The compact 'where is every house lord right now' table.

    This is the first thing to look at on any chart: twelve rows, each saying
    who rules what and where they have gone.
    """
    rows = []
    for h in range(1, 13):
        sign = chart.sign_of_house(h)
        lord = sign_lord(sign)
        lg = chart.grahas[lord]
        nature = functional_nature(chart, lord)
        rows.append({
            "house": h,
            "sign": SIGNS[sign],
            "lord": lord,
            "sits_in_house": lg.house,
            "sits_in_sign": SIGNS[lg.sign],
            "degree": round(lg.degree_in_sign, 2),
            "nakshatra": lg.nakshatra_name,
            "dignity": full_dignity(chart, lord)["label"],
            "strength": graha_strength(chart, lord)["score"],
            "functional": nature["label"],
            "functional_class": nature["class"],
            "retrograde": lg.retrograde,
            "combust": lg.combust,
            "also_rules": [r for r in nature["ruled"] if r != h],
            "summary": "%s lord %s in the %s (%s)" % (
                _ord(h), lord, _ord(lg.house), SIGNS[lg.sign]),
        })
    return rows


def graha_report(chart: Chart, name: str) -> dict:
    """Everything about one graha, assembled for a detail panel."""
    g = chart.grahas[name]
    info = interpret.GRAHAS_INFO[name]
    nature = functional_nature(chart, name)
    dignity = full_dignity(chart, name)
    strength = graha_strength(chart, name)
    h = interpret.HOUSES[g.house - 1]
    sign_info = interpret.SIGNS_INFO[g.sign]

    # Three separate readings, because they answer three different questions:
    # what the graha does where it sits, what the sign does to its method, and
    # what it delivers for the houses it rules.
    readings = []
    for ruled in nature["ruled"]:
        readings.append({
            "rules": ruled,
            "headline": "Lord of the %s in the %s" % (_ord(ruled), _ord(g.house)),
            "text": interpret.LORD_IN_HOUSE[ruled][g.house],
        })

    if not readings:
        disp = sign_lord(g.sign)
        dg = chart.grahas[disp]
        readings.append({
            "rules": None,
            "headline": "%s delivers through its dispositor" % name,
            "text": "%s rules no sign, so it has no house to deliver. It works "
                    "through %s, the lord of %s, which sits in the %s, and "
                    "through whatever graha it shares a house with." % (
                        name, disp, SIGNS[g.sign], _ord(dg.house)),
        })

    return {
        "name": name,
        "sanskrit": info["sanskrit"],
        "longitude": round(g.longitude, 4),
        "sign": SIGNS[g.sign],
        "sign_sanskrit": sign_info["sanskrit"],
        "degree": round(g.degree_in_sign, 4),
        "house": g.house,
        "house_title": h["title"],
        "nakshatra": g.nakshatra_name,
        "nakshatra_lord": nakshatra_lord(g.nakshatra),
        "pada": g.pada,
        "speed": round(g.speed, 4),
        "retrograde": g.retrograde,
        "combust": g.combust,
        "dignity": dignity,
        "strength": strength,
        "functional": nature,
        "karaka": info["karaka"],
        "signifies": info["signifies"],
        "behaviour": info["behaviour"],
        "in_house": phala.graha_in_house(name, g.house),
        "in_sign": phala.graha_in_sign(name, g.sign),
        "in_house_headline": "%s in the %s house" % (name, _ord(g.house)),
        "in_sign_headline": "%s in %s" % (name, SIGNS[g.sign]),
        "natural": info["nature"],
        "gem": info["gem"],
        "day": info["day"],
        "readings": readings,
        "aspects_houses": chart.aspects_from(name),
        "vargottama": name in varga.vargottama(chart),
        "dispositor": sign_lord(g.sign),
        "dispositor_house": chart.grahas[sign_lord(g.sign)].house,
    }
