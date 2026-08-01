#!/usr/bin/env python3
"""
CGI entry point for shared hosting (Hostinger, cPanel, LiteSpeed, Apache).

Shared hosts will not keep a long-running process alive, so the standalone
server in server.py is not an option there. CGI is: the web server executes
this file per request, it dispatches through jyotish/router.py -- the same
routes the local server uses -- and exits.

Upload the whole project, point .htaccess at this file, and make it executable
(chmod 755). If anything is wrong, open  <your-folder>/api/diag  in a browser
and it will tell you exactly what.
"""

import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # the project folder, one level up
sys.path.insert(0, ROOT)

# Shared hosts install user packages here. Add the usual locations so
# `pip3 install --user pyswisseph` is enough, with no virtualenv.
for extra in (
    os.path.join(ROOT, ".venv", "lib"),
    os.path.expanduser("~/.local/lib"),
):
    if os.path.isdir(extra):
        for entry in sorted(os.listdir(extra)):
            sp = os.path.join(extra, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)


def _out(status, headers, body):
    sys.stdout.write("Status: %s\r\n" % status)
    for k, v in headers.items():
        sys.stdout.write("%s: %s\r\n" % (k, v))
    sys.stdout.write("Cache-Control: no-store\r\n")
    sys.stdout.write("Content-Length: %d\r\n\r\n" % len(body))
    sys.stdout.flush()
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def main():
    method = os.environ.get("REQUEST_METHOD", "GET").upper()
    # PATH_INFO is the part after this script, which is what the router wants.
    # Some LiteSpeed configurations leave it empty and put everything in
    # REQUEST_URI instead, so fall back to that and strip the script prefix.
    path = os.environ.get("PATH_INFO", "")
    if not path:
        uri = os.environ.get("REQUEST_URI", "/").split("?")[0]
        script = os.environ.get("SCRIPT_NAME", "")
        path = uri[len(script):] if script and uri.startswith(script) else uri
    query = os.environ.get("QUERY_STRING", "")

    body = b""
    if method == "POST":
        try:
            length = int(os.environ.get("CONTENT_LENGTH") or 0)
        except ValueError:
            length = 0
        if length:
            body = sys.stdin.buffer.read(length)

    from jyotish import router
    status, headers, payload = router.handle(method, path, query, body)
    _out(status, headers, payload)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        sys.stderr.write(tb)
        msg = (
            '{"error":"The Python entry point crashed before routing. This is '
            'almost always a missing dependency or a wrong Python path.",'
            '"hint":"Run: pip3 install --user pyswisseph tzdata",'
            '"traceback":%s}' % __import__("json").dumps(tb)
        ).encode("utf-8")
        _out(500, {"Content-Type": "application/json; charset=utf-8"}, msg)
