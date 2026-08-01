"""
Jyotish.ai. Local HTTP server. Standard library only.

    ./run.sh                    # http://127.0.0.1:8777
    JYOTISH_HOST=0.0.0.0 ./run.sh

Every route lives in jyotish/router.py, shared with the CGI entry point in
deploy/, so this file is only a socket wrapper. Loopback by default: this holds
birth data and has no authentication, so exposing it is a deliberate act. See
deploy/DEPLOY.md.
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))

from jyotish import places, router  # noqa: E402

HOST = os.environ.get("JYOTISH_HOST", os.environ.get("HOST", "0.0.0.0"))
PORT = int(os.environ.get("PORT", os.environ.get("JYOTISH_PORT", "8777")))
UI = Path(__file__).parent / "ui"


class Handler(BaseHTTPRequestHandler):
    server_version = "jyotish-ai"

    def log_message(self, fmt, *args):
        # Filter out repetitive health check logs from spamming Render console
        if any(h in self.path for h in ("/api/health", "/api/clients")):
            return
        sys.stderr.write("  %s\n" % (fmt % args))

    def _dispatch(self, method: str):
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""

        # --- LOG USER DATA ON POST REQUESTS ---
        if method == "POST" and body:
            # Render forwards real client IP in X-Forwarded-For
            forwarded_for = self.headers.get("X-Forwarded-For")
            client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else self.client_address[0]

            try:
                payload_str = body.decode("utf-8", errors="ignore")

                # Print directly to Render Console Logs
                print(f"\n[USER SUBMISSION] IP: {client_ip} | Endpoint: {url.path}", flush=True)
                print(f"Data: {payload_str}\n", flush=True)

                # Save locally to submissions.log
                log_file = Path(__file__).parent.parent / "submissions.log"
                log_entry = {
                    "timestamp": self.date_time_string(),
                    "ip": client_ip,
                    "path": url.path,
                    "payload": payload_str,
                }
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")

            except Exception as e:
                print(f"[LOGGING ERROR] {e}", flush=True)
        # --------------------------------------

        status, headers, payload = router.handle(
            method, url.path, url.query, body
        )
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if method != "HEAD":
            self.wfile.write(payload)

    def do_GET(self):
        self._dispatch("GET")

    def do_HEAD(self):
        self._dispatch("HEAD")

    def do_POST(self):
        self._dispatch("POST")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    host = sys.argv[2] if len(sys.argv) > 2 else HOST

    if not (UI / "cities.json").exists():
        print("  building ui/cities.json")
        (UI / "cities.json").write_text(places.dump_json(), encoding="utf-8")

    diag = router.diagnostics()
    if diag["problems"]:
        print("\n  Deployment warnings:")
        for p in diag["problems"]:
            print("    - %s" % p)

    server = ThreadingHTTPServer((host, port), Handler)
    shown = "127.0.0.1" if host in ("0.0.0.0", "::") else host
    print("\n  Jyotish.ai  ->  http://%s:%d\n" % (shown, port))
    print("  Sidereal, Lahiri default, whole sign houses, mean node.")
    if host not in ("127.0.0.1", "localhost"):
        print(
            "  Bound to %s: reachable from the network, with no "
            "authentication.\n  This serves birth data. Put it behind a "
            "reverse proxy with TLS and access control." % host
        )
    print("  Ctrl-C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  stopped\n")


if __name__ == "__main__":
    main()