"""
Core ephemeris layer. Everything sidereal, Lahiri by default.

All longitudes are sidereal ecliptic longitudes in degrees, 0-360, Aries = 0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

import swisseph as swe

# timezonefinder is a large optional dependency. The city table in places.py
# already carries an IANA zone for every entry, so it is only needed when a
# chart is cast from raw coordinates with no zone stated.
_tf = None


def _timezone_finder():
    global _tf
    if _tf is None:
        from timezonefinder import TimezoneFinder
        _tf = TimezoneFinder()
    return _tf

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGNS_SA = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena",
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Graha -> Swiss Ephemeris body id. Ketu is derived from Rahu.
GRAHAS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}

AYANAMSAS = {
    "Lahiri": swe.SIDM_LAHIRI,
    "Raman": swe.SIDM_RAMAN,
    "Krishnamurti": swe.SIDM_KRISHNAMURTI,
    "True Chitra": swe.SIDM_TRUE_CITRA,
    "Yukteshwar": swe.SIDM_YUKTESHWAR,
}

# Combustion orbs in degrees from the Sun. Retrograde orbs in the second slot.
COMBUST_ORB = {
    "Moon": (12.0, 12.0),
    "Mars": (17.0, 17.0),
    "Mercury": (14.0, 12.0),
    "Jupiter": (11.0, 11.0),
    "Venus": (10.0, 8.0),
    "Saturn": (15.0, 15.0),
}

# Special drishti beyond the universal 7th. Values are house distances.
SPECIAL_ASPECTS = {
    "Mars": (4, 7, 8),
    "Jupiter": (5, 7, 9),
    "Saturn": (3, 7, 10),
    "Rahu": (5, 7, 9),
    "Ketu": (5, 7, 9),
}

EXALTATION = {
    "Sun": (0, 10), "Moon": (1, 3), "Mars": (9, 28), "Mercury": (5, 15),
    "Jupiter": (3, 5), "Venus": (11, 27), "Saturn": (6, 20),
}

OWN_SIGNS = {
    "Sun": (4,), "Moon": (3,), "Mars": (0, 7), "Mercury": (2, 5),
    "Jupiter": (8, 11), "Venus": (1, 6), "Saturn": (9, 10),
}


@dataclass
class BirthData:
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int = 0
    latitude: float = 0.0
    longitude: float = 0.0
    place: str = ""
    tz_name: str | None = None  # resolved from coords if left None
    ayanamsa: str = "Lahiri"

    def resolve_tz(self) -> str:
        if self.tz_name:
            return self.tz_name
        tz = _timezone_finder().timezone_at(lat=self.latitude, lng=self.longitude)
        if tz is None:
            raise ValueError(f"Could not resolve a timezone for {self.latitude},{self.longitude}")
        return tz

    def julian_day(self) -> float:
        """Convert local civil time to Julian Day in UT.

        This uses the IANA database via zoneinfo, so historical offsets are
        handled correctly. India's 1942-45 wartime shifts and Sri Lanka's
        1996 and 2006 changes come out right, which a hardcoded +5:30 will not.
        """
        tz = ZoneInfo(self.resolve_tz())
        local = datetime(
            self.year, self.month, self.day,
            self.hour, self.minute, self.second, tzinfo=tz,
        )
        ut = local.astimezone(ZoneInfo("UTC"))
        frac_hour = ut.hour + ut.minute / 60 + ut.second / 3600
        return swe.julday(ut.year, ut.month, ut.day, frac_hour, swe.GREG_CAL)


@dataclass
class Graha:
    name: str
    longitude: float          # sidereal, 0-360
    speed: float              # degrees per day, negative means retrograde
    sign: int                 # 0 = Aries
    degree_in_sign: float
    nakshatra: int            # 0 = Ashwini
    pada: int                 # 1-4
    house: int = 0            # 1-12, filled in by Chart
    retrograde: bool = False
    combust: bool = False
    dignity: str = ""

    @property
    def sign_name(self) -> str:
        return SIGNS[self.sign]

    @property
    def nakshatra_name(self) -> str:
        return NAKSHATRAS[self.nakshatra]


@dataclass
class Chart:
    birth: BirthData
    jd: float
    ascendant: float
    grahas: dict[str, Graha] = field(default_factory=dict)
    house_cusps: list[float] = field(default_factory=list)
    ayanamsa_value: float = 0.0

    @property
    def lagna_sign(self) -> int:
        return int(self.ascendant // 30)

    def sign_of_house(self, house: int) -> int:
        """Whole sign houses: house 1 is the lagna sign."""
        return (self.lagna_sign + house - 1) % 12

    def grahas_in_house(self, house: int) -> list[Graha]:
        return [g for g in self.grahas.values() if g.house == house]

    def aspects_from(self, name: str) -> list[int]:
        """Houses aspected by a graha, as rasi drishti."""
        g = self.grahas.get(name)
        if not g:
            return []
        distances = SPECIAL_ASPECTS.get(name, (7,))
        return [((g.house - 1 + d - 1) % 12) + 1 for d in distances]


def _flags(sidereal: bool = True) -> int:
    f = swe.FLG_SWIEPH | swe.FLG_SPEED
    if sidereal:
        f |= swe.FLG_SIDEREAL
    return f


def _nakshatra_pada(longitude: float) -> tuple[int, int]:
    span = 360 / 27          # 13 deg 20 min
    n = int(longitude // span)
    within = longitude - n * span
    pada = int(within // (span / 4)) + 1
    return n, pada


def _dignity(name: str, sign: int, degree: float) -> str:
    ex = EXALTATION.get(name)
    if ex and sign == ex[0]:
        return "Exalted"
    if ex and sign == (ex[0] + 6) % 12:
        return "Debilitated"
    if sign in OWN_SIGNS.get(name, ()):
        return "Own sign"
    return ""


def compute_chart(birth: BirthData) -> Chart:
    swe.set_sid_mode(AYANAMSAS[birth.ayanamsa], 0, 0)
    jd = birth.julian_day()
    flags = _flags()

    # Ascendant and cusps. 'W' gives whole sign, which is the Parashari default.
    cusps, ascmc = swe.houses_ex(
        jd, birth.latitude, birth.longitude, b"W", flags
    )
    ascendant = ascmc[0]

    chart = Chart(
        birth=birth,
        jd=jd,
        ascendant=ascendant,
        house_cusps=list(cusps),
        ayanamsa_value=swe.get_ayanamsa_ut(jd),
    )

    lagna_sign = int(ascendant // 30)
    sun_long = None

    for name, body in GRAHAS.items():
        values, _ = swe.calc_ut(jd, body, flags)
        lon, speed = values[0] % 360, values[3]
        sign = int(lon // 30)
        nak, pada = _nakshatra_pada(lon)
        g = Graha(
            name=name,
            longitude=lon,
            speed=speed,
            sign=sign,
            degree_in_sign=lon - sign * 30,
            nakshatra=nak,
            pada=pada,
            house=((sign - lagna_sign) % 12) + 1,
            retrograde=speed < 0,
            dignity=_dignity(name, sign, lon - sign * 30),
        )
        chart.grahas[name] = g
        if name == "Sun":
            sun_long = lon

    # Rahu is always retrograde in the mean node model. Ketu mirrors it.
    rahu = chart.grahas["Rahu"]
    rahu.retrograde = True
    ketu_long = (rahu.longitude + 180) % 360
    k_sign = int(ketu_long // 30)
    k_nak, k_pada = _nakshatra_pada(ketu_long)
    chart.grahas["Ketu"] = Graha(
        name="Ketu",
        longitude=ketu_long,
        speed=rahu.speed,
        sign=k_sign,
        degree_in_sign=ketu_long - k_sign * 30,
        nakshatra=k_nak,
        pada=k_pada,
        house=((k_sign - lagna_sign) % 12) + 1,
        retrograde=True,
    )

    # Combustion
    for name, (orb, retro_orb) in COMBUST_ORB.items():
        g = chart.grahas[name]
        sep = abs((g.longitude - sun_long + 180) % 360 - 180)
        g.combust = sep <= (retro_orb if g.retrograde else orb)

    return chart


def transits(when: datetime, ayanamsa: str = "Lahiri") -> dict[str, Graha]:
    """Current or arbitrary-moment graha positions, no birth data needed.

    Pass a timezone-aware datetime. Overlay the result on a natal Chart to read
    gochar, Sade Sati, returns and dasha-transit correlation.
    """
    swe.set_sid_mode(AYANAMSAS[ayanamsa], 0, 0)
    ut = when.astimezone(ZoneInfo("UTC"))
    jd = swe.julday(
        ut.year, ut.month, ut.day,
        ut.hour + ut.minute / 60 + ut.second / 3600,
        swe.GREG_CAL,
    )
    out: dict[str, Graha] = {}
    for name, body in GRAHAS.items():
        values, _ = swe.calc_ut(jd, body, _flags())
        lon, speed = values[0] % 360, values[3]
        sign = int(lon // 30)
        nak, pada = _nakshatra_pada(lon)
        out[name] = Graha(
            name=name, longitude=lon, speed=speed, sign=sign,
            degree_in_sign=lon - sign * 30, nakshatra=nak, pada=pada,
            retrograde=speed < 0,
        )
    r = out["Rahu"]
    kl = (r.longitude + 180) % 360
    ks = int(kl // 30)
    kn, kp = _nakshatra_pada(kl)
    out["Ketu"] = Graha(
        name="Ketu", longitude=kl, speed=r.speed, sign=ks,
        degree_in_sign=kl - ks * 30, nakshatra=kn, pada=kp, retrograde=True,
    )
    return out


def overlay(natal: Chart, moving: dict[str, Graha]) -> dict[str, int]:
    """Which natal house each transiting graha currently occupies."""
    return {
        name: ((g.sign - natal.lagna_sign) % 12) + 1
        for name, g in moving.items()
    }


def sade_sati(natal: Chart, moving: dict[str, Graha]) -> dict:
    """Saturn's position relative to the natal Moon sign."""
    moon_sign = natal.grahas["Moon"].sign
    sat_sign = moving["Saturn"].sign
    offset = (sat_sign - moon_sign) % 12
    phase = {11: "First phase (12th from Moon)",
             0: "Peak phase (over natal Moon)",
             1: "Third phase (2nd from Moon)"}.get(offset)
    return {
        "active": phase is not None,
        "phase": phase,
        "moon_sign": SIGNS[moon_sign],
        "saturn_sign": SIGNS[sat_sign],
        "dhaiya": offset in (3, 7),  # ashtama and kantaka shani
    }


