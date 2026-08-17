# Jyotish.ai

Sidereal chart engine with a reading layer on top of it. Swiss Ephemeris for the
astronomy, Parashari classification for everything above that.

## Run it

**Easiest:** double-click `start.command` in Finder. It builds the environment
on first run, starts the server and opens the browser.

Or in Terminal:

    ./run.sh

First run builds the venv and installs `pyswisseph`. After that it starts in
about two seconds. Then open:

    http://127.0.0.1:8777

To use a different port: `./run.sh 9000`.

The server binds to loopback only. It holds birth data, so it is not reachable
from the network and there is nothing to log into.

The older Streamlit UI still works: `streamlit run app.py`.

**Do not open `ui/index.html` by double-clicking it.** Browsers block a
`file://` page from loading anything, so nothing will work. The app detects
this and tells you, but the fix is always to start the server and use
`http://127.0.0.1:8777`.

## Putting it on a domain

**This is not a static site.** The astronomy comes from Swiss Ephemeris, a
Python extension that cannot run in a browser. Uploading `index.html` on its
own gives you a form that computes nothing.

Full instructions are in [deploy/DEPLOY.md](deploy/DEPLOY.md). On Hostinger, the
best route is **hPanel → Advanced → Setup Python App**, which runs the app
through Passenger:

    ./deploy/build.sh          # writes dist/ in the Passenger layout

Upload the contents of `dist/` to an app folder, then in Setup Python App set
the startup file to `passenger_wsgi.py`, the entry point to `application`, and
install `requirements.txt`. Open `/api/diag` to confirm — it reports the Python
version, whether Swiss Ephemeris imported, whether the ayanamsa computes to a
sane value, and whether the database is writable, so a broken deploy names its
own problem.

If the plan has no Setup Python App button, `./deploy/build.sh cgi jyotish`
produces a CGI layout with `.htaccess` routing instead. For a VPS there is a
systemd unit and an nginx config in `deploy/`. All three run the same routes
from `jyotish/router.py`; the front end resolves API calls against its own
directory, so any of them works at the domain root or in a subfolder without
editing.

None of this can go on a purely static host (Netlify, GitHub Pages, a plain
file upload): Swiss Ephemeris is a Python extension and needs a Python process.

**There is no authentication.** Anything that can reach the app can read and
write every saved chart, and this is birth data. `deploy/DEPLOY.md` shows how to
put basic auth in front of it. The local default stays on loopback for the same
reason.

Place lookup works with or without a backend: the city table ships to the
browser as `ui/cities.json` and is searched locally. Regenerate it after editing
the city list:

    .venv/bin/python -m jyotish.places

## On a phone

The UI is phone-first and installs to the home screen. Open the address on a
device on the same network (start it with a LAN-visible host if you want that,
see the note on `HOST` in `server.py`), then use Add to Home Screen. It runs
standalone with no browser chrome, a bottom tab bar, a scrolling section strip
and safe-area insets.

Bear in mind what that means: the server listens on loopback by default
precisely because this is birth data. Exposing it to a network is a decision to
make deliberately, not a default to inherit.

## What the console shows

**Overview** — the landing page, and the main findings first: who this is, what
is working, what is under strain, what is running, what is coming with a date on
it, and what to work on. Each finding carries the chart evidence that produced
it underneath, in mono, so nothing has to be taken on trust. Colour is semantic
throughout the app: mint supports, amber is a dated prediction, rose warns, iris
explains the mechanism.

**Right now** — the plain-language page. What the running period is doing, then
all eight areas of life scored from three sources at once: the natal chart (what
is possible), the dasha (what is currently active) and the transits (when it
lands). Each area opens to show which transit is crossing it, what to watch for
and why, what helps, and the chart reasoning underneath. Then what changes at
the next period boundary, and Sade Sati with all three phases dated.

**Character and the work** — the lagna as the vantage point the whole chart is
experienced from: temperament, the shadow those same traits cast, constitution,
and where the lagna lord keeps putting you. Then the part that matters: any
pressured house that is *structurally wired to the 1st* — its lord sits in your
1st, or your lagna lord has gone into it, or a graha in your 1st rules it — with
the trait in play and specific behavioural work. Where a house is weak but has
no such link, the page says so plainly rather than inventing a character flaw.

**Psyche** — the chart read as a description of a person rather than a set of
events. Three layers of self: the lagna nakshatra is how you meet a room, the
Moon nakshatra is who you actually are, the Sun nakshatra is what the life is
for. Where those three disagree, the page says so, because naming that division
is usually the most useful thing a reading does. Then the nine grahas as
psychological functions with their condition here, the guna, tattva and
purushartha weighting of the chart, and what each slow transit is doing on the
inside rather than only in events.

**Nakshatras** — the janma nakshatra in full: shakti, deity, gana, yoni, nadi,
guna, tattva, body part, and its gift, shadow, wound and work. Every graha by
nakshatra with its pada, the pada's navamsa and pada lord, and the tara counted
from your birth star. The nakshatra dispositor chain for each graha, followed
until it closes on itself, which is where that graha's results actually land.
The nine-fold tara bala cycle, and all twenty-seven coloured by tara.

The rasi grid, running dasha and panchanga also sit on the Overview page.

