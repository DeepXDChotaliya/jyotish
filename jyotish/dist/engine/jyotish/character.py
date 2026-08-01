"""
The first house as the lens, and what it asks the person to change.

Parashara's ordering is deliberate: the lagna comes before the twelve subjects
because it is the vantage point from which all twelve are experienced. Two
people with identical 7th houses will not have identical marriages, because the
lagna decides what each of them does when the 7th house produces its result.

That gives a practical rule, and it is the whole point of this module. When a
difficult house is *connected to the lagna* -- its lord sits in the 1st, or the
lagna lord has gone into it, or a graha in the 1st rules it -- the trouble is
not simply arriving from outside. The person's own default behaviour is part of
the mechanism. That is the part that can be changed, and changing it is what
classical texts mean by upaya before they get to gemstones.

Where no such connection exists, this module says so rather than inventing one.
A hard 8th house with no link to the lagna is a circumstance to be endured, not
a character flaw to be corrected, and telling someone otherwise is malpractice.
"""

from __future__ import annotations

from . import interpret, phala
from .engine import (
    DUSTHANA, KENDRA, MARAKA, NATURAL_BENEFIC, NATURAL_MALEFIC, SIGNS,
    TRIKONA, Chart, full_dignity, graha_strength, sign_lord,
)
from .lords import _ord, analyse_house, functional_nature, houses_ruled

# ---------------------------------------------------------------------------
# The lagna sign as a temperament, with the shadow it casts and the work.
# ---------------------------------------------------------------------------

