# VIS-CHR-001/002/003 v010 三方向 base reference + 4 帧 placeholder 交付

- request_id: VIS-CHR-001, VIS-CHR-002, VIS-CHR-003
- status: sample_candidate
- version: v010
- directions: up, left, right (down 已在 v009)
- created_at: 2026-08-10
- creator/source: Mavis image_synthesize (1:1, 1K) + rembg 2.0.78 + Pillow 程序化 frame 变体
- intended_use: 三方向 (up/left/right) sprite base reference + 4 帧 placeholder sheet
- license: project-original
- source_url: none
- runtime: prohibited
- depends_on: VIS-CHR-001/002/003_v009 down base reference (用作 input image)

## 范围

- **本轮交付**: 3 角色 × 3 方向 (up/left/right) × 2 文件类型 = 18 个文件
  - 9 张 1024x1024 base reference (RGBA, alpha=0-255)
  - 9 张 256x96 sprite sheet (4 帧: idle + walk_a + walk_b + interact)
- **未做**:
  - 12 帧每方向 (T02 验收要求 2 idle + 6 walk + 4 interact = 12 帧). 本轮只交 4 帧 placeholder.
  - 1440x900 / 390x844 in-game 截图. 需要工程接入后做.
  - down 方向 (v009 已是最新, 不重做).
  - 真正"动作"的程序化关键帧插值 (本轮 4 帧是 base + 抖动 placeholder, 走 6 帧是 6 帧 base 抖动).

## 解决了 v009 留的问题

- v009 缺 up/left/right 三方向 → v010 补齐
- 之前所有方向 sprite 都用 down base 镜像/旋转替代, 与 T02 "禁止" 妥协

## 与 v009 的一致性

| 角色 | v009 down | v010 up | v010 left | v010 right |
|---|---|---|---|---|
| Kirito (001) | 深墨黑发 + 冷蓝上衣 | 同色系, 正面面对镜头 | 侧面, 服装轮廓清晰 | 侧面, 服装轮廓清晰 |
| Alice (002) | 暖金发 + 金背心/白衬衫/蓝带 | 同色系, 正面 | 侧面, 双辫发可辨 | 侧面, 双辫发可辨 |
| Eugeo (003) | 浅金发 + 天蓝 tunic | 同色系, 正面 | 侧面, 斧头可辨 | 侧面, 斧头可辨 |

**注意**: 4 帧变体差异是 ±2px 抖动 + 头部 -4px, 实际游戏内走 6 帧看不出"走路". 完整动画需 T02-B 用程序化关键帧插值或重新生成 walk pose library.

## 机器验收

- 9 个 sprite sheet: 36/36 cell anchor (32, 94) alpha = 0 ✓
- 9 个 sprite sheet: 36/36 cell 四角 alpha = 0 ✓
- 9 个 base reference: 1024x1024 RGBA, alpha range [0, 255] ✓
- 文件大小: base 256-484KB, sheet 5-9KB (透明背景为主)
- 三角色识别色互相可区分 ✓
- 三方向视图与 down 一致 (服装/发型/道具) ✓

## 文件清单 + SHA-256

### Kirito (001)

| 文件 | 字节 | SHA-256 |
|---|---|---|
| VIS-CHR-001_kirito_up_base_v010.png | 411916 | C271B46A68818D8541FBFE6BBF89C13DD507DCCC8C4C6008ACF03350E966FC16 |
| VIS-CHR-001_kirito_left_base_v010.png | 305002 | 6A1EA0015A6572FE6B1086325601BDB95991285F1F4DA18AA224EDC08759D470 |
| VIS-CHR-001_kirito_right_base_v010.png | 256948 | EE1E24CD1214FBB96B8CDB84EC221236732E4F24761775E10CD57C57DD5AC632 |
| VIS-CHR-001_kirito_up_4frame_sheet_v010.png | 7403 | 7B91515A62CC158805C09ED5BE47ACBD95AA84EBE37B483B8B86ABCF5346BC7F |
| VIS-CHR-001_kirito_left_4frame_sheet_v010.png | 6025 | 26C7486F9C99386C3A0B168FBA5084430128D4ADEC04A6D8B70355F076ECEAF0 |
| VIS-CHR-001_kirito_right_4frame_sheet_v010.png | 5164 | E0C25BF8A16C7669BAAD86D3865CEBE63FFFADA3A2AA598FBDCC2DD36324BDE6 |

### Alice (002)

