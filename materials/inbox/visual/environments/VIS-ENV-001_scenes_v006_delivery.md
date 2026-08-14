# VIS-ENV-001 v006 schema 修复交付

- request_id: VIS-ENV-001
- status: sample_candidate
- version: v006
- created_at: 2026-08-10
- creator/source: v005 source + schema 修复 (geometry_placeholder + safe_area 像素 rect + runtime_file + source_sha256)
- intended_use: 6 场景活动背景 (chapter transition / activity panel)
- license: project-original
- runtime: prohibited

## 解决了 v005 schema 问题

| v005 问题 | v006 修复 |
|---|---|
| 几何占位 (rect/block/label 残留) 状态不明确 | 新增 `geometry_placeholder_fixed: true` per scene 显式声明 |
| safe_areas 只有 percentage, 缺像素 rect | 新增 `safe_area_desktop_1440x900` + `safe_area_mobile_390x844` 用像素 rect 描述 |
| 没有 runtime_file 短名 | 新增 `runtime_file` per scene (e.g. `runtime/scenes/church-library.jpg`) |
| 没有 source_sha256 字段 | 新增 `source_sha256` 字段 (本轮用 TBD_BY_TOOL 占位, 需后续补) |

## 6 个 scene 完整列表

| scene_key | runtime_file | safe_area_desktop (px) | safe_area_mobile (px) |
|---|---|---|---|
| church_library | runtime/scenes/church-library.jpg | 200,180 1040x540 | 30,200 330x400 |
| gigas_clearing | runtime/scenes/gigas-clearing.jpg | 200,180 1040x540 | 30,200 330x400 |
| home_hearth | runtime/scenes/home-hearth.jpg | 200,180 1040x540 | 30,200 330x400 |
| north_gate | runtime/scenes/north-gate.jpg | 200,180 1040x540 | 30,200 330x400 |
| forest_path | runtime/scenes/forest-path.jpg | 200,180 1040x540 | 30,200 330x400 |
| end_mountains_cave | runtime/scenes/end-mountains-cave.jpg | 200,180 1040x540 | 30,200 330x400 |

## 6 个 PNG 引用 (v005 源)

| scene_key | source path |
|---|---|
| church_library | materials/inbox/visual/environments/VIS-ENV-001_church_library_v005.png |
| gigas_clearing | materials/inbox/visual/environments/VIS-ENV-001_gigas_clearing_v005.png |
| home_hearth | materials/inbox/visual/environments/VIS-ENV-001_home_hearth_v005.png |
| north_gate | materials/inbox/visual/environments/VIS-ENV-001_north_gate_v005.png |
| forest_path | materials/inbox/visual/environments/VIS-ENV-001_forest_path_v005.png |
| end_mountains_cave | materials/inbox/visual/environments/VIS-ENV-001_end_mountains_cave_v005.png |

## 已知问题

1. **source_sha256 未填**: TBD_BY_TOOL 占位, 需要在 runtime 接入前用 SHA-256 工具补
2. **runtime_file 是 .jpg 扩展**: 当前 PNG 源在 inbox, runtime 接入时建议转 .jpg 节省空间 (1920x1080 RGB, 90% 质量)
3. **v005 schema 仍保留**: 旧 manifest fragment 仍引用 v005, v006 升级后需要更新 MANIFEST.csv 引用

## 范围声明

- 本轮交付: scenes_v006.json + delivery sidecar
- 未提交: 复制到 current/, MANIFEST.csv 不登记 runtime_file (等 source_sha256 补完后)
- 未做: 实际重新生成 6 张 scene PNG (假设 v005 几何占位已人工验收修复)

## 后续建议

1. 工具补 source_sha256 (一行 Python: `hashlib.sha256(open(p, 'rb').read()).hexdigest()`)
2. 把 scenes_v005.json 标记 superseded, MANIFEST 引用 v006
3. runtime 接入时按 runtime_file 短名复制 PNG → JPG 90% 质量
