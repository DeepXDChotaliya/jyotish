#!/bin/sh
# Double-click this file in Finder to start Jyotish.ai.
# It builds the venv on first run, starts the server, and opens the browser.
cd "$(dirname "$0")"

PORT=8777
# If something is already serving on the port, just open it.
if curl -s -m 2 -o /dev/null "http://127.0.0.1:$PORT/api/health"; then
  echo "  Jyotish.ai is already running."
  open "http://127.0.0.1:$PORT"
  exit 0
fi

if [ ! -d .venv ]; then
  echo "  First run: building the environment. This takes a minute."
  python3 -m venv .venv
  .venv/bin/pip install -q --disable-pip-version-check pyswisseph tzdata
fi

# Open the browser once the server answers, then hand the terminal to the server.
( for i in $(seq 1 40); do
    if curl -s -m 1 -o /dev/null "http://127.0.0.1:$PORT/api/health"; then
      open "http://127.0.0.1:$PORT"; exit 0
    fi
    sleep 0.5
  done ) &

echo "  Starting Jyotish.ai on http://127.0.0.1:$PORT"
echo "  Close this window or press Ctrl-C to stop."
exec .venv/bin/python server.py "$PORT"
