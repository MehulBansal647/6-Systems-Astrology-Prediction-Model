#!/usr/bin/env bash
# Reproduce the six-culture chart from BIRTH_INPUT.json.
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || { python3.12 -m venv .venv && .venv/bin/pip install -r requirements.lock; }
[ -d js/node_modules/iztro ] || (cd js && npm ci)
mkdir -p ephe
for f in sepl_18.se1 semo_18.se1; do
  [ -f "ephe/$f" ] || curl -sSfL -o "ephe/$f" "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/$f"
done
cd src
../.venv/bin/python build_dataset.py
../.venv/bin/python synthesize.py > /dev/null
../.venv/bin/python report.py
