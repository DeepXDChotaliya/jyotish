# Jyotish.ai

Personal Vedic astrology tool. Single user, runs locally, binds to loopback.
The UI is a phone-first installable web app; the engine is importable on its own.

## Purpose
Compute sidereal charts, dashas, vargas and transits, and keep versioned
consultation notes attached to each chart so patterns can be queried across
years of readings.

## Non-negotiables
- Sidereal only. Lahiri is the default ayanamsa, others are selectable.
- Whole sign houses are the Parashari default. Do not silently switch to
  Placidus. If Bhava Chalit is added it must be an explicit toggle.
- Timezone handling goes through zoneinfo and the IANA database. Never
  hardcode an offset. Historical shifts matter for Indian and Sri Lankan births.
- Rahu uses the mean node. If true node is added it must be a setting, and the
  chart output must state which was used.
- Astronomy comes from Swiss Ephemeris. Do not hand-roll orbital mechanics.

## Layout

Engine, unchanged in spirit:
- `jyotish/engine.py`    ephemeris, Chart and Graha objects, transits, Sade Sati,
                         plus rulership, panchadha maitri, dig bala, panchanga
                         and a transparent strength score
- `jyotish/dasha.py`     Vimshottari. Lazy tree to sookshma, date-to-date output,
                         running chain, flat timeline, per-chain reading
- `jyotish/varga.py`     D1 through D30, pure arithmetic on D1 longitudes
- `jyotish/render.py`    North and South Indian SVG (server side, legacy)
- `jyotish/db.py`        SQLite plus FTS5 over reading notes

Reading layer, added for the console:
- `jyotish/interpret.py` static corpus one: 144 lord-in-house readings, plus
                         house, sign and graha material. No computation here.
- `jyotish/phala.py`     static corpus two: graha-in-sign (108), graha-in-house
                         (108) and plain-language transit results (108, with
                         area / what / watch / helps per cell). Distinct from
                         interpret.py because lordship and occupation are
                         different questions and a full reading needs both.
- `jyotish/lords.py`     house lord analysis, functional nature, verdicts
- `jyotish/yogas.py`     yoga detectors, each returning the placements that
                         triggered it
- `jyotish/gochar.py`    transits, ingress and station dates solved by bisection,
                         Sade Sati windows
- `jyotish/nakshatra.py` the 27 lunar mansions with lord, deity, symbol, gana,
                         yoni, nadi, guna, tattva, varna, body part and shakti,
                         plus a psychological signature per nakshatra. Pada to
                         navamsa, tara bala, gandanta detection, and the
                         nakshatra dispositor chain.
- `jyotish/psyche.py`    the chart as a description of a person. Three layers
                         of self (lagna, Moon, Sun nakshatras), the grahas as
                         psychological functions, guna/tattva/purushartha
                         balance, and the interior of each slow transit.
- `jyotish/character.py` the lagna as the lens. Temperament, the shadow it
                         casts, and growth_edges(): pressured houses that are
                         structurally wired to the 1st, with the behavioural
                         work each implies. Silent where no link exists.
- `jyotish/narrative.py` plain language. life_areas() scores eight areas from
                         natal plus dasha plus transit and says why; whats_next()
                         gives upcoming antardasha changes; sade_sati() dates all
                         three phases.
- `jyotish/ashtakavarga.py` the bindu system. The eight benefic-place tables,
                         Bhinnashtakavarga per graha, Sarvashtakavarga, and
                         kaksha division for transit timing. `verify_tables()`
                         self-checks that the seven BAV totals sum to 337, and
                         every chart re-checks it.
- `jyotish/panchanga.py` the five limbs with exact transition times solved by
                         bisection, sunrise/sunset, rahu kaal, choghadiya,
                         abhijit, plus personal(): the same day read against
                         one natal Moon via tara bala and chandra bala.
- `jyotish/places.py`    curated places first, then 168,339 GeoNames places in
                         `jyotish/data/cities.db` (SQLite, indexed). Alternate
                         names are indexed, so Bombay, Calcutta, Madras, Poona
                         and Saigon resolve. Rebuild with
                         `deploy/build_cities.py`. GeoNames is CC BY 4.0 and
                         the attribution ships in the Reference page; keep it.
- `sources/`             eight scanned books extracted to text
                         (`sources/raw/*.txt`, 2.4M chars), OCR-normalised by
                         `sources/normalise.py`, and indexed into
                         `sources/corpus.json` as 525 attributed passages
                         tagged by topic, graha and house. Regenerate after
                         adding a book.
- `jyotish/classical.py` two things, kept strictly apart. `cite()` returns
                         source passages VERBATIM with the book named, for
                         findings the app computed independently. Techniques
                         are hand-implemented rule sets crisp enough to
                         compute, currently K.N. Rao's four child-timing
                         transit rules. **Never convert mined OCR prose into
                         firing rules.** If a passage cannot be computed it
                         gets quoted, not obeyed.
