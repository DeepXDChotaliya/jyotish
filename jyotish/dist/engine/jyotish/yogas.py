"""
Yoga detection.

Every detector returns the combination it found and the placements that
triggered it, so a claimed yoga can always be checked by eye against the chart
rather than taken on faith. A yoga that is present but formed by weak grahas is
reported as present and weak, not suppressed, because that is how it behaves.
"""

from __future__ import annotations

from .engine import (
    DUSTHANA, EXALTATION, KENDRA, NATURAL_BENEFIC, NATURAL_MALEFIC, OWN_SIGNS,
    SIGNS, TRIKONA, UPACHAYA, Chart, full_dignity, graha_strength, sign_lord,
)
from .lords import _ord, functional_nature, houses_ruled

REAL_GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _house_from(chart: Chart, origin_house: int, target_house: int) -> int:
    """Distance in houses, counted inclusively the Jyotish way."""
    return ((target_house - origin_house) % 12) + 1


def _yoga(name, sanskrit, kind, strength, summary, reason, effect, grahas=None):
    return {
        "name": name,
        "sanskrit": sanskrit,
        "kind": kind,            # raja, dhana, mahapurusha, lunar, dosha, viparita, spiritual
        "strength": strength,    # 0-100
        "summary": summary,
        "reason": reason,        # why it was detected, in chart terms
        "effect": effect,        # what it does
        "grahas": grahas or [],
    }


# ---------------------------------------------------------------------------
# Raja yogas
# ---------------------------------------------------------------------------

def raja_yogas(chart: Chart) -> list[dict]:
    out = []
    kendra_lords = {}
    trikona_lords = {}
    for h in (1, 4, 7, 10):
        kendra_lords.setdefault(sign_lord(chart.sign_of_house(h)), []).append(h)
    for h in (1, 5, 9):
        trikona_lords.setdefault(sign_lord(chart.sign_of_house(h)), []).append(h)

    # A single graha holding both an angle and a trine. The lagna counts as
    # both, so it cannot supply the pair on its own.
    for graha in set(kendra_lords) & set(trikona_lords):
        k = [h for h in kendra_lords[graha] if h != 1]
        t = [h for h in trikona_lords[graha] if h != 1]
        if not k or not t:
            continue
        s = graha_strength(chart, graha)
        out.append(_yoga(
            "Yogakaraka raja yoga", "Yogakaraka", "raja", s["score"],
            "%s rules both an angle and a trine on its own." % graha,
            "%s rules the %s (angle) and the %s (trine). One graha holding "
            "both is the cleanest form of raja yoga: there is nothing to "
            "connect because it is already connected." % (
                graha, _ord(k[0]), _ord(t[0])),
            "Raises the whole life when its dasha runs. %s is currently in the "
            "%s in %s at %s strength." % (
                graha, _ord(chart.grahas[graha].house),
                SIGNS[chart.grahas[graha].sign], s["band"].lower()),
            [graha]))

    # Two different grahas, one angular one trinal, brought into relationship.
    seen = set()
    for kl, khouses in kendra_lords.items():
        for tl, thouses in trikona_lords.items():
            if kl == tl or (min(kl, tl), max(kl, tl)) in seen:
                continue
            kg, tg = chart.grahas[kl], chart.grahas[tl]
            link = None
            if kg.house == tg.house:
                link = "conjunct in the %s" % _ord(kg.house)
            elif tg.house in chart.aspects_from(kl) and kg.house in chart.aspects_from(tl):
                link = "in mutual aspect"
            elif sign_lord(kg.sign) == tl and sign_lord(tg.sign) == kl:
                link = "in exchange of signs"
            if not link:
                continue
            seen.add((min(kl, tl), max(kl, tl)))
            score = (graha_strength(chart, kl)["score"] +
                     graha_strength(chart, tl)["score"]) / 2
            out.append(_yoga(
                "Raja yoga", "Raja yoga", "raja", score,
                "%s and %s, angle lord and trine lord, are %s." % (kl, tl, link),
                "%s rules the %s, an angle. %s rules the %s, a trine. They are "
                "%s, which links the visible structure of the life to its "
                "supporting merit." % (
                    kl, _ord(khouses[0]), tl, _ord(thouses[0]), link),
                "Status, authority and opportunity rise together during the "
                "dasha and antardasha of either graha.",
                [kl, tl]))
    return out


