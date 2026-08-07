#!/usr/bin/env python3
"""Move all generated v002 files from agent workspace to UW project inbox."""
import shutil
from pathlib import Path

AGENT_WS = Path(r'C:\Users\liang\.minimax\agents\mavis\workspace')
UW_ROOT = Path(r'C:\Users\liang\Desktop\UW')

# Source: agent_ws/materials/inbox/...
# Target: UW_ROOT/materials/inbox/...
source_root = AGENT_WS / 'materials' / 'inbox'

if not source_root.exists():
    print(f'Source not found: {source_root}')
    raise SystemExit(1)

moved = 0
for src in source_root.rglob('*'):
    if not src.is_file():
        continue
    rel = src.relative_to(source_root)
    dst = UW_ROOT / 'materials' / 'inbox' / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        # Don't overwrite
        print(f'SKIP (exists): {rel}')
        continue
    shutil.copy2(src, dst)
    moved += 1
    print(f'MOVED: {rel}  ({src.stat().st_size} bytes)')

print(f'\nTotal moved: {moved}')
