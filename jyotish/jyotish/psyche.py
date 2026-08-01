"""
Depth psychology, and the interior of a transit.

Jyotish already contains a psychology; it just does not use modern vocabulary
for it. The grahas are not only planets, they are functions of a person:
Surya is the will to be someone, Chandra is the feeling mind, Shani is the
reality principle, Rahu is craving, Ketu is the drive toward dissolution. This
module reads the chart in those terms without pretending the two systems are
identical.

The three-layer model used here is standard and worth stating plainly:

  Lagna nakshatra   the operating system. How you meet a room, what you look
                    like from outside, the reflex before thought.
  Chandra nakshatra the actual person. The feeling mind, the private self,
                    what you are like when nobody is managing the impression.
                    This is the layer classical Jyotish weights most heavily.
  Surya nakshatra   the soul's agenda. What the life is for, as distinct from
                    what it feels like or how it presents.

Where those three disagree, the person experiences themselves as divided, and
naming that division is usually the single most useful thing a reading does.

An important limit, stated once: this is a symbolic language for
self-reflection, not a clinical instrument. It does not diagnose anything and
it does not replace a therapist. Where the chart describes real suffering, the
correct response is a person, not a gemstone.
"""

from __future__ import annotations

from datetime import datetime

from . import nakshatra as nk
from .engine import (
    DUSTHANA, KENDRA, NAKSHATRAS, SIGNS, TRIKONA, Chart, full_dignity,
    graha_strength, nakshatra_lord, sign_lord,
)
from .lords import _ord, functional_nature, houses_ruled

# ---------------------------------------------------------------------------
# The grahas as psychological functions
# ---------------------------------------------------------------------------

