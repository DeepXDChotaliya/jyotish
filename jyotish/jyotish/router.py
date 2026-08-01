"""
Request dispatch, independent of how the request arrived.

One function, `handle()`, takes a method, a path, a query string and a body,
and returns a status, headers and bytes. It knows nothing about sockets, WSGI,
CGI or Apache. `server.py` wraps it in a ThreadingHTTPServer for local use, and
`deploy/index.cgi` wraps it in CGI for shared hosting. Neither duplicates a
single route, which is the whole point: a route fixed once is fixed for both.

Paths arrive already stripped of any prefix. When the app lives in a subfolder
the front end resolves API calls against its own directory, and the CGI wrapper
uses PATH_INFO, so both arrive here as plain "/api/chart".
"""

from __future__ import annotations

import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs

UI = Path(__file__).resolve().parent.parent / "ui"

STATIC = {
    "": ("index.html", "text/html; charset=utf-8"),
    "index.html": ("index.html", "text/html; charset=utf-8"),
    "manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json"),
    "icon.svg": ("icon.svg", "image/svg+xml"),
    "cities.json": ("cities.json", "application/json; charset=utf-8"),
}

JSON_CT = "application/json; charset=utf-8"


def _json(payload, code: int = 200):
    body = json.dumps(payload, default=str).encode("utf-8")
    return code, {"Content-Type": JSON_CT}, body


def _parse_dt(value, default=None):
    if not value:
        return default or datetime.now()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M",
                "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError("Unparseable date %r" % value)


def diagnostics() -> dict:
    """Everything needed to work out why a deployment is broken, in one call.

    Deploying to shared hosting fails in a small number of predictable ways:
    the Python is too old, pyswisseph did not install, or the database
    directory is not writable. Guessing at those over FTP is miserable, so
    this reports all of them at once.
    """
    out = {
        "ok": True,
        "python": sys.version.split()[0],
        "python_ok": sys.version_info >= (3, 9),
        "executable": sys.executable,
        "platform": sys.platform,
        "ui_dir": str(UI),
        "ui_present": (UI / "index.html").exists(),
        "cities_present": (UI / "cities.json").exists(),
        "problems": [],
    }

    if not out["python_ok"]:
        out["problems"].append(
            "Python %s is too old. This needs 3.9 or newer." % out["python"])

    try:
        import swisseph as swe
        out["swisseph"] = getattr(swe, "version", "unknown")
        out["swisseph_ok"] = True
        try:
            swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
            jd = swe.julday(2000, 1, 1, 12.0, swe.GREG_CAL)
            ayan = swe.get_ayanamsa_ut(jd)
            out["ayanamsa_j2000"] = round(ayan, 6)
            # Known good value for Swiss Lahiri at this moment.
            out["ephemeris_ok"] = 23.5 < ayan < 24.2
            if not out["ephemeris_ok"]:
                out["problems"].append(
                    "Swiss Ephemeris imported but returned an implausible "
                    "ayanamsa (%.4f). The install may be damaged." % ayan)
        except Exception as exc:
            out["ephemeris_ok"] = False
            out["problems"].append("Swiss Ephemeris failed to compute: %s" % exc)
    except Exception as exc:
        out["swisseph_ok"] = False
        out["ephemeris_ok"] = False
        out["problems"].append(
            "pyswisseph is not installed or not importable (%s). Install it "
            "with: pip3 install --user pyswisseph" % exc)

    try:
        from zoneinfo import ZoneInfo
        ZoneInfo("Asia/Kolkata")
        out["timezones_ok"] = True
    except Exception as exc:
        out["timezones_ok"] = False
        out["problems"].append(
            "The IANA timezone database is unavailable (%s). Install it with: "
            "pip3 install --user tzdata" % exc)

    try:
        from . import db
        db.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        probe = db.DB_PATH.parent / ".write-probe"
        probe.write_text("ok")
        probe.unlink()
        out["db_dir"] = str(db.DB_PATH.parent)
        out["db_writable"] = True
    except Exception as exc:
        out["db_writable"] = False
        out["problems"].append(
            "Cannot write to the database directory (%s). Saving charts will "
            "fail; everything else still works." % exc)

    if not out["ui_present"]:
        out["problems"].append(
            "ui/index.html is missing next to the code. Upload the whole "
            "project folder, not only the deploy directory.")
    if not out["cities_present"]:
        out["problems"].append(
            "ui/cities.json is missing, so place lookup will fall back to the "
            "server. Regenerate it with: python3 -m jyotish.places")

    out["ok"] = not out["problems"]
    return out