LAGNA_TEMPERAMENT = {
    0: {
        "constitution": "Lean, wiry, quick to heat. Marks or scars about the head are the classical note.",
        "temperament": "You start things. Direct, physically brave, impatient with process, and constitutionally unable to be second in a room you care about.",
        "strengths": ["initiative", "physical courage", "decisiveness", "honesty to the point of bluntness"],
        "shadow": ["impatience", "starting more than you finish", "reading disagreement as challenge", "anger that arrives before the facts"],
        "core_work": "Finish one thing before starting the next, and let a disagreement sit for a day before answering it. Almost every difficulty an Aries lagna reports traces back to speed rather than to malice.",
    },
    1: {
        "constitution": "Solid, well built, strong neck and throat, prone to putting on weight with comfort.",
        "temperament": "You accumulate and you hold. Patient, sensual, reliable, and immovable once you have taken a position.",
        "strengths": ["persistence", "loyalty", "practical sense", "genuine calm under pressure"],
        "shadow": ["refusing to revise a position", "attachment to comfort past its usefulness", "slowness that becomes avoidance", "possessiveness about people and things"],
        "core_work": "Notice the difference between being steady and being stuck. Set a review date on positions you have held for years, and actually keep it.",
    },
    2: {
        "constitution": "Slim, mobile, expressive hands, nervous energy. Lungs and shoulders are the classical note.",
        "temperament": "You think by talking and you exist in more than one version. Curious, articulate, adaptable, and rarely fully present in one place.",
        "strengths": ["quick intelligence", "communication", "adaptability", "seeing several sides at once"],
        "shadow": ["scattering", "talking instead of doing", "committing to nothing so as not to lose anything", "nervous overthinking"],
        "core_work": "Reduce the number of open threads. Pick the two that matter and close the rest deliberately rather than letting them lapse.",
    },
    3: {
        "constitution": "Softer build, round face, sensitive digestion and chest.",
        "temperament": "You read the room before you enter it. Protective, retentive, emotionally intelligent, and slow to let anyone all the way in.",
        "strengths": ["empathy", "memory", "loyalty to your own", "reading what is unsaid"],
        "shadow": ["withdrawing instead of stating a need", "holding grievances for years", "moodiness that others must navigate", "confusing caretaking with control"],
        "core_work": "Say the need out loud at the time, in plain words, instead of withdrawing and waiting to be understood. This single habit resolves more Cancer lagna difficulty than anything else.",
    },
    4: {
        "constitution": "Upright bearing, broad chest, strong presence. Heart and spine are the classical note.",
        "temperament": "You need the thing to be yours. Generous, warm, commanding, and genuinely wounded by being overlooked.",
        "strengths": ["natural authority", "generosity", "loyalty", "the ability to carry a room"],
        "shadow": ["pride that will not bend", "needing credit more than the outcome", "taking disagreement personally", "dramatising a slight"],
        "core_work": "Separate the outcome from the credit. Practise letting someone else announce a result you produced, and notice that nothing is actually lost.",
    },
    5: {
        "constitution": "Neat, contained, often youthful. Digestion and nerves are the classical note.",
        "temperament": "You see the flaw first. Precise, useful, self-improving, and harder on yourself than on anyone else.",
        "strengths": ["discrimination", "reliability", "service without fuss", "genuine competence"],
        "shadow": ["criticism that lands as rejection", "anxiety dressed up as preparation", "perfectionism that prevents finishing", "under-claiming your own worth"],
        "core_work": "Say one appreciative thing before the correction, every time. And ship at eighty percent, because the last twenty is usually anxiety rather than quality.",
    },
    6: {
        "constitution": "Balanced, attractive, pleasant featured. Kidneys and lower back are the classical note.",
        "temperament": "You move through agreement rather than force. Diplomatic, fair, aesthetically alert, and uncomfortable in open conflict.",
        "strengths": ["fairness", "charm", "negotiation", "seeing the other position honestly"],
        "shadow": ["avoiding necessary conflict until it compounds", "deciding by deferring", "keeping the peace at your own expense", "resentment stored behind politeness"],
        "core_work": "Have the difficult conversation early and small. A Libra lagna's problems are almost never caused by the conflict itself; they are caused by how long it was postponed.",
    },
    7: {
        "constitution": "Intense gaze, strong constitution, marked features. Reproductive and eliminative systems are the classical note.",
        "temperament": "You go under the surface and keep your own counsel. Penetrating, resilient, private, and slow to forgive.",
        "strengths": ["depth", "resilience", "loyalty once given", "seeing what people conceal"],
        "shadow": ["suspicion in advance of evidence", "control exercised through withholding", "keeping score", "cutting someone off entirely rather than repairing"],
        "core_work": "Ask the question instead of building the theory. Most Scorpio lagna damage is done by a conclusion reached privately and acted on before it was checked.",
    },
    8: {
        "constitution": "Tall or long-limbed, open expression, strong thighs. Liver and hips are the classical note.",
        "temperament": "You need a principle before you will commit. Optimistic, expansive, honest, and restless for whatever is further off.",
        "strengths": ["vision", "honesty", "generosity of spirit", "the ability to lift other people"],
        "shadow": ["promising more than you deliver", "moralising", "leaving before the difficult middle", "mistaking enthusiasm for a plan"],
        "core_work": "Halve what you promise and deliver all of it. Stay through one full cycle of something boring; the maturity a Sagittarius lagna is missing is almost always on the other side of that.",
    },
    9: {
        "constitution": "Lean, durable, ages well. Knees, joints and teeth are the classical note.",
        "temperament": "You climb. Disciplined, realistic, patient with delay, and suspicious of anything that arrives easily.",
        "strengths": ["endurance", "responsibility", "long-range planning", "reliability under load"],
        "shadow": ["treating warmth as inefficiency", "carrying everything alone", "pessimism presented as realism", "postponing your own life until the work is done"],
        "core_work": "Ask for help before you need it, and schedule rest as an obligation, since that is the only category you honour. The work is not going anywhere.",
    },
    10: {
        "constitution": "Tall or angular, distinctive appearance. Circulation and ankles are the classical note.",
        "temperament": "You stand slightly outside. Humane in principle, independent, unorthodox, and more comfortable with the many than with the few.",
        "strengths": ["originality", "principled independence", "genuine egalitarianism", "systems thinking"],
        "shadow": ["detachment where warmth is required", "contrarianism as reflex", "intellectualising feeling", "loyalty to the idea over the person"],
        "core_work": "Practise particular warmth with specific people rather than general goodwill toward everyone. The intimacy an Aquarius lagna misses is not a concept, it is an evening.",
    },
    11: {
        "constitution": "Soft featured, expressive eyes, fluid build. Feet and the lymphatic system are the classical note.",
        "temperament": "Your edges are provisional. Compassionate, imaginative, permeable, and prone to absorbing whatever is around you.",
        "strengths": ["compassion", "imagination", "intuition", "the capacity to forgive genuinely"],
        "shadow": ["poor boundaries", "escaping rather than confronting", "vagueness about your own needs", "rescuing people who are not asking"],
        "core_work": "Decide in advance what you will and will not do, and write it down, because in the moment you will agree to anything. Boundaries are the entire practice for a Pisces lagna.",
    },
}

