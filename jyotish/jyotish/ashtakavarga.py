"""
Ashtakavarga. The bindu system.

Every other technique in this package asks whether a graha is strong. This one
asks a different and more useful question: how much support does a given sign
have, pooled from all eight reference points at once. A graha can be weak by
dignity and still deliver, if the sign it stands in is well supplied with
bindus, and a strong graha in a starved sign consistently underperforms.

Three layers, in the order they are used:

  Bhinnashtakavarga   One table per graha. Each of the eight reference points
  (BAV)               (the seven grahas plus the lagna) contributes a bindu to
                      certain houses counted from itself. Sun's table totals 48
                      bindus, Moon's 49, and so on.

  Sarvashtakavarga    The seven BAV tables added together, giving a score out
  (SAV)               of 337 spread across twelve signs. This is the single
                      most practical number in the system: it says which parts
                      of the life have reserves and which do not.

  Kaksha              Each sign divides into eight parts of 3 degrees 45, one
                      per reference point in a fixed order. A transiting graha
                      passing through a kaksha whose owner gave it a bindu
                      produces results; through an empty kaksha it does not.
                      This is the sharpest transit timing tool in Jyotish and
                      it costs almost nothing to compute.

The tables below are the standard BPHS set. The arithmetic self-checks: the
seven BAV totals must sum to exactly 337, and `verify_tables()` asserts it.

Not implemented, deliberately: trikona and ekadhipatya sodhana. The reduction
rules are disputed between schools and applying the wrong one produces
confident nonsense. Raw bindus are reported instead.
"""

from __future__ import annotations

from .engine import SIGNS, Chart, sign_lord

# The eight reference points, in the fixed order used for kaksha division.
REFERENCES = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon",
              "Lagna"]

# Graha whose ashtakavarga is being built -> reference point -> the houses,
# counted from that reference point, which receive a bindu.
BENEFIC_PLACES = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [3, 6, 10, 11],
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Lagna": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Lagna": [1, 3, 4, 6, 10, 11],
    },
}

BAV_TOTALS = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
              "Jupiter": 56, "Venus": 52, "Saturn": 39}

SAV_TOTAL = 337

# Sarvashtakavarga bands, as taught. The thresholds are conventional rather
# than computed, and are stated as bands rather than verdicts.
SAV_BANDS = [
    (32, "Very strong", "mint",
     "Well above average. This part of life has reserves and recovers from "
     "setbacks without much help."),
    (28, "Strong", "mint",
     "Above average. Matters here tend to go the person's way over time."),
    (25, "Average", "",
     "Around the mean of 28. Neither supported nor starved; outcomes here "
     "follow the dasha rather than the natal promise."),
    (22, "Weak", "amber",
     "Below average. This area needs effort disproportionate to the result, "
     "and does not absorb shocks well."),
    (0, "Very weak", "rose",
     "Well below average. Structurally short of support. Avoid making this "
     "area carry the weight of the life."),
]


def verify_tables() -> dict:
    """Self-check. The seven BAV totals must sum to exactly 337."""
    totals = {g: sum(len(v) for v in refs.values())
              for g, refs in BENEFIC_PLACES.items()}
    grand = sum(totals.values())
    mismatch = {g: (totals[g], BAV_TOTALS[g])
                for g in totals if totals[g] != BAV_TOTALS[g]}
    return {"totals": totals, "grand": grand, "expected": SAV_TOTAL,
            "ok": grand == SAV_TOTAL and not mismatch,
            "mismatch": mismatch}


def _reference_signs(chart: Chart) -> dict:
    """The sign index each reference point occupies. Lagna counts as a point."""
    refs = {name: chart.grahas[name].sign
            for name in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                         "Saturn")}
    refs["Lagna"] = chart.lagna_sign
    return refs


def bhinna(chart: Chart, graha: str) -> list:
    """One graha's ashtakavarga: bindus per sign, indexed 0 = Aries."""
    refs = _reference_signs(chart)
    bindus = [0] * 12
    for reference, houses in BENEFIC_PLACES[graha].items():
        base = refs[reference]
        for h in houses:
            bindus[(base + h - 1) % 12] += 1
    return bindus


