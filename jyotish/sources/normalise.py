"""
Normalise OCR text from the scanned source books.

The scans are readable but noisy in consistent, fixable ways: "aspected" comes
out "aspeeted", "(a)" as "Ca)", and every line wraps mid sentence. Naive
grepping therefore finds almost nothing and gives the false impression the
text is unusable. It is not; it just needs cleaning first.

Only mechanical substitutions are applied. Nothing here guesses at meaning,
because a wrong guess silently becomes a false astrological rule downstream.
"""

import re

# Consistent OCR confusions in these particular scans.
FIXES = [
    (r"\baspeeted\b", "aspected"), (r"\baspeet\b", "aspect"),
    (r"\baspeets\b", "aspects"), (r"\bAspeet\b", "Aspect"),
    (r"\bC([a-h])\)", r"(\1)"),          # Ca) -> (a)
    (r"\bJ\s*upiter\b", "Jupiter"), (r"\bSatum\b", "Saturn"),
    (r"\bSaturo\b", "Saturn"), (r"\bMoou\b", "Moon"),
    (r"\bVeuus\b", "Venus"), (r"\bMercuty\b", "Mercury"),
    (r"\blagoa\b", "lagna"), (r"\bLagoa\b", "Lagna"),
    (r"\bnakshatta\b", "nakshatra"), (r"\bdasa\b", "dasha"),
    (r"\bhoroseope\b", "horoscope"), (r"\bplaoet\b", "planet"),
    (r"\btransil\b", "transit"), (r"\bhonse\b", "house"),
    (r"\bfiflh\b", "fifth"), (r"\bteoth\b", "tenth"),
    (r"\bseveoth\b", "seventh"), (r"\bnioth\b", "ninth"),
    (r"[’‘]", "'"), (r"[“”]", '"'),
]


def normalise(text: str) -> str:
    for pat, rep in FIXES:
        text = re.sub(pat, rep, text)
    # Rejoin lines wrapped mid sentence: a line not ending in sentence
    # punctuation, followed by a lowercase start, is one sentence.
    text = re.sub(r"([a-z,;])\n([a-z])", r"\1 \2", text)
    # Drop bare page numbers on their own line.
    text = re.sub(r"\n\s*\d{1,3}\s*\n", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


def sentences(text: str):
    for s in re.split(r"(?<=[.;])\s+", normalise(text)):
        s = " ".join(s.split())
        if 40 <= len(s) <= 400:
            yield s