def dhana_yogas(chart: Chart) -> list[dict]:
    """Wealth combinations: the 2nd, 5th, 9th and 11th lords in relationship."""
    out = []
    wealth_houses = [2, 5, 9, 11]
    pairs_seen = set()
    for i, h1 in enumerate(wealth_houses):
        for h2 in wealth_houses[i + 1:]:
            l1 = sign_lord(chart.sign_of_house(h1))
            l2 = sign_lord(chart.sign_of_house(h2))
            if l1 == l2:
                continue
            key = (min(l1, l2), max(l1, l2))
            if key in pairs_seen:
                continue
            g1, g2 = chart.grahas[l1], chart.grahas[l2]
            link = None
            if g1.house == g2.house:
                link = "conjunct in the %s" % _ord(g1.house)
            elif g2.house in chart.aspects_from(l1) and g1.house in chart.aspects_from(l2):
                link = "in mutual aspect"
            elif sign_lord(g1.sign) == l2 and sign_lord(g2.sign) == l1:
                link = "in exchange of signs"
            if not link:
                continue
            pairs_seen.add(key)
            score = (graha_strength(chart, l1)["score"] +
                     graha_strength(chart, l2)["score"]) / 2
            out.append(_yoga(
                "Dhana yoga", "Dhana yoga", "dhana", score,
                "%s and %s, lords of the %s and %s, are %s." % (
                    l1, l2, _ord(h1), _ord(h2), link),
                "The %s is accumulated wealth, the %s past merit, the %s "
                "fortune and the %s income. Any two of them linked forms a "
                "money combination. Here %s (%s lord) and %s (%s lord) are %s." % (
                    _ord(2), _ord(5), _ord(9), _ord(11),
                    l1, _ord(h1), l2, _ord(h2), link),
                "Money accumulates rather than passing through, particularly "
                "in the dashas of %s and %s." % (l1, l2),
                [l1, l2]))

    # Lakshmi yoga: the 9th lord dignified in an angle with a strong lagna lord.
    ninth = sign_lord(chart.sign_of_house(9))
    lagna = sign_lord(chart.sign_of_house(1))
    ng, lg = chart.grahas[ninth], chart.grahas[lagna]
    nd = full_dignity(chart, ninth)["label"]
    if ng.house in KENDRA and nd in ("Exalted", "Own sign", "Moolatrikona") \
            and graha_strength(chart, lagna)["score"] >= 55:
        out.append(_yoga(
            "Lakshmi yoga", "Lakshmi", "dhana",
            (graha_strength(chart, ninth)["score"] +
             graha_strength(chart, lagna)["score"]) / 2,
            "The 9th lord is dignified in an angle and the lagna lord is strong.",
            "%s rules the 9th and sits %s in the %s, an angle, while the lagna "
            "lord %s holds together at %.0f strength." % (
                ninth, nd.lower(), _ord(ng.house), lagna,
                graha_strength(chart, lagna)["score"]),
            "Wealth arrives with reputation attached rather than in spite of "
            "it. Fortune tends to look effortless from the outside.",
            [ninth, lagna]))
    return out


# ---------------------------------------------------------------------------
# Pancha Mahapurusha
# ---------------------------------------------------------------------------

MAHAPURUSHA = {
    "Mars": ("Ruchaka", "commanding, physically capable, drawn to risk and "
                        "authority over others"),
    "Mercury": ("Bhadra", "quick, articulate, commercially able, young-looking "
                          "well past the age for it"),
    "Jupiter": ("Hamsa", "principled, respected, teacherly, and generally "
                         "believed even when wrong"),
    "Venus": ("Malavya", "attractive, comfortable, artistically able, and "
                         "surrounded by the good things"),
    "Saturn": ("Sasa", "enduring, disciplined, commanding through structure "
                       "rather than charm"),
}


def mahapurusha_yogas(chart: Chart) -> list[dict]:
    out = []
    for graha, (name, quality) in MAHAPURUSHA.items():
        g = chart.grahas[graha]
        if g.house not in KENDRA:
            continue
        d = full_dignity(chart, graha)["label"]
        if d not in ("Exalted", "Own sign", "Moolatrikona"):
            continue
        out.append(_yoga(
            "%s yoga" % name, name, "mahapurusha",
            graha_strength(chart, graha)["score"],
            "%s is %s in the %s, an angle." % (graha, d.lower(), _ord(g.house)),
            "One of the five Mahapurusha yogas. It needs a specific graha to be "
            "in its own sign, moolatrikona or exaltation and simultaneously in "
            "an angle from the lagna. %s is %s in %s and occupies the %s." % (
                graha, d.lower(), SIGNS[g.sign], _ord(g.house)),
            "Marks the person out as %s. This shows in the body and manner, not "
            "just in events." % quality,
            [graha]))
    return out