def bhinna_detail(chart: Chart, graha: str) -> dict:
    """Bindus per sign plus which reference point supplied each one."""
    refs = _reference_signs(chart)
    contributors = [[] for _ in range(12)]
    for reference, houses in BENEFIC_PLACES[graha].items():
        base = refs[reference]
        for h in houses:
            contributors[(base + h - 1) % 12].append(reference)
    bindus = [len(c) for c in contributors]
    lagna = chart.lagna_sign
    return {
        "graha": graha,
        "total": sum(bindus),
        "expected_total": BAV_TOTALS[graha],
        "by_sign": bindus,
        "contributors": contributors,
        "by_house": [bindus[(lagna + h - 1) % 12] for h in range(1, 13)],
        "own_sign_bindus": bindus[chart.grahas[graha].sign],
        "own_house": chart.grahas[graha].house,
        "note": _bhinna_note(chart, graha, bindus),
    }


def _bhinna_note(chart: Chart, graha: str, bindus: list) -> str:
    g = chart.grahas[graha]
    here = bindus[g.sign]
    if here >= 5:
        quality = ("well supplied. %s is standing on supportive ground and "
                   "will deliver more than its dignity alone suggests" % graha)
    elif here >= 4:
        quality = "adequately supplied, so %s performs about as expected" % graha
    elif here >= 2:
        quality = ("thinly supplied. %s underperforms its dignity here, and "
                   "its dasha tends to promise more than it pays" % graha)
    else:
        quality = ("almost empty. %s has very little to work with in this "
                   "sign, whatever its dignity says" % graha)
    return ("%s sits in %s with %d bindu%s of its own eight. That is %s." % (
        graha, SIGNS[g.sign], here, "" if here == 1 else "s", quality))


def sarva(chart: Chart) -> dict:
    """Sarvashtakavarga: the seven tables summed, by sign and by house."""
    per_graha = {g: bhinna(chart, g) for g in BENEFIC_PLACES}
    by_sign = [sum(per_graha[g][s] for g in per_graha) for s in range(12)]
    lagna = chart.lagna_sign

    houses = []
    for h in range(1, 13):
        s = (lagna + h - 1) % 12
        score = by_sign[s]
        band, colour, meaning = _band(score)
        houses.append({
            "house": h, "sign": SIGNS[s], "sign_index": s,
            "bindus": score, "band": band, "colour": colour,
            "meaning": meaning,
            "lord": sign_lord(s),
            "per_graha": {g: per_graha[g][s] for g in per_graha},
        })

    total = sum(by_sign)
    ranked = sorted(houses, key=lambda x: -x["bindus"])
    return {
        "by_sign": by_sign,
        "houses": houses,
        "total": total,
        "expected_total": SAV_TOTAL,
        "valid": total == SAV_TOTAL,
        "average": round(total / 12, 1),
        "strongest": ranked[:3],
        "weakest": ranked[-3:][::-1],
        "kendra_total": sum(h["bindus"] for h in houses if h["house"] in (1, 4, 7, 10)),
        "trikona_total": sum(h["bindus"] for h in houses if h["house"] in (1, 5, 9)),
        "dusthana_total": sum(h["bindus"] for h in houses if h["house"] in (6, 8, 12)),
        "note": _sarva_note(houses, total),
    }


def _band(score: int):
    for threshold, name, colour, meaning in SAV_BANDS:
        if score >= threshold:
            return name, colour, meaning
    return SAV_BANDS[-1][1], SAV_BANDS[-1][2], SAV_BANDS[-1][3]


def _sarva_note(houses: list, total: int) -> str:
    ranked = sorted(houses, key=lambda x: -x["bindus"])
    best, worst = ranked[0], ranked[-1]
    return (
        "Across 337 bindus the average house holds 28. Your strongest is the "
        "%s at %d, in %s, and your weakest is the %s at %d, in %s. Read that "
        "as reserves rather than as fate: the strong house absorbs difficulty "
        "and recovers, the weak one does not, and a dasha touching the weak "
        "house will feel harder than the same dasha touching the strong one." % (
            _ord(best["house"]), best["bindus"], best["sign"],
            _ord(worst["house"]), worst["bindus"], worst["sign"]))