# ---------------------------------------------------------------------------
# Rulership, dignity and strength tables
#
# Everything below is Parashari. It is additive to the ephemeris layer above:
# nothing here touches Swiss Ephemeris, it is all classification on top of the
# longitudes already computed.
# ---------------------------------------------------------------------------

# Sign index -> ruling graha. Traditional rulership only, no outer planets.
SIGN_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]

# Nakshatra index -> Vimshottari lord. The nine repeat three times.
NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
] * 3

# Moolatrikona: (sign index, start degree, end degree). Stronger than own sign.
MOOLATRIKONA = {
    "Sun": (4, 0, 20),
    "Moon": (1, 4, 30),
    "Mars": (0, 0, 12),
    "Mercury": (5, 16, 20),
    "Jupiter": (8, 0, 10),
    "Venus": (6, 0, 15),
    "Saturn": (10, 0, 20),
}

# Natural friendship, BPHS. Anything unlisted is neutral.
NATURAL_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
    "Rahu": {"Venus", "Saturn", "Mercury"},
    "Ketu": {"Mars", "Venus", "Saturn"},
}

NATURAL_ENEMIES = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(),
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
    "Rahu": {"Sun", "Moon", "Mars"},
    "Ketu": {"Sun", "Moon"},
}

# Directional strength: the house where each graha is at full dig bala.
DIG_BALA_HOUSE = {
    "Jupiter": 1, "Mercury": 1,
    "Sun": 10, "Mars": 10,
    "Saturn": 7,
    "Moon": 4, "Venus": 4,
}