# ---------------------------------------------------------------------------
# Lunar yogas
# ---------------------------------------------------------------------------

def lunar_yogas(chart: Chart) -> list[dict]:
    out = []
    moon = chart.grahas["Moon"]
    mh = moon.house

    def rel(h):
        return _house_from(chart, mh, h)

    # Gaja Kesari: Jupiter in an angle from the Moon.
    jup = chart.grahas["Jupiter"]
    if rel(jup.house) in (1, 4, 7, 10):
        out.append(_yoga(
            "Gaja Kesari yoga", "Gaja Kesari", "lunar",
            (graha_strength(chart, "Jupiter")["score"] +
             graha_strength(chart, "Moon")["score"]) / 2,
            "Jupiter stands in an angle from the Moon.",
            "Jupiter is in the %s and the Moon in the %s, which is the %s from "
            "the Moon. Jupiter in a kendra from the Moon protects the mind and "
            "keeps judgement intact." % (
                _ord(jup.house), _ord(mh), _ord(rel(jup.house))),
            "Steady reputation, sound judgement under pressure, and support "
            "that appears when it is needed. Works quietly rather than "
            "dramatically.",
            ["Jupiter", "Moon"]))

    # Sunapha, Anapha, Durudhara: grahas around the Moon, excluding luminaries
    # and nodes.
    companions = [n for n in REAL_GRAHAS
                  if n not in ("Sun", "Moon")]
    second = [n for n in companions if rel(chart.grahas[n].house) == 2]
    twelfth = [n for n in companions if rel(chart.grahas[n].house) == 12]
    with_moon = [n for n in companions if chart.grahas[n].house == mh]
    kendra_moon = [n for n in companions
                   if rel(chart.grahas[n].house) in (1, 4, 7, 10)]

    if second and twelfth:
        out.append(_yoga(
            "Durudhara yoga", "Durudhara", "lunar", 65,
            "Grahas flank the Moon on both sides.",
            "%s occupy the 2nd from the Moon and %s the 12th. The Moon is "
            "escorted on both sides." % (
                " and ".join(second), " and ".join(twelfth)),
            "Resources come in and go out freely, and there is usually help on "
            "either side of any situation. Rarely isolated.",
            second + twelfth))
    elif second:
        out.append(_yoga(
            "Sunapha yoga", "Sunapha", "lunar", 60,
            "Grahas occupy the 2nd from the Moon.",
            "%s sit in the %s, which is the 2nd from the Moon in the %s." % (
                " and ".join(second), _ord(chart.grahas[second[0]].house),
                _ord(mh)),
            "Self-earned resources and a mind that produces its own material. "
            "Wealth built rather than inherited.",
            second))
    elif twelfth:
        out.append(_yoga(
            "Anapha yoga", "Anapha", "lunar", 60,
            "Grahas occupy the 12th from the Moon.",
            "%s sit in the %s, which is the 12th from the Moon in the %s." % (
                " and ".join(twelfth), _ord(chart.grahas[twelfth[0]].house),
                _ord(mh)),
            "Well regarded, comfortable, and inclined to spend on others. "
            "Often a renunciate streak underneath the comfort.",
            twelfth))

    # Kemadruma: the Moon entirely unsupported.
    if not second and not twelfth and not with_moon and not kendra_moon:
        out.append(_yoga(
            "Kemadruma yoga", "Kemadruma", "dosha", 40,
            "The Moon has no graha in the 2nd, 12th, its own house, or any "
            "angle from itself.",
            "The Moon sits alone in the %s with nothing in the 2nd or 12th "
            "from it, nothing beside it, and nothing in an angle from it. The "
            "mind has no companion in the chart." % _ord(mh),
            "Periods of real isolation and a mind that has to steady itself "
            "without help. It is cancelled if the Moon is in an angle from the "
            "lagna, is full, or receives a benefic aspect, so check those "
            "before reading it heavily.",
            ["Moon"]))

    # Adhi yoga: benefics in the 6th, 7th, 8th from the Moon.
    adhi = [n for n in ("Mercury", "Jupiter", "Venus")
            if rel(chart.grahas[n].house) in (6, 7, 8)]
    if len(adhi) >= 2:
        out.append(_yoga(
            "Adhi yoga", "Adhi", "raja", 60 + 10 * len(adhi),
            "Benefics occupy the 6th, 7th and 8th from the Moon.",
            "%s fall in the 6th to 8th from the Moon in the %s. Benefics "
            "arranged opposite the mind give protection through other people." % (
                " and ".join(adhi), _ord(mh)),
            "Long-term security, competent allies, and a life that recovers "
            "well from setbacks.",
            adhi))

    # Chandra Mangala: Moon with Mars.
    if chart.grahas["Mars"].house == mh:
        out.append(_yoga(
            "Chandra Mangala yoga", "Chandra Mangala", "dhana", 55,
            "Moon and Mars occupy the same house.",
            "Moon and Mars are together in the %s. The mind and the cutting "
            "instrument share a house." % _ord(mh),
            "Sharp earning instinct and the nerve to act on it. Also a temper, "
            "and a tendency to make money in ways that are not gentle.",
            ["Moon", "Mars"]))

    # Shakata: the Moon in 6, 8 or 12 from Jupiter.
    jrel = _house_from(chart, jup.house, mh)
    if jrel in (6, 8, 12):
        out.append(_yoga(
            "Shakata yoga", "Shakata", "dosha", 35,
            "The Moon stands in the %s from Jupiter." % _ord(jrel),
            "Jupiter is in the %s and the Moon in the %s, which is the %s from "
            "Jupiter. Wisdom and mind are out of contact." % (
                _ord(jup.house), _ord(mh), _ord(jrel)),
            "Fortune rises and falls in cycles rather than accumulating. "
            "Cancelled when the Moon is in an angle from the lagna.",
            ["Moon", "Jupiter"]))
    return out