GRAHA_PSYCHE = {
    "Sun": {
        "function": "The will to be someone. Ego in the neutral sense: the "
                    "organising centre that says this is me and not that.",
        "healthy": "Confidence without needing an audience. Can lead, can be "
                   "seen, can take responsibility for an outcome.",
        "wounded": "Either inflation, needing constant confirmation of "
                   "importance, or collapse, an inability to occupy any space "
                   "at all. Both are the same wound at different pressures.",
        "integration": "Do something visible and let the credit be shared. "
                       "The Sun heals by being seen without needing to be "
                       "central.",
        "father": "The Sun carries the father, and the relationship to "
                  "authority for the rest of the life is usually a negotiation "
                  "with him, present or absent.",
    },
    "Moon": {
        "function": "The feeling mind. Not emotion as event, but the "
                    "continuous inner weather that everything else is "
                    "experienced through.",
        "healthy": "Emotionally responsive without being flooded. Can be "
                   "affected by something and still act.",
        "wounded": "Either flooding, where feeling overwhelms function, or "
                   "numbing, where feeling is cut off to keep functioning. "
                   "Both track back to the early holding environment.",
        "integration": "Regular sleep, regular food, water, and one person who "
                       "hears the unedited version. The Moon is not repaired "
                       "by insight, it is repaired by rhythm and safety.",
        "mother": "The Moon carries the mother and the first experience of "
                  "being held. Its condition describes what the nervous system "
                  "learned to expect.",
    },
    "Mars": {
        "function": "The capacity to assert, to cut, to protect a boundary. "
                    "Anger in its useful form, which is the energy that says "
                    "no.",
        "healthy": "Can be direct, can compete, can end things. Anger arrives, "
                   "does its job, and leaves.",
        "wounded": "Either explosive, where the boundary is defended long "
                   "after the threat has gone, or collapsed, where anger turns "
                   "inward and becomes depression or illness.",
        "integration": "Physical exertion, and one honest confrontation had at "
                       "the right size. Mars unexpressed does not disappear, "
                       "it relocates into the body.",
    },
    "Mercury": {
        "function": "The discriminating intellect. The part that names, "
                    "divides, compares and explains.",
        "healthy": "Clear thought, clear speech, able to hold two ideas "
                   "without collapsing them.",
        "wounded": "Rumination, anxiety, cleverness used to avoid feeling. "
                   "Mercury under stress talks in order not to know something.",
        "integration": "Write it down rather than turning it over. Mercury "
                       "settles when the loop is externalised.",
    },
    "Jupiter": {
        "function": "The meaning-making function. The part that says this "
                    "matters, and there is a larger frame this fits into.",
        "healthy": "Faith that survives evidence. Generosity. The ability to "
                   "place a difficulty inside a story that makes it bearable.",
        "wounded": "Either dogma, where the frame is defended against reality, "
                   "or nihilism, where no frame is allowed at all. Both are "
                   "failures of the same organ.",
        "integration": "Teach something, or be taught something. Jupiter grows "
                       "in the exchange, not in private conviction.",
    },
    "Venus": {
        "function": "The capacity for pleasure, relatedness and valuing. What "
                    "makes something worth having and someone worth loving.",
        "healthy": "Can enjoy, can receive, can want something without shame "
                   "and can be close without merging.",
        "wounded": "Either compulsive seeking, where the appetite never "
                   "settles, or anhedonia, where nothing is allowed to be "
                   "enjoyed. Often both alternating.",
        "integration": "Receive something with no reciprocation planned. Venus "
                       "is damaged mostly by transactional love and repaired "
                       "by the non-transactional kind.",
    },
    "Saturn": {
        "function": "The reality principle. Time, limit, consequence, and the "
                    "part that knows the bill arrives.",
        "healthy": "Can defer gratification, keep a commitment, and tolerate "
                   "that some things simply take years.",
        "wounded": "Either rigidity and chronic fear, where limit becomes the "
                   "whole world, or an avoidance of all structure, which "
                   "produces the same suffering more slowly.",
        "integration": "Do the small hard thing daily. Saturn is the only "
                       "graha that responds to nothing except repetition over "
                       "time, which is also the point it is making.",
    },
    "Rahu": {
        "function": "Craving. The part of the psyche that reaches for what it "
                    "does not have and cannot be satisfied by getting it.",
        "healthy": "Ambition, hunger for experience, willingness to break a "
                   "pattern the family considers mandatory.",
        "wounded": "Compulsion, addiction, envy, and identity built out of "
                   "image. Rahu's suffering is specifically that acquisition "
                   "does not close the gap.",
        "integration": "Name what the craving is actually for underneath the "
                       "object, and give the object a defined limit. Rahu is "
                       "not renounced, it is bounded.",
    },
    "Ketu": {
        "function": "Disidentification. The part that withdraws investment, "
                    "and that already knows how to do something it has no "
                    "interest in doing.",
        "healthy": "Non-attachment, real spiritual capacity, and the ability "
                   "to walk away cleanly.",
        "wounded": "Dissociation, chronic dissatisfaction with the present, "
                   "and a talent that is refused because it never felt like a "
                   "choice.",
        "integration": "Engage the thing you are skilled at and bored by, "
                       "deliberately, for a fixed period. Ketu's mastery is "
                       "real and its indifference is a defence.",
    },
}

# ---------------------------------------------------------------------------
# The interior of a slow transit
#
# The outer event is in phala.TRANSIT_PHALA. This is what it feels like from
# inside, which is usually what the person actually came to ask about.
# ---------------------------------------------------------------------------