def _ord(n: int) -> str:
    return "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}.get(
        n if n < 20 else n % 10, "th"))


# ---------------------------------------------------------------------------
# Kaksha. Transit timing at 3 degrees 45 resolution.
# ---------------------------------------------------------------------------

KAKSHA_SPAN = 30 / 8      # 3 degrees 45 minutes


def kaksha_of(longitude: float) -> dict:
    """Which of the eight kakshas a longitude falls in, and whose it is."""
    sign = int(longitude // 30) % 12
    within = longitude - int(longitude // 30) * 30
    index = min(int(within // KAKSHA_SPAN), 7)
    return {
        "sign": SIGNS[sign], "sign_index": sign,
        "index": index + 1,
        "owner": REFERENCES[index],
        "from_degree": round(index * KAKSHA_SPAN, 4),
        "to_degree": round((index + 1) * KAKSHA_SPAN, 4),
    }


def kaksha_transit(chart: Chart, graha: str, longitude: float) -> dict:
    """Whether a transiting graha is in a kaksha that gave it a bindu.

    The rule is simple and unusually reliable: a graha crossing a kaksha whose
    owner contributed a bindu to that sign in the graha's own ashtakavarga
    produces results. Crossing an empty kaksha, it produces very little,
    however dramatic the transit looks on paper.
    """
    if graha not in BENEFIC_PLACES:
        return {}
    k = kaksha_of(longitude)
    detail = bhinna_detail(chart, graha)
    contributors = detail["contributors"][k["sign_index"]]
    has_bindu = k["owner"] in contributors
    lagna = chart.lagna_sign
    house = ((k["sign_index"] - lagna) % 12) + 1

    return {
        "graha": graha,
        "sign": k["sign"],
        "house": house,
        "kaksha": k["index"],
        "kaksha_owner": k["owner"],
        "kaksha_range": "%.2f to %.2f degrees" % (k["from_degree"],
                                                  k["to_degree"]),
        "has_bindu": has_bindu,
        "sign_bindus": detail["by_sign"][k["sign_index"]],
        "contributors": contributors,
        "note": (
            "%s is crossing the %s kaksha of %s, and %s did give a bindu here. "
            "Transits through a kaksha with a bindu deliver; this stretch "
            "should produce something visible in %s matters." % (
                graha, k["owner"], k["sign"], k["owner"], _ord(house))
            if has_bindu else
            "%s is crossing the %s kaksha of %s, and %s gave no bindu here. "
            "Transits through an empty kaksha tend to pass without result, "
            "however significant the transit looks otherwise. Expect little "
            "in %s matters until it moves on." % (
                graha, k["owner"], k["sign"], k["owner"], _ord(house))),
    }


def transit_kakshas(chart: Chart, positions: list) -> list:
    """Kaksha reading for every transiting graha that has an ashtakavarga."""
    out = []
    for p in positions:
        if p["graha"] not in BENEFIC_PLACES:
            continue
        out.append(kaksha_transit(chart, p["graha"], p["longitude"]))
    return out


def report(chart: Chart, positions: list = None) -> dict:
    """Everything the Ashtakavarga page needs."""
    bavs = {g: bhinna_detail(chart, g) for g in BENEFIC_PLACES}
    s = sarva(chart)
    return {
        "verification": verify_tables(),
        "bhinna": bavs,
        "sarva": s,
        "kakshas": transit_kakshas(chart, positions or []),
        "references": REFERENCES,
        "explainer": (
            "Each graha has its own table of eight contributors: the seven "
            "grahas and the lagna. A contributor gives a bindu to certain "
            "houses counted from where it sits. Add all seven tables together "
            "and you get the Sarvashtakavarga, 337 bindus spread over twelve "
            "signs, averaging 28 a sign. Signs above the average have reserves; "
            "signs below it do not."),
    }