# What personal trait feeds trouble in each house, when the house is connected
# to the lagna. Used to convert a weak house into something actionable.
TRAIT_FOR_HOUSE = {
    1: ("how you carry yourself",
        "The way you present and assert is itself the variable. Health, energy and how seriously people take you all move when this changes."),
    2: ("what you value and how you speak",
        "Money and family difficulty here usually traces to speech: what was said sharply, or what was never said at all."),
    3: ("courage and follow-through",
        "The gap is between intention and execution. Nothing here is blocked from outside; it stalls because it was not pushed."),
    4: ("what you need in order to feel safe",
        "Domestic difficulty tracks the conditions you have quietly decided you require before you can be at ease."),
    5: ("how you handle being seen, and creative risk",
        "Trouble with children, study or creative work usually traces to either performing for approval or refusing to be visible at all."),
    6: ("how you handle conflict, routine and the body",
        "Enemies, debt and illness here are downstream of habit: what you let accumulate, and which fights you avoid or pick."),
    7: ("how you meet other people, and what you concede",
        "Partnership difficulty traces to the terms you set at the beginning and never revisited, or never set at all."),
    8: ("how you behave when you are not in control",
        "Crisis is not caused by character, but the size of the damage usually is. What matters here is the reflex when the ground moves."),
    9: ("what you believe, and who you allow to teach you",
        "Loss of fortune here often follows a rigid belief, or an unexamined loyalty to the wrong authority."),
    10: ("how you relate to authority and duty",
        "Career difficulty traces to the stance you take toward people above you, and to what you are willing to be seen doing."),
    11: ("what you want, and how much is enough",
        "Gains stall or leak according to whether the wanting has a defined edge, and whether the network is maintained or merely used."),
    12: ("what you refuse to let go of",
        "Loss, expense and isolation here are usually the cost of holding on past the point where holding on works."),
}

# Traditional upaya, kept factual. Behavioural work comes first everywhere in
# this module; these are recorded because they are part of the tradition, not
# because they substitute for it.
UPAYA = {
    "Sun": {"day": "Sunday", "mantra": "Om Suryaya Namah", "charity": "wheat, jaggery, copper", "conduct": "respect toward the father and toward those in authority"},
    "Moon": {"day": "Monday", "mantra": "Om Chandraya Namah", "charity": "rice, milk, silver, white cloth", "conduct": "care of the mother, and regular sleep"},
    "Mars": {"day": "Tuesday", "mantra": "Om Mangalaya Namah", "charity": "red lentils, copper, red cloth", "conduct": "physical exercise, and restraint in anger"},
    "Mercury": {"day": "Wednesday", "mantra": "Om Budhaya Namah", "charity": "green gram, books, green cloth", "conduct": "truthful speech, and study"},
    "Jupiter": {"day": "Thursday", "mantra": "Om Gurave Namah", "charity": "turmeric, chana dal, yellow cloth", "conduct": "respect toward teachers, and giving counsel freely"},
    "Venus": {"day": "Friday", "mantra": "Om Shukraya Namah", "charity": "white sweets, sugar, white cloth", "conduct": "moderation in pleasure, and respect toward women"},
    "Saturn": {"day": "Saturday", "mantra": "Om Shanaye Namah", "charity": "sesame, iron, black cloth, oil", "conduct": "service to labourers and the old, and keeping your word"},
    "Rahu": {"day": "Saturday", "mantra": "Om Rahave Namah", "charity": "mustard oil, blankets, sesame", "conduct": "honesty about motive, and avoidance of intoxicants"},
    "Ketu": {"day": "Tuesday", "mantra": "Om Ketave Namah", "charity": "blankets, sesame, feeding dogs", "conduct": "spiritual practice, and non-attachment to outcome"},
}


def _article(word: str) -> str:
    return "an" if word[:1].upper() in "AEIOU" else "a"


def _decap(text: str) -> str:
    """Lowercase only the first letter, so following sentences survive."""
    return text[:1].lower() + text[1:] if text else text