TRANSIT_INTERIOR = {
    "Saturn": {
        "process": "Contraction and reality testing",
        "philosophy": "Saturn does not add difficulty. It removes the "
                      "cushioning that was hiding difficulty already there. "
                      "What feels like loss is usually the withdrawal of a "
                      "subsidy you had stopped noticing. The transit ends "
                      "when the structure underneath is genuinely load "
                      "bearing, and not before.",
        "houses": {
            1: "You stop being able to run on personality. The self-image thins out and what is left is whatever you can actually do. Uncomfortable, and the most honest two and a half years most people get.",
            2: "The question becomes what you actually value, as opposed to what you say you value. Money is the medium; the subject is worth.",
            3: "Courage stops being a feeling and becomes a decision made repeatedly without enthusiasm. Effort and reward decouple, which is the lesson.",
            4: "The inner base is examined. Whatever you have been using as home, literal or emotional, is tested for whether it actually holds you. Loneliness here is informational, not personal.",
            5: "Spontaneity is restricted so that discipline can be learned. Creativity gets slower and much better. What was play becomes practice.",
            6: "You discover exactly how much you can take, which is more than you thought. Endurance is built here, and the cost is that you find out through use.",
            7: "Other people stop cooperating with your projections. The partner becomes stubbornly themselves. This is either the end of the relationship or the beginning of the real one.",
            8: "Control is removed. Whatever you were managing gets managed by circumstance instead. The psychological work is surrender, which is not resignation.",
            9: "Belief is stripped of comfort. What survives is what you actually hold rather than what you inherited. Faith becomes drier and more durable.",
            10: "You find out whether the work is yours or whether it was a costume. Responsibility increases and recognition lags, which is the specific test.",
            11: "Wanting is examined. You get some of it, later than expected, and discover which of the desires were ever really yours.",
            12: "The interior opens because the exterior goes quiet. Withdrawal is not depression here, though it can become depression if fought. Practice works during this one.",
        },
    },
    "Jupiter": {
        "process": "Expansion and meaning making",
        "philosophy": "Jupiter enlarges whatever it finds, including "
                      "self-deception. The transit gives opportunity and no "
                      "discrimination about which opportunity. Its year is "
                      "wasted by people who take everything and used well by "
                      "people who choose one thing.",
        "houses": {
            1: "Confidence returns and the world becomes more generous. The risk is that certainty outruns competence.",
            2: "Self-worth rises with material worth, which is pleasant and worth noticing as a dependency.",
            3: "Communication expands and courage becomes easier. Also a year where talking about it substitutes for doing it.",
            4: "A genuine settling. Home stops being a problem to solve. The inner base fills in.",
            5: "Play returns. Creativity, romance and children all feel possible again. One of the happiest transits there is.",
            6: "Optimism meets obligation. The danger is taking on more because it currently feels manageable.",
            7: "Other people become more available and more generous. Good for repair, and a year when a bad partnership can be papered over rather than fixed.",
            8: "Depth becomes bearable. Therapy, occult study and honest examination of the hidden all go well, because there is enough faith to survive looking.",
            9: "Meaning is directly available. Teachers appear. This is the year to ask the large questions, because the answers land.",
            10: "Reputation improves while drive softens. Being well thought of can quietly replace doing the work.",
            11: "Wanting is rewarded, widely. The risk is that the network expands while the intimacy does not.",
            12: "The transcendent becomes accessible. Retreat, pilgrimage and practice all work. Also the classic year of generous, untracked spending.",
        },
    },
    "Rahu": {
        "process": "Craving, inflation and the foreign",
        "philosophy": "Rahu shows you what you have been taught to want and "
                      "hands you an unlimited quantity of it. The suffering is "
                      "not in failing to get it, it is in getting it and "
                      "finding the gap unchanged. The eighteen months are used "
                      "well by anyone who notices what the wanting is standing "
                      "in for.",
        "houses": {
            1: "The identity inflates. You become more than you were and less certain who that is. Reinvention that can be genuine or can be a costume, and it is hard to tell from inside.",
            2: "Hunger attaches to money and to family standing. What you say starts outrunning what you can deliver.",
            3: "Boldness without brakes. Real capability here, and a habit of taking the risk because the risk is exciting rather than correct.",
            4: "The ground moves. Home, mother and the sense of belonging all become unstable, and the restlessness is interior before it is geographic.",
            5: "Desire attaches to creation, romance and speculation. Everything feels like insight. Very little of it is.",
            6: "The appetite goes to work on obstacles, which is the healthiest use of it. Conflict becomes a place to put the hunger.",
            7: "Another person becomes the object of the craving, and is mistaken for the answer to it. The most reliably painful Rahu placement.",
            8: "Obsession with what is concealed: other people's motives, other people's money, the occult. Real depth, real capacity to go too far.",
            9: "A total system is adopted and defended. Conviction arrives faster than understanding.",
            10: "Ambition becomes visible and rapid. The gap between reputation and competence is the thing to manage.",
            11: "Desire is fed on a scale that surprises. This is where Rahu delivers and where it demonstrates most clearly that delivery does not satisfy.",
            12: "The craving turns inward, toward escape. Genuine mystical reach for some; substances, avoidance and lost time for others. Often the same person in the same eighteen months.",
        },
    },
    "Ketu": {
        "process": "Disidentification and subtraction",
        "philosophy": "Ketu removes the meaning from something you were "
                      "invested in, without asking. Nothing is destroyed; the "
                      "charge simply drains out of it. That is disorienting "
                      "and it is not a malfunction. What survives the "
                      "subtraction is what was actually yours.",
        "houses": {
            1: "You lose interest in your own image. Freeing and destabilising in equal measure, and self-doubt here rarely matches actual ability.",
            2: "Money and family stop carrying the weight they did. Detachment that is genuine, and can shade into neglect.",
            3: "Ambition drains out of effort while the skill remains. Things get abandoned at eighty percent.",
            4: "The house stops feeling like home. Emotional withdrawal from the family happens before you decide to.",
            5: "The best placement for practice. Meditation and study go deep because there is no ego investment in the outcome.",
            6: "Opposition stops landing. Old problems dissolve without being solved, which is disconcerting if you were braced for a fight.",
            7: "The other person becomes less real to you. Relationships go quiet rather than wrong, which is harder to see and harder to repair.",
            8: "Genuine access to the hidden. Insight arrives unbidden and unearned. The strongest placement for depth work of any kind.",
            9: "The inherited belief system stops fitting. An inner authority replaces the outer one, and the transition is lonely.",
            10: "Career competence continues while the wanting stops. People drift out of professions here by neglect rather than decision.",
            11: "Gains continue and stop mattering. The circle thins, mostly correctly.",
            12: "The strongest transit for release. Practice, retreat and genuine letting go. Also isolation, if the withdrawal is not chosen consciously.",
        },
    },
}