# ---------------------------------------------------------------------------
# Viparita raja yogas
# ---------------------------------------------------------------------------

VIPARITA = {6: ("Harsha", "health, enemies and debt"),
            8: ("Sarala", "crisis, longevity and hidden matters"),
            12: ("Vimala", "loss, expense and confinement")}


def viparita_yogas(chart: Chart) -> list[dict]:
    out = []
    for h, (name, domain) in VIPARITA.items():
        lord = sign_lord(chart.sign_of_house(h))
        g = chart.grahas[lord]
        if g.house not in DUSTHANA:
            continue
        # A lord that also rules a trikona is not really a dusthana lord.
        if any(r in TRIKONA for r in houses_ruled(chart, lord)):
            continue
        out.append(_yoga(
            "%s yoga" % name, name, "viparita",
            graha_strength(chart, lord)["score"],
            "The %s lord has fallen into the %s." % (_ord(h), _ord(g.house)),
            "%s rules the %s and sits in the %s. Two houses of difficulty "
            "cancel rather than compound: the lord of trouble is itself in "
            "trouble, so the trouble does not organise." % (
                lord, _ord(h), _ord(g.house)),
            "Difficulty in %s resolves itself, often suddenly and often "
            "through the failure of whatever was causing it. Reads as luck "
            "from the outside." % domain,
            [lord]))
    return out


# ---------------------------------------------------------------------------
# Neecha bhanga
# ---------------------------------------------------------------------------

