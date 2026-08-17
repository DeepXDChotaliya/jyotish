"""
WSGI entry point for Hostinger's "Setup Python App" (Passenger).

Hostinger shared hosting runs Python through Phusion Passenger, which loads a
file called passenger_wsgi.py at the application root and calls the WSGI
callable named `application`. This is the officially supported way to run
Python there, and it is more reliable than raw CGI.

Everything routes through jyotish/router.py -- the same routes the local
server and the CGI entry point use -- so a route is defined once and works
everywhere. The WSGI app serves the static shell (index.html, cities.json,
icon.svg, manifest) as well as /api/*, so it does not matter whether Passenger
is configured to serve static files itself.

Point Setup Python App at:
    Application root      the folder holding this file
    Application startup   passenger_wsgi.py
    Application entrypoint application
    requirements.txt      lists pyswisseph and tzdata
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Passenger builds a virtualenv for the app, so pyswisseph installed from
# requirements.txt is already importable. The extra path nudges below only
# matter for the rare host that installs into ~/.local instead.
for extra in (os.path.expanduser("~/.local/lib"),):
    if os.path.isdir(extra):
        for entry in sorted(os.listdir(extra)):
            sp = os.path.join(extra, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.append(sp)

from jyotish import router  # noqa: E402

# Standard reason phrases so "200 OK" etc. reach the client correctly.
try:
    from http import HTTPStatus
    _REASON = {s.value: s.phrase for s in HTTPStatus}
except Exception:  # pragma: no cover
    _REASON = {200: "OK", 400: "Bad Request", 404: "Not Found",
               405: "Method Not Allowed", 500: "Internal Server Error"}


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/") or "/"
    query = environ.get("QUERY_STRING", "")

    body = b""
    if method == "POST":
        try:
            length = int(environ.get("CONTENT_LENGTH") or 0)
        except (TypeError, ValueError):
            length = 0
        if length:
            body = environ["wsgi.input"].read(length)

    try:
        status, headers, payload = router.handle(method, path, query, body)
    except Exception as exc:  # never let Passenger show its own 500 page
        import json
        import traceback
        traceback.print_exc(file=sys.stderr)
        payload = json.dumps({
            "error": "The Python app crashed inside the request handler.",
            "detail": str(exc),
            "hint": "Open /api/diag to check the deployment.",
        }).encode("utf-8")
        status, headers = 500, {"Content-Type": "application/json; charset=utf-8"}

    reason = _REASON.get(status, "OK")
    out_headers = list(headers.items()) + [
        ("Content-Length", str(len(payload))),
        ("Cache-Control", "no-store"),
    ]
    start_response("%d %s" % (status, reason), out_headers)
    return [payload]
