# VIS-VFX-001 神圣术 v003 candidate 交付

- request_id: VIS-VFX-001
- asset: 神圣术 (holy_arts) — 静默线 v002 保留在 current/ 目录不变
- version: v003
- status: `sample_candidate`
- created_at: 2026-08-08
- creator/source: Mavis image synthesis (image_synthesize, 4:1 aspect, 2K) + Pillow floodfill keying
- intended_use: 神圣术 VFX 4 帧循环 sheet; **不直接接入 runtime**
- license: project-original
- source_url: none
- runtime: prohibited

## 解决的问题（vs current 神圣术 v001）

| 检查 | v001 current | v003 candidate |
|---|---|---|
| 1024×256 RGBA 尺寸 | ✓ | ✓ |
| 4×1 cell, 256×256 | ✓ | ✓ |
| **每帧四角 alpha=0** | **✗ (corner_min=255)** | **✓ (4/4 pass)** |
| 真透明（无白底/灰底） | ✗ 深灰半透明背景 | ✓ floodfill 去 91.9% 背景 |
| 暖金墨痕语义 | ✓ | ✓ |
| 4 帧节奏 0→1→2→3→0 | ✓ | ✓ |
| 没有文字/水印/Logo | ✓ | ✓ |
| 帧间过渡流畅 | 暖金墨痕 | 暖金墨痕 + 4 帧渐强渐弱 |

## 文件清单 + SHA-256

| 文件 | 尺寸 | 模式 | SHA-256 |
|---|---|---|---|
| `VIS-VFX-001_holy_arts_candidate_v003.png` | 1024×256 | RGBA | `3647f312...8575a` |
| `VIS-VFX-001_holy_arts_frame_0_v003.png` | 256×256 | RGBA | (per metadata) |
| `VIS-VFX-001_holy_arts_frame_1_v003.png` | 256×256 | RGBA | (per metadata) |
| `VIS-VFX-001_holy_arts_frame_2_v003.png` | 256×256 | RGBA | (per metadata) |
| `VIS-VFX-001_holy_arts_frame_3_v003.png` | 256×256 | RGBA | (per metadata) |
| `VIS-VFX-001_holy_arts_v003_frame_metadata.json` | metadata | — | — |

**保留不覆盖**：`materials/inbox/visual/vfx/current/VIS-VFX-001_holy_arts.png`（v001，sample_candidate 状态保留供回滚参考）。

## 4 帧语义

- **frame 0**: 起点 — 小光点刚冒头
- **frame 1**: 增长 — 卷曲墨痕上升
- **frame 2**: 峰值 — 暖金盛开莲花纹 + 粒子光晕
- **frame 3**: 释放 — 墨纹扩散成光点消散

loop 顺序 0→1→2→3→0

## 像素级验收（每帧）

| Frame | 四角 alpha | y_top | y_bottom | non_trans | corner pass |
|---|---|---|---|---|---|
| 0 | [0,0,0,0] | (ink dot) | (ink dot) | 1962 | ✓ |
| 1 | [0,0,0,0] | (curl) | (curl) | 3948 | ✓ |
| 2 | [0,0,0,0] | (peak bloom) | (peak bloom) | 10454 | ✓ |
| 3 | [0,0,0,0] | (dispersal) | (dispersal) | 4825 | ✓ |

## 机器验收

- ✓ 1024×256 RGBA 尺寸正确
- ✓ 4×1 cell, 每 cell 256×256
- ✓ **4/4 cell corner alpha=0**（v001 不通过的关键问题修复）
- ✓ RGBA 真透明（floodfill 去 91.9% 背景像素）
- ✓ 暖金墨痕语义保留
- ✓ 4 帧节奏 0→1→2→3→0
- ✓ 没有文字、水印、Logo、签名、棋盘格
- ✓ 静态查看器中可能显示"深色背景"，这是 alpha=0 透明像素让底色透出，**不是文件本身有背景**

## 已知问题（候选边界，诚实标注）

1. **深色背景下观感问题**：PNG 在深色背景查看器中显示时，墨痕周围看起来有"光晕"——这是因为图片本身没有背景，但深色显示底色让暖金光的"外溢"更明显。在游戏中实际叠加到 Phaser 时（Phaser 默认背景可能是浅色村庄），光晕会显著减弱或消失。
2. **frame 2 像素量偏大**：10454 px 是 4 帧中最复杂的峰值帧。这是 AI 模型渲染"盛开莲花"细节丰富的结果，可以接受（人眼感觉"丰富"），但占内存稍大。
3. **未做实际播放节奏验证**：4 帧的循环是否流畅需要在游戏内运行时验证。本轮交付仅交付单帧 + 拼合 sheet，不含 gif/webm 动画预览。
4. **静默线 v002 保留在 current/，未做 v003 重做**：按本轮决策，静默线保持 v002 现状（alpha 干净，语义可接受）。

## 范围声明

- 本轮交付：1 个 4 帧 sheet + 4 张单帧 + 1 个 frame metadata JSON + 本 sidecar。
- **未生成**：gif/webm 循环预览、深色 vs 浅色背景双版本对比图。
- **未提交**：v003 复制到 current/；MANIFEST.csv 不登记 runtime_file；不写入 frontend/public/assets/runtime/。

## 后续建议

1. **人工验收样本**：重点看
   - 在 Phaser 实际场景下叠加（村庄背景）是否还像"激光"或"光球"
   - 4 帧循环是否流畅
   - 暖金色调是否与村庄关键图、人物肖像相容
2. **如果通过 T04 验收**，本轮 T01-T04 全部 sample_candidate 提交完成；下一轮可以按需求做 in-game 截图或 left/right/up 方向。
3. **如果 v003 暖金光晕在游戏内太抢眼**，可以后续做"低光晕版" v004，减少光晕扩散（threshold 调高）。
