# VIS-ENV-001_delivery_v003

- request_id: VIS-ENV-001
- status: changes_requested → v003 delivered (received); 不得宣称 approved/integrated
- expected_version: v003 (本包替换 v002, v002 文件保留作为审计证据)
- delivery_dir: materials/inbox/visual/environments
- priority: P1
- reviewed_at: 2026-08-07
- intended_use: activity panels and chapter transitions only, never the playable map
- runtime_status: prohibited until project owner acceptance chain passes

## 1. 工具栈与模型

- creator/source: Mavis（程序化绘制）
- tool_model: procedural-environment-v003 (Python Pillow 11.3.0 + numpy 2.3.5)
- created_at: 2026-08-07
- Pillow 11.3.0 + numpy 2.3.5
- Python 3.13.9

## 2. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| 场景数 | 6 | 6 |
| 尺寸 | 1920x1080 | 1920x1080 |
| 通道 | RGB (前景叠加可另交 RGBA) | RGB (foreground overlay may be added separately as RGBA) |
| 16:9 构图 | 是 | 是 |

### 6 个场景

| id | 中文 | English | 文件 | size bytes | SHA-256 |
|---|---|---|---|---|---|
| church_library | 村西书库 | village west library / reading desk | visual/environments/VIS-ENV-001_church_library_v003.png | 12830 | 0c25d671e9c65ae93be3082e9990818c367c79b86d949d8a2745bba7b189f1f7 |
| gigas_clearing | 古誓树清场 | ancient gigas cedar clearing | visual/environments/VIS-ENV-001_gigas_clearing_v003.png | 13074 | 7ff9263a283dcd86013d0c2544bc9cca8c8e5573fefb00671f611042383be9d6 |
| home_hearth | 家中炉火 | village home interior with hearth | visual/environments/VIS-ENV-001_home_hearth_v003.png | 10662 | 76bcc1bbdb9dd044c5db9704714d721863df74515b5b84d26288ae9749e46563 |
| north_gate | 北境边门 | north boundary stone gate | visual/environments/VIS-ENV-001_north_gate_v003.png | 10032 | 615b4956555fc6d107195394652241c7a1501b1a6b87b2c1bec63f135c4fb282 |
| forest_path | 森林路径 | dense forest path with unnatural silence line | visual/environments/VIS-ENV-001_forest_path_v003.png | 16161 | 4d08658ee4bc0b5a996dff8a9e1a2dc368af033f4087d57dab5ec09f881e2850 |
| end_mountains_cave | 终北山洞 | end-mountains cave / boundary approach | visual/environments/VIS-ENV-001_end_mountains_cave_v003.png | 11968 | 7fbf2b4140826e2c5943768bfef2b365b785234878fc36d46e86698ca9631cdd |

## 3. 创作提示词（合成描述）

```text
Original 2D hand-painted 1920x1080 RGB activity background. No characters, no text/labels/UI/watermarks, no copyrighted game/anime composition. Each scene has a clear middle/lower interaction area and crop-safe margins for desktop (16:9) and mobile (390x844 9:19.5). Color palette: church_library = warm amber wood + candle glow; gigas_clearing = bright green grass + ancient tree crown; home_hearth = dark warm brown + fireplace flame; north_gate = cold grey stone + fog wall; forest_path = green-brown dense canopy + earthy path; end_mountains_cave = deep blue-grey stone + distant faint glow inside cave mouth. Style: clear bright linework, restrained detail, hand-painted feel.
```

### Negative prompt / 禁止项

```text
no characters; no text, labels, signs with words; no UI; no watermarks; no copyrighted game/anime composition; no AI-copied material; no third-party art; no map collision data (these are not playable maps).
```

## 4. seed / settings / 修整

- 配色: 见 PROMPT (每场景独立调色板)
- 随机种子: 8001 (gigas 木屑), 8002 (forest 落叶)
- 输出 PNG RGB optimize=True
- 不烘焙文字、UI、棋盘格、官方截图、动画帧临摹
- 桌面 16:9 中心互动区保留; 移动 390x844 9:19.5 中心裁切保留核心场景

## 5. 来源与权利

- license: owned（owned (procedural synthesis by Mavis, no third-party art, no AI-cloned material)）
- source_url: none（程序化绘制，无外部素材/参考图/版权场景）
- attribution_required: false
- intended_use: visual / environment (activity panel / chapter transition)
- rights statement: 本包场景由 Mavis 通过 Python + Pillow 程序化绘制，采用原创几何形状 + 配色方案；不复制任何动漫/游戏截图、不包含 AI 训练集参考或第三方美术。

## 6. 文件清单（带 SHA-256）

| 资产 ID | 文件 | SHA-256 | size |
|---|---|---|---|
| VIS-ENV-001-church_library-v003 | visual/environments/VIS-ENV-001_church_library_v003.png | 0c25d671e9c65ae93be3082e9990818c367c79b86d949d8a2745bba7b189f1f7 | 12830 |
| VIS-ENV-001-gigas_clearing-v003 | visual/environments/VIS-ENV-001_gigas_clearing_v003.png | 7ff9263a283dcd86013d0c2544bc9cca8c8e5573fefb00671f611042383be9d6 | 13074 |
| VIS-ENV-001-home_hearth-v003 | visual/environments/VIS-ENV-001_home_hearth_v003.png | 76bcc1bbdb9dd044c5db9704714d721863df74515b5b84d26288ae9749e46563 | 10662 |
| VIS-ENV-001-north_gate-v003 | visual/environments/VIS-ENV-001_north_gate_v003.png | 615b4956555fc6d107195394652241c7a1501b1a6b87b2c1bec63f135c4fb282 | 10032 |
| VIS-ENV-001-forest_path-v003 | visual/environments/VIS-ENV-001_forest_path_v003.png | 4d08658ee4bc0b5a996dff8a9e1a2dc368af033f4087d57dab5ec09f881e2850 | 16161 |
| VIS-ENV-001-end_mountains_cave-v003 | visual/environments/VIS-ENV-001_end_mountains_cave_v003.png | 7fbf2b4140826e2c5943768bfef2b365b785234878fc36d46e86698ca9631cdd | 11968 |
| VIS-ENV-001-scenes-json-v003 | visual/environments/VIS-ENV-001_scenes_v003.json | 0feff9414be9b908fbaae1c739192586939ea1b17a15d7adb1337330c0551e9e | 2666 |

## 7. Manifest 片段

- 路径: `materials/inbox/visual/environments/VIS-ENV-001_manifest_fragment_v003.csv`
- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空

## 8. 配套 JSON metadata

- 路径: `materials/inbox/visual/environments/VIS-ENV-001_scenes_v003.json`
- 含 schema_version, request_id, scene_size_px, alpha_mode, scenes[6], no_content, safe_areas

## 9. 短生成 brief

```text
Create six original 1920x1080 character-free environment backgrounds for a clear, bright 2D narrative RPG: church library/reading desk, Gigas Cedar clearing, village home hearth, north gate, forest path with an unnatural silent boundary, and End Mountains cave/boundary approach. These are activity-panel and chapter-transition backgrounds, not playable maps.
```