# Natural benefics and malefics before any lordship is considered.
NATURAL_BENEFIC = {"Jupiter", "Venus"}
NATURAL_MALEFIC = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

KENDRA = (1, 4, 7, 10)
TRIKONA = (1, 5, 9)
DUSTHANA = (6, 8, 12)
UPACHAYA = (3, 6, 10, 11)
MARAKA = (2, 7)

# Nakshatra -> the deity, gana and a one-line temperament used in readings.
NAKSHATRA_GANA = [
    "Deva", "Manushya", "Rakshasa", "Manushya", "Deva", "Manushya",
    "Deva", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya",
    "Deva", "Rakshasa", "Deva", "Rakshasa", "Deva", "Rakshasa",
    "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Rakshasa",
    "Manushya", "Manushya", "Deva",
]

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima",
]

KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti",
]

VARA_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday",
              "Thursday", "Friday", "Saturday"]
VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def sunrise_jd(jd: float, latitude: float, longitude: float) -> float | None:
    """JD of the sunrise that opens the Vedic day containing jd.

    The vara does not turn at midnight, it turns at sunrise. A 3am birth still
    belongs to the previous weekday. Returns None if the Sun does not rise,
    which happens above the polar circles.
    """
    try:
        res = swe.rise_trans(jd - 1, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER,
                             (longitude, latitude, 0.0), 0.0, 0.0)
    except Exception:
        return None
    tret = res[1] if isinstance(res, tuple) else res
    rise = tret[0] if isinstance(tret, (list, tuple)) else None
    if rise is None:
        return None
    # Walk forward to the last sunrise at or before jd.
    while rise + 1.0 <= jd:
        rise += 1.0
    return rise