# ---------------------------------------------------------------------------
# Philosophy: the frames a reading sits inside
# ---------------------------------------------------------------------------

PURUSHARTHA = {
    "dharma": {"houses": [1, 5, 9], "name": "Dharma, purpose",
               "meaning": "What the life is for. Identity, intelligence, "
                          "belief and the sense of a right path."},
    "artha": {"houses": [2, 6, 10], "name": "Artha, means",
              "meaning": "What sustains the life. Resources, work, and the "
                         "practical machinery of getting through."},
    "kama": {"houses": [3, 7, 11], "name": "Kama, desire",
             "meaning": "What the life reaches for. Effort, relationship, and "
                        "the wanting that moves a person at all."},
    "moksha": {"houses": [4, 8, 12], "name": "Moksha, release",
               "meaning": "What the life lets go of. Inner ground, "
                          "transformation, and the eventual undoing of all "
                          "of it."},
}

GUNA = {
    "Sattva": "Clarity, balance, the capacity to see a thing as it is. Too "
              "much and the person becomes detached from ordinary life.",
    "Rajas": "Movement, desire, activity. The engine of the life. Too much "
             "and there is no rest, only more motion.",
    "Tamas": "Inertia, density, groundedness. Necessary for form and sleep. "
             "Too much and nothing moves at all.",
}

TATTVA = {
    "Fire": "Transformation, will, digestion of experience.",
    "Earth": "Form, stability, the capacity to make something last.",
    "Air": "Movement, thought, connection between things.",
    "Water": "Feeling, memory, the capacity to be affected.",
    "Ether": "Space, the medium the rest happens in. Detachment and "
             "spaciousness, or emptiness.",
}

GANA_NOTE = {
    "Deva": "Deva gana. Refined, cooperative, oriented toward harmony and "
            "the benefit of others. Struggles with direct conflict and with "
            "people who do not play fair.",
    "Manushya": "Manushya gana. Human, mixed, ambitious and self-interested "
                "in the ordinary way. The most negotiable temperament, and "
                "the most conflicted.",
    "Rakshasa": "Rakshasa gana. Intense, self-determined, willing to break "
                "form. Not malevolent, but unwilling to be managed, and "
                "genuinely formidable when opposed.",
}