**Houses and lords** — which sign falls on each house, who rules it, where that
ruler has gone, its dignity, strength and functional nature. Open any house for
the full chain: the classical reading for that lord in that house, what the sign
does to it, the condition of the lord factor by factor, occupants, aspects, and
how the verdict was reached.

**Grahas** — position, dignity, strength breakdown, and three separate readings
per graha because they answer three different questions: what it does in the
house it occupies, what the sign does to its method, and what it delivers for
the houses it rules.

**Yogas** — Raja, Dhana, Pancha Mahapurusha, Viparita, lunar and the common
doshas. Each one reports the placements that triggered it, so you can check it
against the chart by eye instead of taking it on faith.

**Dashas** — Vimshottari date to date, four levels deep. Click any period to
open the level inside it. The chain is read against the chart: what each dasha
lord delivers from where it sits, and whether the sub-lord sits in a supportive
or obstructed position from the lord above it.

**Segments** — a flat dated scan of any window at any level. Use it to find a
period without walking the tree.

**Transits** — where the grahas are now against the natal houses, contacts to
natal positions within three degrees, the Sade Sati window with real entry and
exit dates, and a dated list of upcoming ingresses and stations. Every transit
is written in plain language — what part of life it touches, what tends to
happen, where the difficulty shows up and why, what actually helps — with the
Sanskrit reasoning folded away behind a toggle. Every transiting graha also
carries its tara counted from your birth star, because a graha crossing your
Vipat or Vadha tara behaves quite differently from the same graha in Sampat.
Ingress dates are solved against the ephemeris by bisection, so retrograde loops
give all three real crossings rather than one averaged guess.

**Ashtakavarga** — the bindu system. Not how strong a graha is, but how much
support each sign actually has, pooled from all eight reference points.
Bhinnashtakavarga per graha, Sarvashtakavarga across twelve signs summing to
337, and kaksha readings at 3°45 resolution: a graha crossing a kaksha whose
owner gave it a bindu produces results, and crossing an empty one it produces
very little however dramatic the transit looks. The table integrity
self-checks on every chart.

Trikona and ekadhipatya sodhana are deliberately not applied. The reduction
rules are disputed between schools and the wrong one produces confident
nonsense, so raw bindus are shown.

**Divisional charts** — D2 through D30, with vargottama flagged.

## Place lookup

Type a city, a state or a country into the place field and pick from the list.
It fills coordinates and the IANA zone. The table is offline and weighted to
India and Sri Lanka. Coordinates stay editable if you have exact ones.

Timezones resolve through `zoneinfo`, so historical offsets come out right: an
Indian birth in 1944 gets +06:30, a Sri Lankan birth in mid-1996 gets +06:30.

## Date of birth vs date of reading

The birth date and time cast the chart. The **Read for date** field, which
defaults to today, is the moment the dashas and transits are computed for. Move
it to read the same chart at any point in its life.

## Ephemeris precision

`pyswisseph` falls back to the built-in Moshier analytical model when no data
files are present, accurate to roughly one arcsecond over the last few
millennia. That is well past what Jyotish needs. For the full Swiss files,
download them and call `swe.set_ephe_path()` at the top of `engine.py`.

## Verify before you use it

Sanity checks that have been run: Lahiri ayanamsa 23°51'25" at 2000-01-01, Sun
at Capricorn 10° on that date, the vara turning at sunrise rather than midnight,
and the historical timezone shifts above. Dasha arithmetic has been checked by
hand against the proportional rule at all four levels.

None of that is a full diff against Jagannatha Hora. Compute one chart you
already know cold and check in this order: ayanamsa value, lagna degree, Moon
longitude, nakshatra and pada, dasha balance at birth, then navamsa.

## Using the engine without the UI

```python
from jyotish.engine import BirthData, compute_chart
from jyotish import character, dasha, lords, narrative, yogas

b = BirthData(name="X", year=1988, month=6, day=14, hour=7, minute=45,
              latitude=15.4909, longitude=73.8278, tz_name="Asia/Kolkata")
c = compute_chart(b)

for row in lords.lord_map(c):
    print(row["summary"], row["dignity"], row["strength"])

for y in yogas.all_yogas(c):
    print(y["name"], "-", y["reason"])

for p in dasha.running_chain(c):
    print(p["level_name"], p["lord"], p["start_date"], "to", p["end_date"])

for area in narrative.life_areas(c):          # worst first
    print(area["name"], area["status"], "-", area["headline"])

for edge in character.growth_edges(c):        # only lagna-linked houses
    print(edge["area"], "->", edge["work"])
```

## API

Everything the UI does is a JSON call, so the engine is scriptable.

| Route | Body |
|---|---|
| `GET /api/places?q=` | city, state or country search |
| `POST /api/chart` | `{birth, when}` — the whole reading |
| `POST /api/dasha` | `{birth, path}` — one level below `path` |
| `POST /api/dasha/at` | `{birth, when}` — the chain at a moment |
| `POST /api/transits` | `{birth, when}` |
| `POST /api/segments` | `{birth, start, end, level}` |
| `POST /api/save` / `GET /api/clients` | saved birth records |

The database lives at `~/.jyotish/practice.db`. Charts are recomputable from
birth data, so only birth data and your notes are stored.
