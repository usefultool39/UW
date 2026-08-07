#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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

[ -x "$PYTHON_BIN" ] || {
  echo "缺少后端 Python 环境：先运行 ./启动游戏.command --setup-only，或设置 PYTHON_BIN" >&2
  exit 1
}
command -v npm >/dev/null 2>&1 || {
  echo "未找到 npm（需要 Node.js 20+）" >&2
  exit 1
}

echo "[1/8] Materials registry and runtime assets"
"$PYTHON_BIN" "$ROOT/materials/tools/check_materials.py"

echo "[2/8] Runtime visual/audio specifications"
"$PYTHON_BIN" "$ROOT/materials/tools/check_runtime_asset_specs.py" --require-complete

echo "[3/8] Pre-Capture readiness report"
"$PYTHON_BIN" "$ROOT/materials/tools/check_precapture_readiness.py"

echo "[4/8] Human playtest record status"
"$PYTHON_BIN" "$ROOT/scripts/check_playtest_round.py"

echo "[5/8] Backend pytest"
(
  cd "$ROOT"
  "$PYTHON_BIN" -m pytest -q
)

echo "[6/8] Frontend unit tests"
npm --prefix "$ROOT/frontend" run test:unit

echo "[7/8] Frontend production build"
npm --prefix "$ROOT/frontend" run build

echo "[8/8] Git diff hygiene"
(
  cd "$ROOT"
  git diff --check
)

echo "Quality gate passed. Run Playwright E2E before release or UI delivery."