def _lagna_lord_effect(chart: Chart) -> dict:
    """Where the lagna lord sits is where the person keeps putting themselves."""
    lord = sign_lord(chart.lagna_sign)
    g = chart.grahas[lord]
    h = interpret.HOUSES[g.house - 1]
    trait, _ = TRAIT_FOR_HOUSE[g.house]
    dignity = full_dignity(chart, lord)
    strength = graha_strength(chart, lord)

    if g.house in DUSTHANA:
        stance = ("You put yourself where the difficulty is. The lagna lord in "
                  "the %s means you are drawn, repeatedly and by temperament, "
                  "into the house of %s. Some of that is service and some of "
                  "it is habit, and telling the two apart is the work." % (
                      _ord(g.house), h["title"].lower()))
    elif g.house in TRIKONA:
        stance = ("You put yourself on supportive ground. The lagna lord in the "
                  "%s means your instinct about where to stand is broadly "
                  "reliable." % _ord(g.house))
    elif g.house in KENDRA:
        stance = ("You put yourself where things are visible. The lagna lord in "
                  "the %s means you gravitate to the active, public side of "
                  "life rather than the interior one." % _ord(g.house))
    else:
        stance = ("The lagna lord in the %s means your energy goes into %s "
                  "before it goes anywhere else." % (
                      _ord(g.house), h["title"].lower()))

    return {
        "lord": lord,
        "house": g.house,
        "house_title": h["title"],
        "sign": SIGNS[g.sign],
        "dignity": dignity["label"],
        "dignity_reason": dignity["reason"],
        "strength": strength["score"],
        "band": strength["band"],
        "stance": stance,
        "trait": trait,
        "in_sign": phala.graha_in_sign(lord, g.sign),
        "in_house": phala.graha_in_house(lord, g.house),
        "condition_note": _condition_note(chart, lord),
    }


def _condition_note(chart: Chart, lord: str) -> str:
    """What the lagna lord's condition does to the person's baseline."""
    g = chart.grahas[lord]
    d = full_dignity(chart, lord)["label"]
    bits = []
    if d in ("Exalted", "Moolatrikona", "Own sign"):
        bits.append("The lagna lord is %s, so the baseline sense of self is "
                    "sound. When things go wrong here they go wrong through "
                    "circumstance rather than through self-doubt." % d.lower())
    elif d == "Debilitated":
        bits.append("The lagna lord is debilitated. The baseline sense of self "
                    "is lower than the actual capability, which means you will "
                    "consistently under-claim. Check for cancellation before "
                    "treating this as fixed.")
    elif "enemy" in d.lower():
        bits.append("The lagna lord sits in a difficult sign, so confidence is "
                    "conditional and has to be rebuilt fairly often.")
    if g.combust:
        bits.append("It is combust, which means your own agenda keeps getting "
                    "subordinated to authority, to the father, or to the "
                    "demands of status.")
    if g.retrograde and lord not in ("Rahu", "Ketu"):
        bits.append("It is retrograde, so self-definition arrives late and out "
                    "of order. People with this often report becoming "
                    "themselves properly in their thirties or later.")
    return " ".join(bits) or ("The lagna lord is in ordinary condition, so it "
                              "neither adds to nor subtracts from the baseline.")


def _occupant_traits(chart: Chart) -> list:
    """Grahas in the 1st imprint directly on the personality."""
    out = []
    for g in chart.grahas_in_house(1):
        nature = functional_nature(chart, g.name)
        info = interpret.GRAHAS_INFO[g.name]
        ruled = nature["ruled"]
        carried = ""
        if ruled:
            hard = [r for r in ruled if r in DUSTHANA]
            if hard:
                carried = ("It brings the %s into your personality directly. "
                           "The matters of that house are not simply happening "
                           "to you; they are part of how you are built, which "
                           "is why they recur." % _ord(hard[0]))
            else:
                carried = ("It brings the %s into your personality, so those "
                           "matters are lived as character rather than as "
                           "circumstance." % " and ".join(_ord(r) for r in ruled))
        out.append({
            "graha": g.name,
            "sign": SIGNS[g.sign],
            "trait": phala.graha_in_house(g.name, 1),
            "in_sign": phala.graha_in_sign(g.name, g.sign),
            "carried": carried,
            "benefic": g.name in NATURAL_BENEFIC,
            "karaka": info["karaka"],
            "strength": graha_strength(chart, g.name)["score"],
        })
    return out


