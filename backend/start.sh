#!/bin/bash
set -euo pipefail

# 边境回声 · 前后端分离启动脚本 (Linux/Mac)

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"
BACKEND_PORT="${BACKEND_PORT:-8765}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
PYTHON_BIN="${PYTHON_BIN:-python}"

echo "边境回声 · 启动前后端"
echo "后端: http://127.0.0.1:${BACKEND_PORT}/api/health"
echo "前端: http://127.0.0.1:${FRONTEND_PORT}"
echo ""

cleanup() {
  if [ -n "${BACKEND_PID:-}" ]; then kill "$BACKEND_PID" 2>/dev/null || true; fi
  if [ -n "${FRONTEND_PID:-}" ]; then kill "$FRONTEND_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM

echo "[后端] 启动 FastAPI..."
(
  cd "$BACKEND_DIR"
  "$PYTHON_BIN" -m uvicorn app.main:app --host 127.0.0.1 --port "$BACKEND_PORT" --reload
) &
BACKEND_PID=$!

sleep 2

echo "[前端] 启动 Vite..."
(
  cd "$FRONTEND_DIR"
  if [ ! -d node_modules ]; then npm install; fi
  npm run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT"
) &
FRONTEND_PID=$!

echo ""
echo "服务已启动。按 Ctrl+C 停止。"
wait "$BACKEND_PID" "$FRONTEND_PID"
