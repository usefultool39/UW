#!/bin/bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FULL=1
RUN_SETUP=1
BACKEND_PORT="${E2E_BACKEND_PORT:-8011}"
FRONTEND_PORT="${E2E_FRONTEND_PORT:-4174}"

usage() {
  cat <<'HELP'
用法：./scripts/playtest-preflight.sh [--quick] [--skip-setup]

  默认         安装/检查依赖，运行素材校验、质量门和完整 Playwright E2E
  --quick      仅运行素材校验、盲测记录状态和质量门，跳过完整 E2E
  --skip-setup 假定依赖已经安装

本脚本只验证“可以交给真人试玩”，不会生成或伪造真人盲测结果。
HELP
}

for arg in "$@"; do
  case "$arg" in
    --quick) FULL=0 ;;
    --skip-setup) RUN_SETUP=0 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数：$arg" >&2; usage >&2; exit 2 ;;
  esac
done

cd "$ROOT"
mkdir -p runs/playtest

if [ "$RUN_SETUP" -eq 1 ]; then
  ./启动游戏.command --setup-only
fi

PYTHON="$ROOT/backend/.venv/bin/python"
[ -x "$PYTHON" ] || { echo "缺少后端虚拟环境，请先运行 ./启动游戏.command --setup-only" >&2; exit 1; }

echo "[盲测预检] 素材台账、来源文件与 runtime hash"
"$PYTHON" materials/tools/check_materials.py

echo "[盲测预检] 真人记录状态（pending 是允许状态，不等于已经完成）"
"$PYTHON" scripts/check_playtest_round.py

echo "[盲测预检] 项目质量门"
./scripts/quality.sh

if [ "$FULL" -eq 1 ]; then
  echo "[盲测预检] 完整 Playwright E2E"
  UW_RATE_LIMIT_ENABLED=0 \
  E2E_BACKEND_PORT="$BACKEND_PORT" \
  E2E_FRONTEND_PORT="$FRONTEND_PORT" \
  npm --prefix frontend run test:e2e
fi

REPORT="runs/playtest/preflight_$(date +%Y%m%d_%H%M%S).json"
COMMIT="$(git rev-parse HEAD)"
VERSION="$(cat VERSION)"
"$PYTHON" - "$REPORT" "$COMMIT" "$VERSION" "$FULL" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

path, commit, version, full = sys.argv[1:]
report = {
    "kind": "playtest_preflight",
    "round_id": "QA-PLAY-001",
    "environment_ready": True,
    "human_playtest_status": "pending-human-run",
    "commit": commit,
    "version": version,
    "full_e2e_run": full == "1",
    "created_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    "note": "This report proves automated readiness only; it is not human playtest evidence.",
}
Path(path).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
Path("runs/playtest/preflight_latest.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
PY

echo "盲测预检通过：$REPORT"
echo "真人记录仍必须由 3 名真实玩家填写，当前状态保持 pending-human-run。"