def sign_lord(sign: int) -> str:
    return SIGN_LORDS[sign % 12]


def nakshatra_lord(nakshatra: int) -> str:
    return NAKSHATRA_LORDS[nakshatra % 27]


def in_moolatrikona(name: str, sign: int, degree: float) -> bool:
    mt = MOOLATRIKONA.get(name)
    if not mt:
        return False
    s, lo, hi = mt
    return sign == s and lo <= degree < hi


def natural_relation(a: str, b: str) -> str:
    """How graha a natively regards graha b."""
    if a == b:
        return "Own"
    if b in NATURAL_FRIENDS.get(a, ()):
        return "Friend"
    if b in NATURAL_ENEMIES.get(a, ()):
        return "Enemy"
    return "Neutral"


def temporal_relation(house_a: int, house_b: int) -> str:
    """Tatkalika maitri. 2,3,4,10,11,12 from a graha are its temporary friends."""
    distance = ((house_b - house_a) % 12) + 1
    return "Friend" if distance in (2, 3, 4, 10, 11, 12) else "Enemy"


_COMPOUND = {
    ("Friend", "Friend"): "Great friend",
    ("Friend", "Enemy"): "Neutral",
    ("Neutral", "Friend"): "Friend",
    ("Neutral", "Enemy"): "Enemy",
    ("Enemy", "Friend"): "Neutral",
    ("Enemy", "Enemy"): "Great enemy",
    ("Own", "Friend"): "Great friend",
    ("Own", "Enemy"): "Friend",
}


def compound_relation(natural: str, temporal: str) -> str:
    """Panchadha maitri, the five-fold relationship actually used for dignity."""
    return _COMPOUND.get((natural, temporal), "Neutral")


