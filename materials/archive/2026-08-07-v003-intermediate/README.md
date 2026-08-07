# v003 历史中间文件归档

- 归档日期：2026-08-07
- 原因：以下文件属于 v003 生成/转码中间产物，文件名不含已登记 request_id，导致 `check_materials.py` 报 7 个错误。
- 处理：从正式 `materials/inbox` 扫描范围非破坏性移动到本审计归档；不删除、不改内容。
- 状态：历史证据，不得进入 MANIFEST 或 runtime。

| 原路径 | 归档相对路径 | bytes | SHA-256 |
|---|---|---:|---|
| `materials/inbox/audio/_v003_work/test_192k.ogg` | `audio/_v003_work/test_192k.ogg` | 425758 | `532731d3201fcf49b60688cf30c0619dcf3cd42357fa42ca2067a3600ce2d147` |
| `materials/inbox/audio/_v003_work/test_192k2.ogg` | `audio/_v003_work/test_192k2.ogg` | 1310720 | `224c24ba2ceeabe417670fe4580a32922d5112c89c1a654b25451df320405615` |
| `materials/inbox/audio/_v003_work/test_full.ogg` | `audio/_v003_work/test_full.ogg` | 1838406 | `ecf3b14dfa12af7e2dd7a7caa9fd9aafe0423e151e41f02256c2a728f621efe8` |
| `materials/inbox/visual/world/props_atlas_v003.png` | `visual/world/root/props_atlas_v003.png` | 1273 | `49c86e3f84e0f80ea5aa2c684f88d7a883d59309c1aad483ae6fbb99efa7fc10` |
| `materials/inbox/visual/world/tiles_atlas_v003.png` | `visual/world/root/tiles_atlas_v003.png` | 870 | `12beca9f5d2d66ff1d6856c7f6ffe8de0061625adee1709a5b62fdad8177f5d2` |
| `materials/inbox/visual/world/_v003_work/props_atlas_v003.png` | `visual/world/_v003_work/props_atlas_v003.png` | 1273 | `49c86e3f84e0f80ea5aa2c684f88d7a883d59309c1aad483ae6fbb99efa7fc10` |
| `materials/inbox/visual/world/_v003_work/tiles_atlas_v003.png` | `visual/world/_v003_work/tiles_atlas_v003.png` | 870 | `12beca9f5d2d66ff1d6856c7f6ffe8de0061625adee1709a5b62fdad8177f5d2` |

归档完成后应重新运行：

```powershell
backend\.venv\python.exe materials\tools\check_materials.py
```

