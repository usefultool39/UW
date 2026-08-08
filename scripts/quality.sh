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

[ -x "${PYTHON_BIN:-}" ] || {
  echo "缺少后端 Python 环境：先运行 ./启动游戏.command --setup-only，或设置 PYTHON_BIN" >&2
  exit 1
}
command -v npm >/dev/null 2>&1 || {
  echo "未找到 npm（需要 Node.js 20+）" >&2
  exit 1
}

echo "[1/7] Documentation consistency"
"$PYTHON_BIN" "$ROOT/scripts/check_docs.py"

echo "[2/7] Materials registry"
"$PYTHON_BIN" "$ROOT/materials/tools/check_materials.py"

echo "[3/7] Runtime asset specifications"
"$PYTHON_BIN" "$ROOT/materials/tools/check_runtime_asset_specs.py" --require-complete

echo "[4/7] Backend tests"
(
  cd "$ROOT"
  "$PYTHON_BIN" -m pytest -q backend/tests
)

echo "[5/7] Frontend unit tests"
npm --prefix "$ROOT/frontend" run test:unit

echo "[6/7] Frontend production build"
npm --prefix "$ROOT/frontend" run build

echo "[7/7] Git diff hygiene"
(
  cd "$ROOT"
  git diff --check
)

echo "Quality gate passed. Release readiness, human playtest and E2E are checked by scripts/release.sh."