def _aspects_to_lagna(chart: Chart) -> list:
    """Drishti onto the 1st conditions the personality from a distance."""
    from .engine import aspecting_grahas
    out = []
    for a in aspecting_grahas(chart, 1):
        g = chart.grahas[a["graha"]]
        if g.house == 1:
            continue
        nature = functional_nature(chart, a["graha"])
        if a["graha"] in NATURAL_BENEFIC:
            effect = ("softens and protects the personality. It is why you get "
                      "the benefit of the doubt more often than you notice.")
        elif a["graha"] == "Saturn":
            effect = ("disciplines and restricts the personality. It is the "
                      "source of the seriousness, the self-doubt and the "
                      "durability, all three from the same place.")
        elif a["graha"] == "Mars":
            effect = ("adds heat and push to the personality, and a shorter "
                      "fuse than you would otherwise have.")
        elif a["graha"] in ("Rahu", "Ketu"):
            effect = ("distorts the self-image, either inflating it or "
                      "hollowing it out. Your view of yourself is the least "
                      "reliable instrument you own.")
        else:
            effect = "colours the personality with its own nature."
        out.append({
            "graha": a["graha"],
            "aspect": "%s aspect" % _ord(a["aspect"]),
            "from_house": g.house,
            "rules": nature["ruled"],
            "effect": "%s throws its %s aspect onto your lagna from the %s, "
                      "which %s" % (a["graha"], _ord(a["aspect"]),
                                    _ord(g.house), effect),
        })
    return out


def growth_edges(chart: Chart) -> list:
    """Pressured houses that are wired to the lagna, and the work each implies.

    Only houses with an actual structural link to the 1st appear here. A house
    can be weak and simply not be about the person's character, and that
    distinction is the point of the method.
    """
    lagna_lord = sign_lord(chart.lagna_sign)
    lagna_lord_house = chart.grahas[lagna_lord].house
    first_house_grahas = [g.name for g in chart.grahas_in_house(1)]

    edges = []
    for house in range(1, 13):
        h = analyse_house(chart, house)
        if h["verdict"] not in ("Mixed", "Under pressure", "Weak"):
            continue

        lord = h["lord"]
        lg = chart.grahas[lord]
        links = []

        if lord in first_house_grahas:
            links.append(("lord_in_lagna",
                          "%s rules your %s and sits in your 1st house. In "
                          "Parashari terms the house has moved into the body. "
                          "Whatever goes wrong there is not arriving from "
                          "outside, it is being carried in by you." % (
                              lord, _ord(house))))
        if lagna_lord_house == house:
            links.append(("lagna_lord_there",
                          "%s, the lord of your lagna, has gone into the %s. "
                          "You put yourself into this house repeatedly. That is "
                          "temperament, not accident, and it is adjustable." % (
                              lagna_lord, _ord(house))))
        if lord == lagna_lord and house != 1:
            links.append(("shared_lord",
                          "The same graha, %s, rules both your lagna and your "
                          "%s. The two are structurally the same subject in "
                          "this chart: you cannot fix one without the other." % (
                              lord, _ord(house))))
        for gname in first_house_grahas:
            if house in houses_ruled(chart, gname) and gname != lord:
                links.append(("occupant_rules",
                              "%s sits in your 1st house and also rules the "
                              "%s, which wires that house's difficulty directly "
                              "into your personality." % (gname, _ord(house))))
        if 1 in chart.aspects_from(lord):
            links.append(("lord_aspects_lagna",
                          "%s, lord of the %s, throws its aspect onto your "
                          "lagna. The house's tone reaches your personality "
                          "even though the graha itself is elsewhere." % (
                              lord, _ord(house))))

        if not links:
            continue

        trait, why = TRAIT_FOR_HOUSE[house]
        lagna_work = LAGNA_TEMPERAMENT[chart.lagna_sign]["core_work"]
        shadow = LAGNA_TEMPERAMENT[chart.lagna_sign]["shadow"]

        edges.append({
            "house": house,
            "area": h["title"],
            "theme": h["theme"],
            "verdict": h["verdict"],
            "lord": lord,
            "lord_house": lg.house,
            "lord_strength": h["strength"]["score"],
            "links": [{"kind": k, "text": t} for k, t in links],
            "trait": trait,
            "why_outer": why,
            "shadow_candidates": shadow,
            "work": _work_for(chart, house, links, lord),
            "lagna_work": lagna_work,
            "upaya": UPAYA.get(lord, {}),
            "priority": (3 if h["verdict"] == "Weak" else
                         2 if h["verdict"] == "Under pressure" else 1)
                        + len(links),
        })

    edges.sort(key=lambda e: -e["priority"])
    return edges