- `jyotish/shadbala.py`  the real six-fold strength, after B.V. Raman's Graha
                         and Bhava Balas: Sthana, Dig, Kala, Chesta, Naisargika
                         and Drik, plus Bhava Bala and Ishta/Kashta phalas.
                         Raman's own minimum rupas decide "strong". Two
                         approximations are declared in the output rather than
                         hidden: Chesta from speed against mean speed rather
                         than seeghrochcha tables, and Ayana from true
                         declination. `engine.graha_strength` remains as the
                         readable proxy the reading layer uses; shadbala is the
                         classical figure.
- `jyotish/decode.py`    the decoder: mechanism in, lived meaning out. Every
                         insight carries four plain answers, composed from the
                         actual houses, graha and condition: which part of life
                         this touches, what actually happens, what to watch
                         for, what to do. HOUSE_LIFE holds thin/rich/watch/
                         practice per house; GRAHA_METHOD names how each graha
                         fails, so the guidance points the right way. A reading
                         that states a mechanism without a decode is unfinished.
- `jyotish/plain.py`     the layman layer. A 14-term glossary written to be
                         read once and understood, a reading order, and
                         orientation() which writes a chart-specific welcome.
                         House style: gloss every Sanskrit term on first use,
                         say the thing then say what it means for the person,
                         never imply fate.
- `jyotish/synthesis.py` composite insight and the anti-repetition machinery.
                         Signals flatten every layer into comparable facts;
                         rules fire only on two or more signals and must say
                         something no single signal supports; a Ledger claims
                         subjects so a fact is stated once across the whole
                         app; a shape guard stops the same sentence template
                         printing twice with different nouns. Also the 14 life
                         dimensions with their classical recipes.
- `jyotish/api.py`       assembles the JSON payload. Calls everything, computes
                         nothing.

Interfaces:
- `jyotish/router.py`    every route, as a pure function of method, path, query
                         and body. Shared by the local server and the CGI entry
                         point, so a route is fixed once. Also holds
                         `diagnostics()` behind `/api/diag`.
- `server.py`            stdlib HTTP server on 127.0.0.1:8777. A socket wrapper
                         around router.py and nothing more.
- `passenger_wsgi.py`    WSGI entry point for Hostinger's Setup Python App
                         (Passenger). Same router.handle, so a third host with
                         no duplicated routes.
- `deploy/`              build.sh (Passenger and CGI layouts), index.cgi,
                         .htaccess routing, systemd unit, nginx config,
                         requirements-deploy.txt, DEPLOY.md
- `ui/index.html`        the console. Single file, no build step, no CDN.
- `run.sh`               builds the venv on first run, then starts the server
- `app.py`               the older Streamlit UI, still works

## Reading rules

**A rule that restates a lookup is a bug.** `synthesis.compose` may only emit
an insight built from two or more independent signals. "Your 10th lord is
strong" is a lookup; "strong but on 22 bindus with no dasha until 2028" is a
reading. Collect by graha, never per house, or one Venus fact prints twice.

**Say a thing once, across the whole app.** `synthesis.build` runs FIRST in
`api.reading` and returns its Ledger; that ledger is threaded into
`narrative.brief` so a fact claimed by synthesis is dropped from the headlines.
Extend the same way for any new section rather than adding a second dedup.

**Watch template repetition, not just fact repetition.** The shape guard
fingerprints a claim with grahas and numbers stripped out. Five transit
readings sharing one visible scaffold read as generated even when every clause
differs, which is why the transit opener and middle vary per graha. Measured
word-overlap sits around 23% across synthesis plus headlines; much of that is
unavoidable shared vocabulary (bindus, period, average), so read output before
trusting the number.

**State disagreement, never smooth it.** Where the rasi and the divisional
chart conflict, that conflict is the most informative thing in the chart and
must be reported as such. Where two dimensions rest on the same house and
varga, the second cross-references the first rather than repeating it.

**Flag birth-time-sensitive findings.** D10, D24, D30 and D20 change every few
minutes. When `time_accuracy` is not `exact` those dimensions return
`confidence: low` with a note. Never present them as firm.

**No blind `except: pass`, anywhere.** A swallowed error already cost one
live debugging session. Degrade visibly: surface the failure through
`/api/diag`, or set a flag the caller reports. `places.db_error()` and
Shadbala's polar `approximated` flag are the pattern to copy.

**Meaning first, mechanism second.** Every card leads with what it means,
what it affects, what to watch for and what to do. The claim and its evidence
sit behind a "why the chart says this" toggle. A reader must never meet a bindu
count before they know what the passage is about. `insightCard()` in the UI is
the one place this arrangement lives; use it rather than hand-rolling a card.

