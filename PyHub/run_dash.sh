#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v python3 >/dev/null 2>&1; then
  python3 dash.py
else
  echo "Python 3 is required to run PyHub dashboard." >&2
  exit 1
fi
