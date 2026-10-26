#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if [[ ! -x .venv/bin/streamlit ]]; then
    printf 'Ambiente virtual não encontrado. Execute ./scripts/setup.sh primeiro.\n' >&2
    exit 1
fi

exec .venv/bin/streamlit run app.py