**Never assert a result without the chain that produced it.** Every verdict,
strength score and yoga in the API carries its own reasoning, and the UI shows
it. If a new detector cannot explain itself, it does not ship.

**Combine the three sources in order: natal, then dasha, then transit.** The
natal chart says what is possible, the dasha says what is currently active, the
transit says when it lands. A transit across a house whose lord is not running
in any period does very little, and anything that reports otherwise is wrong.
`narrative.life_areas` is this rule implemented; keep new features consistent
with it.

**Do not turn circumstance into character.** `character.growth_edges` only
reports a house when it is structurally connected to the lagna. A weak house
with no such link is something to endure and time correctly, not a personal
failing. Never add a code path that assigns blame without that link.

**The psychological material is symbolic, not clinical.** `psyche.py` reads
grahas as functions of a person. It does not diagnose, and the caution it
returns is part of the payload rather than decoration. Do not add anything that
reads as a diagnosis or that discourages someone from seeing a professional.

**Ashtakavarga reductions stay unimplemented.** Trikona and ekadhipatya sodhana
are disputed between schools and the wrong one produces confident nonsense. Raw
bindus are reported. If reductions are ever added they must be a labelled
setting, never a silent default.

**Deploy targets share one router; add hosts, never routes.** `router.handle`
is the single dispatch. `server.py` (sockets), `passenger_wsgi.py` (Hostinger
Setup Python App / Passenger, the recommended host) and `deploy/index.cgi` (CGI
fallback) all wrap it. The Hostinger API and its MCP plugin do DNS, domains, VPS
and static-site deploys only — they cannot upload a Python app into hosting, so
the file upload is always manual. `./deploy/build.sh` produces the Passenger
layout by default, `./deploy/build.sh cgi [folder]` the CGI one.

**The UI must degrade honestly when the backend is absent.** The engine is
Python plus Swiss Ephemeris and cannot run in a browser, so a static host will
serve the page and nothing else. Two rules follow. Never write an empty
`catch {}` around a fetch — a silent failure is worse than an error, and cost
a live debugging session already. And check `content-type` before `r.json()`,
because a static host answers `/api/*` with an HTML 404 and "Unexpected token
<" tells a person nothing.

Place lookup is deliberately backend-free: `ui/cities.json` is generated by
`python -m jyotish.places` and searched in the browser, with the API only as a
fallback. Keep it that way, and regenerate the file when the city table
changes. API paths resolve against `BASE` so subpath hosting works.

**Mobile is a first-class target, not a fallback.** Below 860px the rail is
replaced by a bottom tab bar with a horizontally scrolling section strip, the
form becomes a bottom sheet, and safe-area insets apply. Two rules that keep
biting: declare two-column splits as `.splitgrid` rather than an inline
`grid-template-columns`, because inline styles beat media queries; and keep form
inputs at 16px so iOS does not zoom on focus.

**Reading hierarchy in the UI is semantic, not decorative.** Four classes:
`.hl-title` for the finding, `.t-read` for what it means, `.t-pred` for a dated
prediction (always with a date badge), `.t-fact` for the chart evidence. Accent
colour carries meaning everywhere: mint supports, amber times, rose warns, iris
explains the mechanism. Keep new UI consistent with that, because the whole
point is that a page can be skimmed and trusted at any depth.

## Known gaps, in rough priority order
1. Still untested against Jagannatha Hora. Sanity checks that have been run:
   Lahiri ayanamsa 23°51'25" at 2000-01-01, Sun at Capricorn 10° on that date,
   correct vara across the sunrise boundary, India 1944 resolving to +06:30 and
   Sri Lanka 1996 to +06:30. That is not the same as a full diff. Do one against
   a chart you know cold before trusting a reading.
2. D60 Shastiamsa missing.
5. Nakshatra work still outstanding: ashtakoota compatibility matching between
   two charts, the nakshatra-level Vimshottari sub-lord (KP style), and yoni
   kuta. The 27-nakshatra corpus, pada to navamsa, tara bala, gandanta and the
   dispositor chain are built and verified.
6. Dasha year length: `dasha.YEAR_LENGTHS` holds both conventions and every
   function takes `year_days`, but `api.py` does not pass it and the UI has no
   control for it yet.
7. No birth time rectification tooling.
8. No export. PDF chart sheet for clients would be useful.
9. The city table in `places.py` is hand-built and shallow outside India and
   Sri Lanka. Swap it for a real GeoNames extract when it starts to bite.

## Style
Terse, typed, no framework and no build step. Keep the engine importable and
usable without any UI. The console is vanilla JS served as one file; do not
introduce a bundler for it.
