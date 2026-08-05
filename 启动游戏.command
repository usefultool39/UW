#!/bin/bash
set -Eeuo pipefail

# Finder 双击启动时也能找到用户安装的 Node.js 与 Python。
export PATH="$HOME/.local/nodejs/bin:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"
VENV_DIR="$BACKEND_DIR/.venv"
BACKEND_PORT="${BACKEND_PORT:-8765}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
OPEN_BROWSER=1
SETUP_ONLY=0
BACKEND_PID=""
FRONTEND_PID=""

for arg in "$@"; do
  case "$arg" in
    --no-open) OPEN_BROWSER=0 ;;
    --setup-only) SETUP_ONLY=1; OPEN_BROWSER=0 ;;
    -h|--help)
      cat <<'HELP'
用法：双击“启动游戏.command”，或在终端执行：
  ./启动游戏.command              安装缺失依赖并启动游戏
  ./启动游戏.command --no-open    启动但不自动打开浏览器
  ./启动游戏.command --setup-only 只安装/检查依赖，不启动服务

可选环境变量：BACKEND_PORT、FRONTEND_PORT、PYTHON_BIN
HELP
      exit 0
      ;;
    *) echo "未知参数：$arg"; exit 2 ;;
  esac
done

info() { printf '\033[1;36m%s\033[0m\n' "$*"; }
ok() { printf '\033[1;32m%s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m%s\033[0m\n' "$*"; }
fail() { printf '\033[1;31m错误：%s\033[0m\n' "$*" >&2; exit 1; }

pause_on_error() {
  status=$?
  if [ "$status" -ne 0 ]; then
    printf '\n启动失败（退出码 %s）。请查看上方错误信息。\n' "$status" >&2
    if [ -t 0 ]; then
      printf '按回车键关闭窗口...'
      read -r _ || true
    fi
  fi
  exit "$status"
}
trap pause_on_error ERR

cleanup() {
  trap - ERR INT TERM EXIT
  printf '\n'
  warn "正在停止服务..."
  if [ -n "$FRONTEND_PID" ]; then kill "$FRONTEND_PID" 2>/dev/null || true; fi
  if [ -n "$BACKEND_PID" ]; then kill "$BACKEND_PID" 2>/dev/null || true; fi
  wait 2>/dev/null || true
  ok "边境回声已停止。"
}

is_supported_python() {
  "$1" -c 'import sys; raise SystemExit(0 if (3,11) <= sys.version_info[:2] < (3,14) else 1)' >/dev/null 2>&1
}

find_python() {
  if [ -n "${PYTHON_BIN:-}" ] && command -v "$PYTHON_BIN" >/dev/null 2>&1 && is_supported_python "$PYTHON_BIN"; then
    command -v "$PYTHON_BIN"
    return 0
  fi
  for candidate in python3.11 python3.12 python3.13; do
    if command -v "$candidate" >/dev/null 2>&1 && is_supported_python "$candidate"; then
      command -v "$candidate"
      return 0
    fi
  done
  return 1
}

