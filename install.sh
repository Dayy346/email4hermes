#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "==> email4hermes install"

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
  echo "Python 3.11+ is required."
  exit 1
fi

PYTHON_BIN="$(command -v python3 || command -v python)"

if [[ ! -d .venv ]]; then
  echo "==> Creating .venv"
  "$PYTHON_BIN" -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Installing package (editable + dev)"
python -m pip install --upgrade pip
pip install -e ".[dev]"

if [[ ! -f .env ]]; then
  echo "==> Copying .env.example -> .env"
  cp .env.example .env
  echo "    Edit .env and add GOOGLE_* credentials + GOOGLE_REFRESH_TOKEN"
else
  echo "==> .env already present"
fi

mkdir -p output

echo
echo "==> Next steps"
echo "1. Edit .env (EMAIL_BACKEND=gmail, GOOGLE_CLIENT_ID/SECRET/REFRESH_TOKEN, GOOGLE_ACCOUNT_EMAIL)"
echo "2. Edit config/newsletter.yaml (cadence_days, profile, to_email, timezone)"
echo "3. Start API:  uvicorn email_assistant.main:app --host 127.0.0.1 --port 8000"
echo "4. If needed, get refresh token via GET /auth/google/url then /auth/google/callback"
echo "5. Paste docs/HERMES_MASTER_PROMPT.md into Hermes so it can install cron"
echo "6. Dry-run checklist: docs/HERMES_ORCHESTRATOR.md"
echo
echo "Windows PowerShell equivalent:"
echo "  python -m venv .venv"
echo "  .\\.venv\\Scripts\\Activate.ps1"
echo "  pip install -e \".[dev]\""
echo "  Copy-Item .env.example .env"
echo "  .\\.venv\\Scripts\\python.exe -m uvicorn email_assistant.main:app --reload"
echo
echo "Install complete."
