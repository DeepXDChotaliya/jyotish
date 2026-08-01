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
- `jyotish/places.py`    offline city table (281 entries), name to coordinates
                         and IANA zone
- `jyotish/api.py`       assembles the JSON payload. Calls everything, computes
                         nothing.

Interfaces:
- `jyotish/router.py`    every route, as a pure function of method, path, query
                         and body. Shared by the local server and the CGI entry
                         point, so a route is fixed once. Also holds
                         `diagnostics()` behind `/api/diag`.
- `server.py`            stdlib HTTP server on 127.0.0.1:8777. A socket wrapper
                         around router.py and nothing more.
- `deploy/`              CGI entry point, .htaccess routing, build script,
                         systemd unit, nginx config, DEPLOY.md
- `ui/index.html`        the console. Single file, no build step, no CDN.
- `run.sh`               builds the venv on first run, then starts the server
- `app.py`               the older Streamlit UI, still works

## Reading rules

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
2. Shadbala is not implemented. `engine.graha_strength` is a readable proxy that
   returns its own factors, not a substitute for the real six-fold calculation.
3. D60 Shastiamsa missing.
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
