#!/usr/bin/env bash
source ../.venv/bin/activate
cd "$(dirname "$0")"

if [ -d venv ]; then
    source venv/bin/activate
fi

(sleep 2 && xdg-open http://127.0.0.1:8000) &

python3 -m uvicorn api:app --reload