def neecha_bhanga(chart: Chart) -> list[dict]:
    """Cancellation of debilitation. Only reported when a graha is debilitated."""
    out = []
    for name in REAL_GRAHAS:
        g = chart.grahas[name]
        ex = EXALTATION.get(name)
        if not ex or g.sign != (ex[0] + 6) % 12:
            continue
        dispositor = sign_lord(g.sign)
        exalt_lord = sign_lord(ex[0])
        conditions = []
        if chart.grahas[dispositor].house in KENDRA:
            conditions.append(
                "%s, the lord of the sign of debilitation, sits in the %s, an "
                "angle from the lagna" % (
                    dispositor, _ord(chart.grahas[dispositor].house)))
        if chart.grahas[exalt_lord].house in KENDRA:
            conditions.append(
                "%s, the lord of %s's exaltation sign, sits in the %s, an "
                "angle" % (exalt_lord, name, _ord(chart.grahas[exalt_lord].house)))
        moon_house = chart.grahas["Moon"].house
        if _house_from(chart, moon_house, chart.grahas[dispositor].house) in (1, 4, 7, 10):
            conditions.append(
                "%s is in an angle from the Moon" % dispositor)
        if g.house in KENDRA:
            conditions.append(
                "%s itself occupies the %s, an angle" % (name, _ord(g.house)))
        # A debilitated graha aspected by or joined to its own exaltation lord.
        if chart.grahas[exalt_lord].house == g.house:
            conditions.append(
                "%s sits with %s, the lord of its exaltation sign" % (
                    name, exalt_lord))

        if conditions:
            out.append(_yoga(
                "Neecha bhanga raja yoga", "Neecha Bhanga", "raja",
                40 + 12 * len(conditions),
                "%s is debilitated in %s, and the debilitation is cancelled." % (
                    name, SIGNS[g.sign]),
                "%s falls in %s. Cancellation applies because %s." % (
                    name, SIGNS[g.sign], "; and ".join(conditions)),
                "The classical reading is that a cancelled debilitation "
                "outperforms an ordinary placement, because the graha has to "
                "climb. Expect a slow start in %s's matters followed by real "
                "capability." % name,
                [name, dispositor]))
        else:
            out.append(_yoga(
                "Debilitation, uncancelled", "Neecha", "dosha", 25,
                "%s is debilitated in %s with no cancellation." % (
                    name, SIGNS[g.sign]),
                "%s is in %s, its sign of fall. Neither %s nor %s reaches an "
                "angle, and %s is not itself angular, so none of the standard "
                "cancellations apply." % (
                    name, SIGNS[g.sign], dispositor, exalt_lord, name),
                "%s's significations operate without confidence. They still "
                "operate. Look to its dispositor %s for how they finally "
                "deliver." % (name, dispositor),
                [name]))
    return out


# ---------------------------------------------------------------------------
# Nodal and afflicting combinations
# ---------------------------------------------------------------------------

def nodal_yogas(chart: Chart) -> list[dict]:
    out = []
    rahu, ketu = chart.grahas["Rahu"], chart.grahas["Ketu"]

    # Kala Sarpa: every graha inside one nodal semicircle.
    r, k = rahu.longitude, ketu.longitude
    inside = []
    for n in REAL_GRAHAS:
        lon = chart.grahas[n].longitude
        arc = (lon - r) % 360
        inside.append(arc < ((k - r) % 360))
    if all(inside) or not any(inside):
        reverse = not any(inside)
        out.append(_yoga(
            "Kala Sarpa yoga", "Kala Sarpa", "dosha", 45,
            "All seven grahas fall on one side of the Rahu-Ketu axis.",
            "Rahu is at %.1f degrees %s and Ketu at %.1f degrees %s. Every "
            "graha lies in the %s arc between them, so the whole chart is "
            "swallowed by the nodal axis." % (
                rahu.degree_in_sign, SIGNS[rahu.sign],
                ketu.degree_in_sign, SIGNS[ketu.sign],
                "Ketu to Rahu" if reverse else "Rahu to Ketu"),
            "Life runs in a confined channel: strong drive, narrow options, and "
            "results that arrive all at once rather than steadily. It is not a "
            "curse. Most charts carrying it simply have an unusually "
            "concentrated life. Broken the moment any graha steps outside the "
            "axis, so check the degrees before reading it heavily.",
            ["Rahu", "Ketu"]))

    for node in ("Rahu", "Ketu"):
        ng = chart.grahas[node]
        for other in REAL_GRAHAS:
            og = chart.grahas[other]
            if og.house != ng.house:
                continue
            sep = abs((og.longitude - ng.longitude + 180) % 360 - 180)
            if other == "Jupiter":
                out.append(_yoga(
                    "Guru Chandala yoga", "Guru Chandala", "dosha", 35,
                    "Jupiter is joined to %s." % node,
                    "Jupiter and %s share the %s, %.1f degrees apart. The "
                    "teacher and the outcaste occupy the same ground." % (
                        node, _ord(ng.house), sep),
                    "Belief becomes unorthodox. Either genuinely original "
                    "understanding or a talent for convincing arguments in bad "
                    "faith, and often both at different ages.",
                    ["Jupiter", node]))
            elif other in ("Sun", "Moon"):
                out.append(_yoga(
                    "Grahana yoga", "Grahana", "dosha", 35,
                    "%s is joined to %s." % (other, node),
                    "%s and %s share the %s, %.1f degrees apart. The "
                    "eclipse pattern." % (other, node, _ord(ng.house), sep),
                    "%s. The signification is not destroyed, it is obscured, "
                    "and tends to be recovered later in life." % (
                        "The father and the sense of self are clouded early on"
                        if other == "Sun" else
                        "The mind and the mother's line carry unrest"),
                    [other, node]))
    return out


