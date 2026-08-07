import hashlib
import os
from pathlib import Path

# 输出所有 v003 交付文件的 SHA-256 + size
ROOTS = {
    "audio": Path(r"C:\Users\liang\Desktop\UW\materials\inbox\audio"),
    "world": Path(r"C:\Users\liang\Desktop\UW\materials\inbox\visual\world"),
    "characters": Path(r"C:\Users\liang\Desktop\UW\materials\inbox\visual\characters"),
    "environments": Path(r"C:\Users\liang\Desktop\UW\materials\inbox\visual\environments"),
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


for label, root in ROOTS.items():
    print(f"=== {label} ===")
    for f in sorted(root.rglob("*v003*")):
        if not f.is_file():
            continue
        if "_v003_work" in str(f):
            continue
        sha = sha256_file(f)
        print(f"  {f.relative_to(root.parent.parent)} | size={f.stat().st_size} | sha256={sha}")
    print()