def _layer(chart: Chart, longitude: float, label: str, role: str,
           janma: int) -> dict:
    r = nk.nakshatra_report(longitude, janma)
    return {
        "layer": label,
        "role": role,
        "nakshatra": r["name"],
        "pada": r["pada"],
        "lord": r["lord"],
        "deity": r["deity"],
        "shakti": r["shakti"],
        "gana": r["gana"],
        "guna": r["guna"],
        "tattva": r["tattva"],
        "nadi": r["nadi"],
        "yoni": r["yoni"],
        "symbol": r["symbol"],
        "drive": r["drive"],
        "gift": r["gift"],
        "shadow": r["shadow"],
        "wound": r["wound"],
        "work": r["work"],
        "pada_note": r["pada_note"],
        "pada_navamsa": r["pada_navamsa"],
        "gandanta": r["gandanta"],
    }


def three_layers(chart: Chart) -> list:
    janma = chart.grahas["Moon"].nakshatra
    return [
        _layer(chart, chart.ascendant, "Lagna nakshatra",
               "The operating system. How you meet a room, before thought.",
               janma),
        _layer(chart, chart.grahas["Moon"].longitude, "Moon nakshatra",
               "The actual person. The feeling mind, and what you are like "
               "when nobody is being managed. Classical Jyotish weights this "
               "layer most heavily.", janma),
        _layer(chart, chart.grahas["Sun"].longitude, "Sun nakshatra",
               "The soul's agenda. What the life is for, as distinct from "
               "what it feels like.", janma),
    ]


def division(layers: list) -> str:
    """Name the split between the three layers, if there is one."""
    ganas = {l["gana"] for l in layers}
    tattvas = {l["tattva"] for l in layers}
    lagna, moon, sun = layers

    bits = []
    if lagna["gana"] != moon["gana"]:
        bits.append(
            "You present as %s and you are actually %s. %s That gap is why "
            "people consistently misread you, and why their reaction can feel "
            "like it is aimed at someone else." % (
                lagna["gana"].lower(), moon["gana"].lower(),
                GANA_NOTE[moon["gana"]]))
    if moon["lord"] != sun["lord"]:
        bits.append(
            "The mind answers to %s and the purpose answers to %s. What "
            "settles you and what the life is for are governed by different "
            "grahas, so contentment and progress will not arrive together as "
            "often as you would like." % (moon["lord"], sun["lord"]))
    else:
        bits.append(
            "The mind and the purpose share a lord, %s. What settles you and "
            "what the life is for pull in the same direction, which is "
            "unusual and is worth not wasting." % moon["lord"])
    if len(tattvas) == 3:
        bits.append(
            "All three layers sit in different elements: %s. The self is "
            "genuinely plural rather than merely complicated." %
            ", ".join(sorted(tattvas)))
    elif len(tattvas) == 1:
        bits.append(
            "All three layers share the %s element, so the personality is "
            "unusually consistent. The strength is coherence; the cost is a "
            "narrow range." % list(tattvas)[0].lower())
    return " ".join(bits)


def balances(chart: Chart) -> dict:
    """Guna, tattva, gana and purushartha weighting across the nine grahas."""
    guna, tattva, gana = {}, {}, {}
    for g in chart.grahas.values():
        d = nk.data(g.nakshatra)
        guna[d["guna"]] = guna.get(d["guna"], 0) + 1
        tattva[d["tattva"]] = tattva.get(d["tattva"], 0) + 1
        gana[d["gana"]] = gana.get(d["gana"], 0) + 1

    pura = {}
    for key, meta in PURUSHARTHA.items():
        occupants = [g.name for g in chart.grahas.values()
                     if g.house in meta["houses"]]
        pura[key] = {
            "name": meta["name"], "meaning": meta["meaning"],
            "houses": meta["houses"], "count": len(occupants),
            "grahas": occupants,
        }
    top = max(pura, key=lambda k: pura[k]["count"])
    low = min(pura, key=lambda k: pura[k]["count"])

    return {
        "guna": guna, "tattva": tattva, "gana": gana,
        "guna_notes": {k: GUNA[k] for k in guna},
        "tattva_notes": {k: TATTVA[k] for k in tattva},
        "purushartha": pura,
        "dominant_aim": top,
        "weakest_aim": low,
        "aim_note": "The weight of this chart sits in %s. %d of the nine "
                    "grahas occupy houses %s, the domain of what the life "
                    "%s. The lightest aim is %s, with %d graha%s in houses %s. "
                    "That is not a flaw, it is a description of where the life "
                    "spends itself, and the neglected aim is usually what a "
                    "person eventually comes looking for." % (
                        pura[top]["name"], pura[top]["count"],
                        ", ".join(str(h) for h in pura[top]["houses"]),
                        {"dharma": "is for", "artha": "runs on",
                         "kama": "reaches for",
                         "moksha": "lets go of"}[top],
                        pura[low]["name"], pura[low]["count"],
                        "" if pura[low]["count"] == 1 else "s",
                        ", ".join(str(h) for h in pura[low]["houses"])),
    }