def mangal_dosha(chart: Chart) -> list[dict]:
    """Kuja dosha, checked from lagna, Moon and Venus as the tradition requires."""
    mars = chart.grahas["Mars"]
    afflicted_houses = (1, 2, 4, 7, 8, 12)
    hits = []
    for label, origin in (("the lagna", 1),
                          ("the Moon", chart.grahas["Moon"].house),
                          ("Venus", chart.grahas["Venus"].house)):
        d = _house_from(chart, origin, mars.house)
        if d in afflicted_houses:
            hits.append("the %s from %s" % (_ord(d), label))
    if not hits:
        return []

    cancels = []
    if mars.sign in OWN_SIGNS["Mars"] or mars.sign == EXALTATION["Mars"][0]:
        cancels.append("Mars is in its own sign or exaltation, which cancels "
                       "the dosha in most schools")
    if mars.house in chart.aspects_from("Jupiter") or \
            mars.house == chart.grahas["Jupiter"].house:
        cancels.append("Jupiter aspects or joins Mars")
    if mars.house == chart.grahas["Saturn"].house:
        cancels.append("Saturn is with Mars, which blunts it")

    return [_yoga(
        "Mangal dosha", "Kuja dosha", "dosha", 30,
        "Mars falls in %s." % ", ".join(hits),
        "Mars sits in the %s in %s. Counted from %s it lands in a position the "
        "tradition flags for partnership. The dosha is about the pace and heat "
        "Mars brings to marriage, not about the marriage failing." % (
            _ord(mars.house), SIGNS[mars.sign],
            " and ".join(h.split("from ")[1] for h in hits)),
        "Marriage runs hot and needs room for both people to act. %s" % (
            "Cancellation applies: " + "; ".join(cancels) + "."
            if cancels else
            "No standard cancellation found in this chart, so read it as a "
            "real factor in timing rather than a verdict."),
        ["Mars"])]


# ---------------------------------------------------------------------------
# Sun, Mercury and the scholarly combinations
# ---------------------------------------------------------------------------