def handle(method: str, path: str, query: str = "", body: bytes = b"",
           read_static=True):
    """Dispatch one request. Returns (status, headers dict, body bytes)."""
    from . import api, db, places

    path = "/" + path.strip("/")
    if path == "/":
        path = "/"

    try:
        # ---- static assets ---------------------------------------------
        if method in ("GET", "HEAD"):
            key = path.strip("/")
            if key in STATIC and read_static:
                name, ctype = STATIC[key]
                target = UI / name
                if not target.exists():
                    if name == "cities.json":
                        data = places.dump_json().encode("utf-8")
                        return 200, {"Content-Type": ctype}, data
                    return _json({"error": "%s is missing on the server. "
                                           "Upload the ui/ folder." % name}, 404)
                return 200, {"Content-Type": ctype}, target.read_bytes()

        params = parse_qs(query or "")

        # ---- GET api ----------------------------------------------------
        if method == "GET":
            if path == "/api/health":
                return _json({"ok": True, "engine": "swiss ephemeris"})
            if path == "/api/diag":
                return _json(diagnostics())
            if path == "/api/places":
                q = (params.get("q") or [""])[0]
                return _json({"results": places.search(q)})
            if path == "/api/clients":
                conn = db.connect()
                return _json({"clients": [dict(r) for r in db.list_clients(conn)]})
            if path.startswith("/api/clients/"):
                conn = db.connect()
                b = db.load_client(conn, int(path.rsplit("/", 1)[1]))
                return _json({
                    "name": b.name, "year": b.year, "month": b.month,
                    "day": b.day, "hour": b.hour, "minute": b.minute,
                    "latitude": b.latitude, "longitude": b.longitude,
                    "place": b.place, "tz_name": b.tz_name,
                    "ayanamsa": b.ayanamsa})
            return _json({"error": "No route %s" % path}, 404)

        # ---- POST api ---------------------------------------------------
        if method == "POST":
            payload = json.loads(body.decode("utf-8")) if body else {}
            birth_payload = payload.get("birth", payload)

            if path == "/api/chart":
                birth = api.birth_from_dict(birth_payload)
                return _json(api.reading(birth, _parse_dt(payload.get("when"))))
            if path == "/api/dasha":
                birth = api.birth_from_dict(birth_payload)
                return _json(api.dasha_branch(birth, payload.get("path", [])))
            if path == "/api/dasha/at":
                birth = api.birth_from_dict(birth_payload)
                return _json(api.dasha_at(birth, _parse_dt(payload.get("when"))))
            if path == "/api/transits":
                birth = api.birth_from_dict(birth_payload)
                return _json(api.transits_at(birth,
                                             _parse_dt(payload.get("when"))))
            if path == "/api/segments":
                birth = api.birth_from_dict(birth_payload)
                return _json(api.segments(
                    birth, _parse_dt(payload.get("start")),
                    _parse_dt(payload.get("end")),
                    int(payload.get("level", 2))))
            if path == "/api/save":
                conn = db.connect()
                birth = api.birth_from_dict(birth_payload)
                return _json({"id": db.save_client(conn, birth)})
            return _json({"error": "No route %s" % path}, 404)

        return _json({"error": "Method %s not allowed" % method}, 405)

    except ValueError as exc:
        return _json({"error": str(exc)}, 400)
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        return _json({"error": str(exc),
                      "hint": "Call /api/diag to check the deployment."}, 500)
