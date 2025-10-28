#!/usr/bin/env bash
# bootstrap for local development
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt
echo "Bootstrap complete"