def full_dignity(chart: "Chart", name: str) -> dict:
    """Dignity of one graha including the dispositor relationship.

    Returns the label, a -3..+3 score and the reason, so the UI can always
    show why a placement was called strong or weak rather than asserting it.
    """
    g = chart.grahas[name]
    lord = sign_lord(g.sign)

    if name in ("Rahu", "Ketu"):
        # The nodes own nothing. Classical opinion on their exaltation is split,
        # so they are read through their dispositor rather than by sign dignity.
        disp = chart.grahas.get(lord)
        return {
            "label": "Node",
            "score": 0,
            "reason": (
                "%s owns no sign. It acts through %s, the lord of %s, "
                "which sits in house %d." % (
                    name, lord, SIGNS[g.sign], disp.house if disp else 0)
            ),
            "dispositor": lord,
        }

    ex = EXALTATION.get(name)
    if ex and g.sign == ex[0]:
        deep = abs(g.degree_in_sign - ex[1]) < 1
        return {
            "label": "Exalted",
            "score": 3,
            "reason": "%s is exalted in %s%s. Its significations run at their "
                      "cleanest here." % (
                          name, SIGNS[g.sign],
                          ", within a degree of deep exaltation at %d" % ex[1]
                          if deep else ""),
            "dispositor": lord,
        }
    if ex and g.sign == (ex[0] + 6) % 12:
        return {
            "label": "Debilitated",
            "score": -3,
            "reason": "%s is debilitated in %s. The significations still "
                      "operate but without confidence, and usually late." % (
                          name, SIGNS[g.sign]),
            "dispositor": lord,
        }
    if in_moolatrikona(name, g.sign, g.degree_in_sign):
        return {
            "label": "Moolatrikona",
            "score": 2.5,
            "reason": "%s is in its moolatrikona portion of %s, which is "
                      "stronger than plain own sign." % (name, SIGNS[g.sign]),
            "dispositor": lord,
        }
    if g.sign in OWN_SIGNS.get(name, ()):
        return {
            "label": "Own sign",
            "score": 2,
            "reason": "%s is in its own sign %s. It answers to nobody and "
                      "gives its results directly." % (name, SIGNS[g.sign]),
            "dispositor": lord,
        }

    disp = chart.grahas.get(lord)
    nat = natural_relation(name, lord)
    if disp is None:
        rel = nat
    else:
        rel = compound_relation(nat, temporal_relation(g.house, disp.house))
    score = {"Great friend": 1.5, "Friend": 1, "Neutral": 0,
             "Enemy": -1, "Great enemy": -1.5}.get(rel, 0)
    return {
        "label": rel + "'s sign",
        "score": score,
        "reason": "%s sits in %s, ruled by %s. Naturally %s is %s to %s%s, "
                  "so the placement reads as %s." % (
                      name, SIGNS[g.sign], lord, lord,
                      nat.lower(), name,
                      "" if disp is None else
                      ", and by temporary position %s" % temporal_relation(
                          g.house, disp.house).lower(),
                      rel.lower()),
        "dispositor": lord,
    }


def has_dig_bala(name: str, house: int) -> bool:
    return DIG_BALA_HOUSE.get(name) == house


def graha_strength(chart: "Chart", name: str) -> dict:
    """A transparent 0-100 strength reading with every contributing factor.

    This is not Shadbala. It is a readable proxy built from the factors an
    astrologer checks by eye: dignity, house type, direction, combustion,
    retrogradation, vargottama and the state of the dispositor. Every point
    added or removed is returned as a line of reasoning.
    """
    from . import varga

    g = chart.grahas[name]
    factors = []
    score = 50.0

    dig = full_dignity(chart, name)
    delta = dig["score"] * 8
    if delta:
        score += delta
        factors.append({"factor": dig["label"], "delta": round(delta, 1),
                        "note": dig["reason"]})

    if g.house in KENDRA:
        score += 8
        factors.append({"factor": "Kendra", "delta": 8,
                        "note": "House %d is an angle. Angular grahas act on "
                                "the visible life, not just the inner one." % g.house})
    elif g.house in TRIKONA:
        score += 10
        factors.append({"factor": "Trikona", "delta": 10,
                        "note": "House %d is a trine, the most supportive "
                                "ground a graha can stand on." % g.house})
    elif g.house in DUSTHANA:
        malefic = name in NATURAL_MALEFIC
        d = -4 if malefic else -10
        score += d
        factors.append({"factor": "Dusthana", "delta": d,
                        "note": "House %d is a dusthana. %s" % (
                            g.house,
                            "Malefics tolerate this ground better than benefics "
                            "and can even thrive on it." if malefic else
                            "A benefic here spends itself on loss and repair.")})

    if has_dig_bala(name, g.house):
        score += 10
        factors.append({"factor": "Dig bala", "delta": 10,
                        "note": "%s has full directional strength in house %d." % (
                            name, g.house)})

    if g.combust:
        score -= 15
        factors.append({"factor": "Combust", "delta": -15,
                        "note": "Within the Sun's orb. The graha's own agenda "
                                "is burnt off and it serves the Sun's instead."})

    if g.retrograde and name not in ("Rahu", "Ketu"):
        score += 4
        factors.append({"factor": "Retrograde", "delta": 4,
                        "note": "Retrograde grahas are held to be strong in "
                                "output but unconventional in timing. Results "
                                "arrive out of sequence."})

    if name in varga.vargottama(chart):
        score += 10
        factors.append({"factor": "Vargottama", "delta": 10,
                        "note": "Same sign in D1 and D9. What the rasi promises, "
                                "the navamsa confirms."})

    if g.degree_in_sign < 1 or g.degree_in_sign > 29:
        score -= 6
        factors.append({"factor": "Sandhi", "delta": -6,
                        "note": "At %0.1f degrees the graha is on a sign "
                                "boundary and loses definition." % g.degree_in_sign})

    nl = nakshatra_lord(g.nakshatra)
    nlg = chart.grahas.get(nl)
    if nlg and nl != name:
        if nlg.house in DUSTHANA:
            score -= 5
            factors.append({"factor": "Nakshatra lord in dusthana", "delta": -5,
                            "note": "%s sits in %s, whose lord %s is in house "
                                    "%d. The nakshatra lord colours delivery." % (
                                        name, NAKSHATRAS[g.nakshatra], nl, nlg.house)})
        elif nlg.house in TRIKONA or nlg.house in KENDRA:
            score += 5
            factors.append({"factor": "Nakshatra lord well placed", "delta": 5,
                            "note": "%s sits in %s, whose lord %s is in house "
                                    "%d." % (name, NAKSHATRAS[g.nakshatra], nl,
                                             nlg.house)})

    score = max(0.0, min(100.0, score))
    band = ("Very strong" if score >= 75 else "Strong" if score >= 60
            else "Workable" if score >= 45 else "Weak" if score >= 30
            else "Very weak")
    return {"score": round(score, 1), "band": band, "factors": factors}