port_in_use() {
  lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

wait_for_url() {
  url="$1"
  label="$2"
  attempts=80
  while [ "$attempts" -gt 0 ]; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    attempts=$((attempts - 1))
    sleep 0.25
  done
  fail "$label 未能及时响应：$url"
}

clear 2>/dev/null || true
printf '\n========================================\n'
printf '       边境回声 · macOS 一键启动\n'
printf '========================================\n\n'
info "项目目录：$ROOT"

[ -d "$BACKEND_DIR" ] || fail "找不到 backend 目录"
[ -d "$FRONTEND_DIR" ] || fail "找不到 frontend 目录"
command -v node >/dev/null 2>&1 || fail "未找到 Node.js，请先安装 Node.js 20 或更新版本"
command -v npm >/dev/null 2>&1 || fail "未找到 npm"
command -v curl >/dev/null 2>&1 || fail "未找到 curl"

NODE_MAJOR="$(node -p 'Number(process.versions.node.split(".")[0])')"
[ "$NODE_MAJOR" -ge 20 ] || fail "Node.js 版本过低：$(node --version)，需要 20 或更新版本"
ok "Node.js：$(node --version) / npm $(npm --version)"

if [ -x "$VENV_DIR/bin/python" ] && is_supported_python "$VENV_DIR/bin/python"; then
  PYTHON="$VENV_DIR/bin/python"
else
  SYSTEM_PYTHON="$(find_python)" || fail "未找到 Python 3.11–3.13。建议安装 Python 3.11 后重试"
  info "创建 Python 虚拟环境（首次运行）..."
  rm -rf "$VENV_DIR"
  "$SYSTEM_PYTHON" -m venv "$VENV_DIR"
  PYTHON="$VENV_DIR/bin/python"
fi
ok "Python：$($PYTHON --version 2>&1)"

REQ_HASH="$(shasum -a 256 "$BACKEND_DIR/requirements.txt" | awk '{print $1}')"
REQ_MARKER="$VENV_DIR/.requirements.sha256"
INSTALLED_HASH=""
[ -f "$REQ_MARKER" ] && INSTALLED_HASH="$(cat "$REQ_MARKER")"
if [ "$REQ_HASH" != "$INSTALLED_HASH" ] || ! "$PYTHON" -c 'import fastapi, uvicorn, pydantic, httpx, dotenv, anthropic, slowapi' >/dev/null 2>&1; then
  info "安装后端依赖（首次运行可能需要几分钟）..."
  "$PYTHON" -m pip install -r "$BACKEND_DIR/requirements.txt"
  printf '%s' "$REQ_HASH" > "$REQ_MARKER"
else
  ok "后端依赖已就绪"
fi

if [ ! -x "$FRONTEND_DIR/node_modules/.bin/vite" ]; then
  info "安装前端依赖（首次运行可能需要几分钟）..."
  (
    cd "$FRONTEND_DIR"
    if [ -f package-lock.json ]; then npm ci; else npm install; fi
  )
else
  ok "前端依赖已就绪"
fi

if [ "$SETUP_ONLY" -eq 1 ]; then
  printf '\n'
  ok "环境检查和依赖安装完成。"
  exit 0
fi

free_port() {
  local port=$1 pids
  trap - ERR
  set +e
  pids=$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null)
  set -e
  trap pause_on_error ERR
  if [ -n "$pids" ]; then
    warn "端口 $port 已被占用，正在自动释放..."
    echo "$pids" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
}
free_port "$BACKEND_PORT"
free_port "$FRONTEND_PORT"

trap cleanup INT TERM EXIT

printf '\n'
info "[1/2] 启动后端：http://127.0.0.1:$BACKEND_PORT/api/health"
(
  cd "$BACKEND_DIR"
  exec "$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port "$BACKEND_PORT"
) &
BACKEND_PID=$!
wait_for_url "http://127.0.0.1:$BACKEND_PORT/api/health" "后端"
ok "后端已启动"

info "[2/2] 启动前端：http://127.0.0.1:$FRONTEND_PORT"
(
  cd "$FRONTEND_DIR"
  exec npm run dev -- --host 127.0.0.1 --port "$FRONTEND_PORT"
) &
FRONTEND_PID=$!
wait_for_url "http://127.0.0.1:$FRONTEND_PORT" "前端"
ok "前端已启动"

printf '\n========================================\n'
ok "游戏已运行：http://127.0.0.1:$FRONTEND_PORT"
printf '不要关闭此终端窗口；按 Ctrl+C 可停止游戏。\n'
printf '========================================\n\n'

if [ "$OPEN_BROWSER" -eq 1 ] && command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:$FRONTEND_PORT"
fi

while kill -0 "$BACKEND_PID" 2>/dev/null && kill -0 "$FRONTEND_PID" 2>/dev/null; do
  sleep 1
done
fail "有一个服务意外退出，请查看上方日志"
