#!/bin/sh
# Jyotish.ai launcher. Creates the venv on first run.
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  echo "  first run, building the venv"
  python3 -m venv .venv
  .venv/bin/pip install -q --disable-pip-version-check -r requirements.txt
fi
exec .venv/bin/python server.py "$@"
