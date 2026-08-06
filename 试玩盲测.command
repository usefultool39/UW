#!/bin/bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "$ROOT/启动游戏.command" --playtest "$@"
