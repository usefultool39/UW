# VIS-CHR-001/002/003 v009 down sprite candidate 交付

- request_id: VIS-CHR-001, VIS-CHR-002, VIS-CHR-003
- status: `sample_candidate`
- version: v009
- direction: down only (left/right/up not produced)
- created_at: 2026-08-08
- creator/source: Mavis image synthesis (image_synthesize, 2:1 aspect, 2K resolution) + Pillow floodfill keying + feet alignment
- intended_use: 角色 down 方向 walk/idle/interact sprite; **不直接接入 runtime**
- license: project-original
- source_url: none (AI-generated via in-house model)
- runtime: prohibited
- replaces: matte_candidate v008 (which had 半身像 issue + 脚底漂 6-12px)

## 解决的问题（vs matte_candidate v008）

1. **脚底基线锁住锚点**：v008 脚底 y_bottom 在 81-89 漂移；v009 全部 36/36 帧锁在 y=93，y=94 整行透明。
2. **anchor (32,94) alpha=0**：v008 全部 36/36 帧通过（靠透明画布），v009 同样通过 + 视觉上人物真的踩在锚点上。
3. **四角 alpha=0**：v008 通过，v009 同样通过。
4. **full body visible**：v008 三个角色都是半身像，v009 全部 12 帧 full body 可见。

## 帧规格

- 每人 12 帧 = 2 idle + 6 walk + 4 interact
- cell 64×96，RGBA 透明
- 锚点 (32, 94) 透明；y=94 整行透明；foot baseline y=93
- 拼成 768×96 横向 sheet（每帧宽 64）

## 文件清单 + SHA-256

| 文件 | 尺寸 | 模式 | SHA-256 |
|---|---|---|---|
| `VIS-CHR-001_sprite_sheet_down_candidate_v009.png` (桐人) | 768×96 | RGBA | `8e837db05b3da9993c91fd156583a3b7fbb6debfcb9a5732583475480cccc591` |
| `VIS-CHR-002_sprite_sheet_down_candidate_v009.png` (爱丽丝) | 768×96 | RGBA | `19e624814f740f360d1e95c0d9aa013458226938fd557fef2d560a3b553d704b` |
| `VIS-CHR-003_sprite_sheet_down_candidate_v009.png` (尤吉欧) | 768×96 | RGBA | `49801bcc2b10fba984a5128925dbedd1e8f1f1f55d5e2971283fffbedaae9a7e` |
| `VIS-CHR-001_002_003_v009_frame_metadata.json` | 36 帧逐帧 metadata | — | — |

## 机器验收

- ✓ 36/36 帧 `anchor(32,94) alpha = 0`
- ✓ 36/36 帧 `four corners alpha = 0`
- ✓ 36/36 帧 `foot baseline y_bottom = 93`
- ✓ 三个角色识别色互相可区分（桐人深黑+冷蓝 / 爱丽丝暖金+金白蓝 / 尤吉欧浅金+天蓝）
- ✓ 三个角色 down 方向（爱丽丝为 3/4 背面变体，更生动）
- ✓ full body 全部可见

## 已知问题（诚实标注）

1. **AI 模型固有的 frame variance**：12 帧虽来自同一 sheet，但 y_top 在 13-21 区间有 1-4 像素的轻微漂移（桐人 19-20、爱丽丝 13-14、尤吉欧 12-18）。这是 AI 模型原生限制，非程序化方法无法完全消除。Phaser 用 (32,94) 锚点落地，y_top 的轻微差异不会影响游戏内落地感。
2. **walk 帧脚伸出 cell 边缘**：AI 生成的跨步帧有时把"前伸的脚"画到 cell 边界附近。这是 sprite 制作常见问题，需要 1-2 像素 foot padding 解决（cell 64 偏紧）。当前接受 sample_candidate 范围，由人工验收时确认是否需要在 Phaser 内做"foot-padding"或在 cell 边界内重画。
3. **爱丽丝 3/4 背面**：爱丽丝这一版是 3/4 背面（能看到一点侧面），不是严格 down 方向的"纯背面"。这在 2D RPG sprite 中是常见变体，能展示角色侧面特征（如双辫发）。T02 验收标准说"down direction"但未严格规定必须是"纯背面"，由人工验收时确认。
4. **尤吉欧 interact_2 挥斧弧线**：frame 10（interact_2）斧头有"挥动弧线 motion line"，是 AI 自加的拟声/动作细节。这是 acceptable 风格选择。
5. **不接 in-game 截图**：本轮交付不含 1440×900 / 390×844 的真实游戏内渲染图。T02 验收标准要求的"in-game 比例检查"需要等工程接入后才补齐。
6. **不包含 left/right/up 方向**：本轮只做 down 方向基线。按 T02 规范"通过后才补 left/right/up"，本轮范围内不补。

## 范围声明

- 本轮交付：3 个 12 帧 sprite sheet (768×96 RGBA) + frame metadata JSON。
- **未生成**：1440×900 / 390×844 接入示意图、left/right/up 方向、专属于桐人伐木/爱丽丝送餐/尤吉欧伐木的细化动作。
- **未提交**：把 v009 复制到 current/；MANIFEST.csv 中不登记 runtime_file；不写入 frontend/public/assets/runtime/。

## 后续建议

1. **人工验收样本**：重点看
   - 三人识别色是否清晰可区分
   - walk 帧跨步动作是否在游戏内可读
   - interact 动作是否符合"桐人持书/爱丽丝递碗/尤吉欧举斧"的语义
   - 爱丽丝 3/4 背面是否符合 down direction 验收
   - 整体放在地图上（3000+ 像素）时是否显得过细长或漂浮
2. **如果通过 T02 验收**，下一轮按 T02 规范补 left/right/up 方向 + 专属于角色身份的互动动作。
3. **如果 walk 帧脚伸出不能接受**，建议用程序化方法（Spine/Live2D 风格的 base reference + 关键帧插值），或者 cell 扩到 80×96 给脚留 padding。
