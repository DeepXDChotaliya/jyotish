#!/bin/sh
# Jyotish.ai launcher. Creates the venv on first run.
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  echo "  first run, building the venv"
  python3 -m venv .venv
  .venv/bin/pip install -q --disable-pip-version-check pyswisseph tzdata
fi
# Self-heal: if swisseph is missing from an existing venv, install it.
if ! .venv/bin/python -c "import swisseph" 2>/dev/null; then
  echo "  installing missing dependencies"
  .venv/bin/pip install -q --disable-pip-version-check pyswisseph tzdata
fi
exec .venv/bin/python server.py "$@"