def graha_psychology(chart: Chart) -> list:
    """Each graha as a psychological function, with its condition here."""
    out = []
    for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                 "Saturn", "Rahu", "Ketu"):
        g = chart.grahas[name]
        p = GRAHA_PSYCHE[name]
        strength = graha_strength(chart, name)
        dignity = full_dignity(chart, name)
        n = nk.data(g.nakshatra)

        if strength["score"] >= 60:
            state, state_note = "integrated", (
                "This function is in reasonable shape here. %s" % p["healthy"])
        elif strength["score"] >= 42:
            state, state_note = "workable", (
                "This function works but not effortlessly. Both the healthy "
                "and the wounded expression are available, and which one "
                "shows up depends on load.")
        else:
            state, state_note = "under strain", (
                "This function is compromised in this chart. %s" % p["wounded"])

        out.append({
            "graha": name,
            "function": p["function"],
            "healthy": p["healthy"],
            "wounded": p["wounded"],
            "integration": p["integration"],
            "extra": p.get("father") or p.get("mother"),
            "state": state,
            "state_note": state_note,
            "strength": strength["score"],
            "house": g.house,
            "sign": SIGNS[g.sign],
            "dignity": dignity["label"],
            "nakshatra": g.nakshatra_name,
            "nakshatra_shadow": n["shadow"],
            "colouring": "It operates through %s, whose shadow is: %s" % (
                g.nakshatra_name, n["shadow"][0].lower() + n["shadow"][1:]),
        })
    out.sort(key=lambda x: x["strength"])
    return out


def transit_interior(chart: Chart, positions: list) -> list:
    """The inner experience of each slow transit currently running."""
    out = []
    for p in positions:
        meta = TRANSIT_INTERIOR.get(p["graha"])
        if not meta:
            continue
        out.append({
            "graha": p["graha"],
            "house": p["house"],
            "sign": p["sign"],
            "process": meta["process"],
            "philosophy": meta["philosophy"],
            "interior": meta["houses"][p["house"]],
            "duration": p.get("duration", ""),
            "retrograde": p.get("retrograde", False),
        })
    return out


def profile(chart: Chart, positions: list = None) -> dict:
    layers = three_layers(chart)
    b = balances(chart)
    janma = chart.grahas["Moon"].nakshatra
    moon_n = nk.data(janma)

    return {
        "layers": layers,
        "division": division(layers),
        "balances": b,
        "grahas": graha_psychology(chart),
        "interior": transit_interior(chart, positions or []),
        "janma_nakshatra": NAKSHATRAS[janma],
        "gana_note": GANA_NOTE[moon_n["gana"]],
        "core": "Your Moon is in %s, so the private self runs on this: %s The "
                "gift of it is %s The shadow of it is %s And the work, stated "
                "as plainly as this system states anything: %s" % (
                    NAKSHATRAS[janma],
                    moon_n["drive"],
                    moon_n["gift"][0].lower() + moon_n["gift"][1:],
                    moon_n["shadow"][0].lower() + moon_n["shadow"][1:],
                    moon_n["work"]),
        "caution": "This is a symbolic language for self-reflection, not a "
                   "clinical instrument. It does not diagnose anything. Where "
                   "it describes real suffering, the useful response is a "
                   "person to talk to, not a gemstone.",
    }