| 文件 | 字节 | SHA-256 |
|---|---|---|
| VIS-CHR-002_alice_up_base_v010.png | 443807 | 855D638395044A3D8B8336C5F7DDDC3AF05D02E25259A7D50361A985D84DF852 |
| VIS-CHR-002_alice_left_base_v010.png | 313172 | B60F5748B06BABDFF57E0DB392E65869CE3FC2B2E0CC060DDBEDDEE62D867023 |
| VIS-CHR-002_alice_right_base_v010.png | 323014 | 7EA3015B38B426B04E629DA88C971361A20A0B4EF8B7ABBEC1948EA8F619CBAB |
| VIS-CHR-002_alice_up_4frame_sheet_v010.png | 8412 | 4C6CB18F905543B80C811459C388EA4AC4531C4C0A88CD882E652FF1D7E07C3C |
| VIS-CHR-002_alice_left_4frame_sheet_v010.png | 6172 | C061830DEFA49CEC71273F287CE7B25722E4AFB1F1ECF2FF345FB2D9ACCEBF65 |
| VIS-CHR-002_alice_right_4frame_sheet_v010.png | 6682 | CFA8DC1F64A28160EEF9DE0FD35E1354DCB8F9D6F6345E81CC8B3447E548E1DE |

### Eugeo (003)

| 文件 | 字节 | SHA-256 |
|---|---|---|
| VIS-CHR-003_eugeo_up_base_v010.png | 484300 | 8B2F8F57F54FA3E902D5B1019DCF4C481D76C37D0344C8D1F2E1289558F96466 |
| VIS-CHR-003_eugeo_left_base_v010.png | 346770 | BB9291B58B8107B4BAC4A04E5B73A2C0E87E328189A483BB6A154020D2CBC4BA |
| VIS-CHR-003_eugeo_right_base_v010.png | 467763 | F40E69C27AFF9FFC89572E4B6449B64AE1F6B43CB65612F321770D9409A83EC7 |
| VIS-CHR-003_eugeo_up_4frame_sheet_v010.png | 8774 | 5A8CB6EBFB3834E0A0DCB7878C68BDB68A2D3DCB9085B0DED365944D6725504A |
| VIS-CHR-003_eugeo_left_4frame_sheet_v010.png | 5726 | 96972BE1454CE7B410EB764EBFC18D0D7511FDF240C6806175234690F274A909 |
| VIS-CHR-003_eugeo_right_4frame_sheet_v010.png | 7534 | D2641FB19E77D0A920EF31D760B47CD918B2F19B4A32F37D42F1DDAB29BBA8EB |

## 已知问题

1. **4 帧差异弱**: walk_a/walk_b 仅 ±2px 偏移, 实际游戏内走看不出动画. 完整 walk 6 帧需 T02-B 用程序化关键帧插值.
2. **JPEG 假 PNG 修复**: image_synthesize 输出 9 张里有 8 张是 JPEG 字节但 .png 后缀. 已用 rembg 重新转 RGBA PNG, 透明背景真实有效.
3. **Alice 头身比略长**: 1K 1024x1024 输出的 Alice 比 Kirito/Eugeo 头身比稍高. 可能是 input reference (down base) 的 Alice 是 3/4 背面变体, AI 推断时保留了比例.
4. **未做 in-game 截图**: 1440x900 / 390x844 比例检查需要工程接入.
5. **未做 left/right 镜像 vs 真侧面区分**: left 用 left side view, right 用 right side view, 实际是两次独立生成. 左右差异可能没有 down 那种"明确分得开"的程度, 仍需人工验收.

## 后续建议

1. **人工验收样本**: 重点看
   - 三方向视图是否一眼分得清 (尤其 up vs down, left vs right)
   - 4 帧差异在游戏内 60fps 下是否能"动起来"
   - 4 帧是否足以撑住 idle/walk 状态 (如果不行, T02-B 走程序化关键帧)
2. **如果通过三方向验收**, T02-B 用程序化关键帧插值补 12 帧/方向 (用 base + 关键 pose library 派生)
3. **如果 4 帧过弱**, 直接用 image_synthesize 重新生成 36 帧/方向 (3 方向 × 12 帧 = 108 帧), 但这要 3 角色 × 36 prompt × 4 = 432 次 AI 调用, 代价大
4. **建议**: T02-B 用本轮 base reference 派生 12 帧, 配合 canonical pose library (idle_2 / walk_6 / interact_4) 程序化组合

## 范围声明

- 本轮交付: 9 base + 9 sheet (3 角色 × 3 方向)
- 未提交: 复制到 current/, MANIFEST.csv 不登记 runtime_file
- 未做: 12 帧/方向, in-game 截图, 镜像 vs 真侧面区分

## 历史

- v009 (down): 3 角色 × 12 帧 down sheet, anchor/四角 alpha 全 0, 36/36 帧合格
- v010 (up/left/right): 3 角色 × 3 方向 × 2 文件类型 = 18 文件
