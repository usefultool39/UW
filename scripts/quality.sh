#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT/backend/.venv/bin/python}"

[ -x "$PYTHON_BIN" ] || {
  echo "缺少后端虚拟环境：先运行 ./启动游戏.command --setup-only" >&2
  exit 1
}
command -v npm >/dev/null 2>&1 || {
  echo "未找到 npm（需要 Node.js 20+）" >&2
  exit 1
}

echo "[1/4] Backend pytest"
(
  cd "$ROOT"
  "$PYTHON_BIN" -m pytest -q
)

echo "[2/4] Frontend unit tests"
npm --prefix "$ROOT/frontend" run test:unit

echo "[3/4] Frontend production build"
npm --prefix "$ROOT/frontend" run build

echo "[4/4] Git diff hygiene"
(
  cd "$ROOT"
  git diff --check
)

echo "Quality gate passed. Run Playwright E2E before release or UI delivery."