def panchanga(chart: "Chart") -> dict:
    """The five limbs of the day, computed from Sun and Moon longitudes."""
    sun = chart.grahas["Sun"].longitude
    moon = chart.grahas["Moon"].longitude
    diff = (moon - sun) % 360

    tithi_index = int(diff // 12)
    paksha = "Shukla" if tithi_index < 15 else "Krishna"
    within = tithi_index % 15
    tithi = "Amavasya" if tithi_index == 29 else TITHI_NAMES[within]

    karana_index = int(diff // 6)
    if karana_index == 0:
        karana = "Kimstughna"
    elif karana_index >= 57:
        karana = ["Shakuni", "Chatushpada", "Naga"][karana_index - 57]
    else:
        karana = KARANA_NAMES[(karana_index - 1) % 7]

    yoga_index = int(((sun + moon) % 360) // (360 / 27))

    # The vara turns at sunrise, not midnight. Anchor on the sunrise that
    # opened this Vedic day and take the weekday from there.
    anchor = sunrise_jd(chart.jd, chart.birth.latitude, chart.birth.longitude)
    weekday = int((anchor if anchor is not None else chart.jd) + 1.5) % 7
    moon_g = chart.grahas["Moon"]

    return {
        "tithi": "%s %s" % (paksha, tithi),
        "tithi_index": tithi_index + 1,
        "paksha": paksha,
        "vara": VARA_NAMES[weekday],
        "vara_lord": VARA_LORDS[weekday],
        "nakshatra": NAKSHATRAS[moon_g.nakshatra],
        "nakshatra_lord": nakshatra_lord(moon_g.nakshatra),
        "pada": moon_g.pada,
        "yoga": YOGA_NAMES[yoga_index],
        "karana": karana,
        "gana": NAKSHATRA_GANA[moon_g.nakshatra],
        "moon_phase": round(diff / 3.6, 1),
    }


def graha_aspects_graha(chart: "Chart", source: str, target: str) -> bool:
    """Rasi drishti: does source cast an aspect onto target's house."""
    s, t = chart.grahas.get(source), chart.grahas.get(target)
    if not s or not t:
        return False
    return t.house in chart.aspects_from(source)


def aspecting_grahas(chart: "Chart", house: int) -> list:
    """Every graha throwing drishti at a given house, with the aspect number."""
    out = []
    for name, g in chart.grahas.items():
        for d in SPECIAL_ASPECTS.get(name, (7,)):
            if ((g.house - 1 + d - 1) % 12) + 1 == house:
                out.append({"graha": name, "aspect": d,
                            "benefic": name in NATURAL_BENEFIC and not g.combust})
    return out