def _work_for(chart: Chart, house: int, links: list, lord: str) -> str:
    """The specific behavioural instruction, given how the link was formed."""
    kinds = {k for k, _ in links}
    lagna = LAGNA_TEMPERAMENT[chart.lagna_sign]
    trait, _ = TRAIT_FOR_HOUSE[house]

    if "lagna_lord_there" in kinds and house in DUSTHANA:
        return ("The instruction here is subtraction, not effort. You are "
                "already giving this house more of yourself than it returns. "
                "Reduce the time and identity invested in it and watch whether "
                "the difficulty shrinks. For your lagna specifically: %s" %
                _decap(lagna["core_work"]))
    if "lord_in_lagna" in kinds:
        return ("Because the lord of this house sits in your 1st, the fastest "
                "route to change is behavioural rather than circumstantial. "
                "Work on %s directly. The external situation tends to follow "
                "within one dasha period rather than resisting. For your lagna: "
                "%s" % (trait, _decap(lagna["core_work"])))
    if "shared_lord" in kinds:
        return ("One graha carries both your self and this house, so treat any "
                "improvement in %s as work on yourself, and any work on "
                "yourself as improvement in %s. Strengthening %s serves both." %
                (trait, trait, lord))
    if "occupant_rules" in kinds:
        return ("A graha in your 1st house rules this area, so the trait and "
                "the problem share a source. Change %s and the house changes "
                "with it. %s" % (trait, lagna["core_work"]))
    return ("The connection is by aspect, so the influence is real but "
            "indirect. Work on %s, and expect the change to be gradual rather "
            "than immediate. %s" % (trait, lagna["core_work"]))


def profile(chart: Chart) -> dict:
    """The full first-house reading, assembled."""
    sign = chart.lagna_sign
    t = LAGNA_TEMPERAMENT[sign]
    info = interpret.SIGNS_INFO[sign]
    lord_effect = _lagna_lord_effect(chart)
    occupants = _occupant_traits(chart)
    aspects = _aspects_to_lagna(chart)
    edges = growth_edges(chart)

    return {
        "sign": SIGNS[sign],
        "sign_sanskrit": info["sanskrit"],
        "element": info["element"],
        "mode": info["mode"],
        "lord": lord_effect["lord"],
        "constitution": t["constitution"],
        "temperament": t["temperament"],
        "strengths": t["strengths"],
        "shadow": t["shadow"],
        "core_work": t["core_work"],
        "lord_effect": lord_effect,
        "occupants": occupants,
        "aspects": aspects,
        "growth_edges": edges,
        "summary": _summary(chart, t, lord_effect, occupants, edges),
    }


def _summary(chart, t, lord_effect, occupants, edges) -> str:
    """A synthesis, not a concatenation. Everything quoted here is expanded
    in its own panel below, so this says only what those panels do not."""
    info = interpret.SIGNS_INFO[chart.lagna_sign]
    parts = [
        "Every house in this chart is experienced from %s %s lagna, %s %s, "
        "ruled by %s." % (
            _article(SIGNS[chart.lagna_sign]), SIGNS[chart.lagna_sign],
            info["mode"].lower(), info["element"].lower(), lord_effect["lord"]),
        "Its lord has gone to the %s, which sets where you habitually put "
        "yourself." % _ord(lord_effect["house"]),
    ]
    if occupants:
        parts.append("%s in the 1st house %s that further." % (
            " and ".join(o["graha"] for o in occupants),
            "shape" if len(occupants) > 1 else "shapes"))
    if edges:
        top = edges[:3]
        areas = "; ".join("the %s (%s)" % (_ord(e["house"]), e["area"].lower())
                          for e in top)
        parts.append("Of the houses currently under pressure, %s %s wired back "
                     "to your own temperament rather than to circumstance "
                     "alone, which means %s can be moved by changing how you "
                     "operate." % (
                         areas, "are" if len(top) > 1 else "is",
                         "they" if len(top) > 1 else "it"))
    else:
        parts.append("No pressured house in this chart is structurally wired to "
                     "your lagna. Where difficulty shows up it is circumstance "
                     "rather than character, and the work is endurance and "
                     "timing rather than self-correction.")
    return " ".join(parts)
