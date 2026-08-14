# VIS-CHR-004 NPC sprite v002 candidate 交付

- request_id: VIS-CHR-004
- status: sample_candidate (从 archive/unreviewed 升级)
- version: v002
- created_at: 2026-08-10
- creator/source: archive/unreviewed/supporting-npc v002 原图 + rembg 2.0.78 alpha 修复
- intended_use: 三个支持 NPC 的 up/down 方向 sprite (idle/walk/interact 帧)
- license: project-original
- source_url: none
- runtime: prohibited
- 3 角色: Selka 赛尔卡 (女童) / Garret 加斯夫特 (中年工) / Rulid Elder 村庄长老 (老人)

## 解决了 unreviewed 状态的问题

- 11/17 文件是 JPEG 假 PNG → 用 rembg 重新生成真 RGBA PNG
- 文件位置从 `archive/unreviewed/supporting-npc/` 移到 `inbox/visual/characters/candidate/` (正式候选目录)
- 生成 6 个 sprite sheet (3 角色 × up/down), 替代原单帧散图
- 写 manifest fragment + delivery sidecar
- 机器检查: 全部 17 alpha cell anchor (32, 94) = 0

## 文件清单

### 17 张 alpha 修复版单帧

| 文件 | 角色 | 方向 | 动作 | 字节 |
|---|---|---|---|---|
| VIS-CHR-004_garret_down_idle_v002_alpha.png | 加斯夫特 | down | idle | 453252 |
| VIS-CHR-004_garret_down_walk_v002_alpha.png | 加斯夫特 | down | walk | 435383 |
| VIS-CHR-004_garret_down_interact_v002_alpha.png | 加斯夫特 | down | interact | 261509 |
| VIS-CHR-004_garret_up_idle_v002_alpha.png | 加斯夫特 | up | idle | 359467 |
| VIS-CHR-004_garret_up_walk_v002_alpha.png | 加斯夫特 | up | walk | 316545 |
| (garret_up_interact 缺失) | | | | |
| VIS-CHR-004_rulid_elder_down_idle_v002_alpha.png | 长老 | down | idle | 374936 |
| VIS-CHR-004_rulid_elder_down_walk_v002_alpha.png | 长老 | down | walk | 288350 |
| VIS-CHR-004_rulid_elder_down_interact_v002_alpha.png | 长老 | down | interact | 615679 |
| VIS-CHR-004_rulid_elder_up_idle_v002_alpha.png | 长老 | up | idle | 515796 |
| VIS-CHR-004_rulid_elder_up_walk_v002_alpha.png | 长老 | up | walk | 420271 |
| VIS-CHR-004_rulid_elder_up_interact_v002_alpha.png | 长老 | up | interact | 386868 |
| VIS-CHR-004_selka_down_idle_v002_alpha.png | 赛尔卡 | down | idle | 222443 |
| VIS-CHR-004_selka_down_walk_v002_alpha.png | 赛尔卡 | down | walk | 318692 |
| VIS-CHR-004_selka_down_interact_v002_alpha.png | 赛尔卡 | down | interact | 357110 |
| VIS-CHR-004_selka_up_idle_v002_alpha.png | 赛尔卡 | up | idle | 274236 |
| VIS-CHR-004_selka_up_walk_v002_alpha.png | 赛尔卡 | up | walk | 376220 |
| VIS-CHR-004_selka_up_interact_v002_alpha.png | 赛尔卡 | up | interact | 398548 |

### 6 张 sprite sheet (3 角色 × up/down)

| 文件 | cells | anchor_zero |
|---|---|---|
| VIS-CHR-004_garret_down_sprite_sheet_v002.png | 3 (idle/walk/interact) | 3/3 ✓ |
| VIS-CHR-004_garret_up_sprite_sheet_v002.png | 2 (idle/walk) | 2/2 ✓ |
| VIS-CHR-004_rulid_elder_down_sprite_sheet_v002.png | 3 | 3/3 ✓ |
| VIS-CHR-004_rulid_elder_up_sprite_sheet_v002.png | 3 | 3/3 ✓ |
| VIS-CHR-004_selka_down_sprite_sheet_v002.png | 3 | 3/3 ✓ |
| VIS-CHR-004_selka_up_sprite_sheet_v002.png | 3 | 3/3 ✓ |

## 已知问题 / 范围限制

1. **left/right 方向完全缺失**: 17 张原图只有 up/down, 没有 left/right 侧视. 本轮未补, 留给 VIS-CHR-004-B.
2. **garret_up_interact 缺失**: 原 archive 里缺一张. 留空.
3. **未做 in-game 截图**: 需要工程接入 Phaser 后做 1440x900/390x844 比例检查.
4. **walk 帧只有 1 帧**: T02 验收要 6 帧 walk, 但每个 NPC 只有 1 张 walk 静态图. 实际游戏内看不到"走"动作.
5. **interact 动作语义**: 都是单帧, 没有"准备-执行-峰值-收回"4 帧序列. 实际游戏中按一下交互是单帧切换, 没有动画.

## 三角色识别 (按项目识别色规范)

- Selka 赛尔卡: 粉裙 + 金发双辫 + 识别色 **rose-pink** (项目未给标准, 建议 rose-400/rose-500)
- Garret 加斯夫特: 工装 + 棕背心 + 灰胡 + 识别色 **amber-700**
- Rulid Elder 长老: 长袍 + 蓝灰 + 白胡 + 木杖 + 识别色 **violet-500** (建议)

## 后续建议

1. **left/right 方向补齐** (VIS-CHR-004-B): 用 image_synthesize 加 down base reference 生成左/右侧面, 每角色 1 张 base
2. **walk 帧程序化派生** (VIS-CHR-004-C): 用 1 帧 walk base + 程序化关键帧派生 6 帧 walk
3. **interact 4 帧派生** (VIS-CHR-004-D): 同上, 用 1 帧 interact base 派生 4 帧
4. **统一识别色规范**: 与 Alice/Kirito/Eugeo 一致, 在 chars meta 里加 color 字段

## 范围声明

- 本轮交付: 17 alpha 单帧 + 6 sprite sheet
- 升级: archive/unreviewed/supporting-npc → inbox/visual/characters/candidate
- 未提交: 复制到 current/, MANIFEST.csv 不登记 runtime_file
- 未做: left/right 方向, walk 6 帧, interact 4 帧, in-game 截图

## 历史

- v002 (unreviewed): 17 张原图, 11 张是 JPEG 假 PNG, 缺 sidecar
- v002 (本轮): 17 张 alpha 修复 + 6 个 sprite sheet, 全部 anchor=0
