#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$ROOT/scripts/quality.sh"

if [ -z "${PYTHON_BIN:-}" ]; then
  for candidate in \
    "$ROOT/backend/.venv/bin/python" \
    "$ROOT/backend/.venv/python.exe" \
    "$ROOT/backend/.venv/Scripts/python.exe" \
    "$ROOT/.conda/uw-runtime/python.exe"; do
    if [ -x "$candidate" ]; then
      PYTHON_BIN="$candidate"
      break
    fi
  done
fi

echo "[release 1/3] Pre-Capture readiness"
"$PYTHON_BIN" "$ROOT/materials/tools/check_precapture_readiness.py"

echo "[release 2/3] Human playtest records"
"$PYTHON_BIN" "$ROOT/scripts/check_playtest_round.py"

echo "[release 3/3] Playwright E2E"
(
  cd "$ROOT/frontend"
  npm run test:e2e
)

echo "Release gate passed."
