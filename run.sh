#!/usr/bin/env bash
set -e
export PYTHONUNBUFFERED=1
# Load .env if present
if [ -f .env ]; then
	set -a
	. ./.env
	set +a
fi
# UI
streamlit run ui/app.py