def other_yogas(chart: Chart) -> list[dict]:
    out = []

    sun, mer = chart.grahas["Sun"], chart.grahas["Mercury"]
    if sun.house == mer.house:
        sep = abs((mer.longitude - sun.longitude + 180) % 360 - 180)
        out.append(_yoga(
            "Budhaditya yoga", "Budhaditya", "raja",
            45 if mer.combust else 70,
            "Sun and Mercury share the %s." % _ord(sun.house),
            "Sun and Mercury are together in %s, %.1f degrees apart.%s" % (
                SIGNS[sun.sign], sep,
                " Mercury is combust at this distance, which is the usual case "
                "and weakens the yoga without removing it." if mer.combust
                else " Mercury is outside the combustion orb, which is "
                     "uncommon and makes this a strong version."),
            "Clear intelligence applied to whatever the %s governs. Good for "
            "analysis, administration and anything requiring a quick, ordered "
            "mind." % _ord(sun.house),
            ["Sun", "Mercury"]))

    # Saraswati: Jupiter, Venus and Mercury all well placed.
    trio = ["Jupiter", "Venus", "Mercury"]
    good = [n for n in trio
            if chart.grahas[n].house in (1, 2, 4, 5, 7, 9, 10)]
    if len(good) == 3 and graha_strength(chart, "Jupiter")["score"] >= 50:
        out.append(_yoga(
            "Saraswati yoga", "Saraswati", "spiritual",
            sum(graha_strength(chart, n)["score"] for n in trio) / 3,
            "Jupiter, Venus and Mercury all occupy angles, trines or the 2nd.",
            "Jupiter is in the %s, Venus in the %s and Mercury in the %s. All "
            "three benefics hold supportive ground and Jupiter is strong." % (
                _ord(chart.grahas["Jupiter"].house),
                _ord(chart.grahas["Venus"].house),
                _ord(chart.grahas["Mercury"].house)),
            "Learning, expression and art come easily and are recognised. "
            "Suited to teaching, writing and performance.",
            trio))

    # Amala: a benefic in the 10th from the lagna or the Moon.
    for origin_name, origin in (("lagna", 1), ("Moon", chart.grahas["Moon"].house)):
        tenth = ((origin - 1 + 9) % 12) + 1
        occupants = [n for n in ("Jupiter", "Venus", "Mercury")
                     if chart.grahas[n].house == tenth
                     and not chart.grahas[n].combust]
        if occupants:
            out.append(_yoga(
                "Amala yoga", "Amala", "raja", 65,
                "%s occupies the 10th from the %s." % (
                    " and ".join(occupants), origin_name),
                "%s sits in the %s, which is the 10th house counted from the "
                "%s. A clean benefic on the house of action." % (
                    " and ".join(occupants), _ord(tenth), origin_name),
                "A lasting reputation for decency. The career is remembered "
                "well even where it was not spectacular.",
                occupants))
            break

    # Vasumati: benefics in the upachayas.
    vas = [n for n in ("Jupiter", "Venus", "Mercury")
           if chart.grahas[n].house in UPACHAYA]
    if len(vas) >= 2:
        out.append(_yoga(
            "Vasumati yoga", "Vasumati", "dhana", 60,
            "Benefics occupy the growth houses.",
            "%s sit in upachaya houses (%s). The 3rd, 6th, 10th and 11th "
            "improve with time, and benefics placed there compound." % (
                " and ".join(vas),
                ", ".join(_ord(chart.grahas[n].house) for n in vas)),
            "Independent means that build steadily. Rarely wealthy young, "
            "reliably comfortable later.",
            vas))

    # Parivartana: any two lords in exchange.
    seen = set()
    for h1 in range(1, 13):
        l1 = sign_lord(chart.sign_of_house(h1))
        g1 = chart.grahas[l1]
        h2 = g1.house
        if h1 == h2:
            continue
        l2 = sign_lord(chart.sign_of_house(h2))
        if l2 == l1 or chart.grahas[l2].house != h1:
            continue
        key = (min(h1, h2), max(h1, h2))
        if key in seen:
            continue
        seen.add(key)
        dusthanas = [h for h in (h1, h2) if h in DUSTHANA]
        if not dusthanas:
            kind, name = "raja", "Maha Parivartana"
            effect = ("The two houses fund each other. What belongs to one "
                      "becomes available to the other, and both improve.")
        elif len(dusthanas) == 2:
            kind, name = "viparita", "Khala Parivartana"
            effect = ("Two difficult houses trade lords, which tends to cancel "
                      "rather than compound. Trouble arrives and then resolves "
                      "itself.")
        else:
            kind, name = "dosha", "Dainya Parivartana"
            effect = ("A good house is tied to a difficult one. The matters of "
                      "the %s are reached only by going through the %s." % (
                          _ord([h for h in (h1, h2) if h not in DUSTHANA][0]),
                          _ord(dusthanas[0])))
        out.append(_yoga(
            "%s yoga" % name, "Parivartana", kind, 55,
            "The %s and %s lords have exchanged signs." % (_ord(h1), _ord(h2)),
            "%s rules the %s and sits in the %s. %s rules the %s and sits in "
            "the %s. A full exchange." % (
                l1, _ord(h1), _ord(h2), l2, _ord(h2), _ord(h1)),
            effect, [l1, l2]))
    return out


# ---------------------------------------------------------------------------

def all_yogas(chart: Chart) -> list[dict]:
    """Every detector, sorted so the useful material is at the top."""
    found = []
    for fn in (raja_yogas, dhana_yogas, mahapurusha_yogas, lunar_yogas,
               viparita_yogas, neecha_bhanga, nodal_yogas, mangal_dosha,
               other_yogas):
        try:
            found.extend(fn(chart))
        except Exception as exc:  # a broken detector must not take the chart down
            found.append(_yoga(
                "Detector error", "", "error", 0,
                "%s failed" % fn.__name__, str(exc), "", []))

    order = {"mahapurusha": 0, "raja": 1, "dhana": 2, "viparita": 3,
             "lunar": 4, "spiritual": 5, "dosha": 6, "error": 9}
    found.sort(key=lambda y: (order.get(y["kind"], 7), -y["strength"]))
    return found


def summary(chart: Chart) -> dict:
    ys = all_yogas(chart)
    return {
        "total": len(ys),
        "supportive": len([y for y in ys if y["kind"] in
                           ("raja", "dhana", "mahapurusha", "viparita",
                            "spiritual")]),
        "challenging": len([y for y in ys if y["kind"] == "dosha"]),
        "yogas": ys,
    }
