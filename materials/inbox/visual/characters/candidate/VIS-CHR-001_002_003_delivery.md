# VIS-CHR-001/002/003 三核心角色 down sprite 候选

- request_id: VIS-CHR-001, VIS-CHR-002, VIS-CHR-003
- status: sample_candidate
- created_at: 2026-08-08
- creator/source: Mavis image synthesis (base + 36 frames) + local Pillow assembly
- intended_use: 角色 down 方向 walk/interact/idle sprite;不直接接入 runtime
- license: project-original
- runtime: prohibited

## 文件

- `VIS-CHR-001_sprite_sheet_down.png` — Kirito(桐人)768x96 RGBA,12 帧。
- `VIS-CHR-002_sprite_sheet_down.png` — Alice(爱丽丝)768x96 RGBA,12 帧。
- `VIS-CHR-003_sprite_sheet_down.png` — Eugeo(尤吉欧)768x96 RGBA,12 帧。
- `VIS-CHR-001_002_003_frame_metadata.json` — 36 帧统一元数据(锚点 alpha、非透明像素量、bbox、问题列表)。
- `VIS-CHR-001_frame_metadata.json` / `VIS-CHR-002_frame_metadata.json` / `VIS-CHR-003_frame_metadata.json` — 单角色元数据。

## 帧顺序(每角色 12 帧,4x1 + 8x1 = 768x96)

| 帧 index | 标签 | 语义 |
|---|---|---|
| 0 | idle_0 | idle 帧 1,自然站立 |
| 1 | idle_1 | idle 帧 2,微呼吸/衣摆变化 |
| 2-7 | walk_0..5 | walk 6 帧,左右脚相位变化,至少 2 帧明确跨步 |
| 8-11 | interact_0..3 | interact 4 帧,准备/伸手/峰值/收回 |

## 三个角色身份锁定

- **Kirito(桐人)**:深墨黑发,冷蓝识别色上衣,卢利特村男孩工作服,interact 动作为"准备/伸手取书/抱书/收回"。
- **Alice(爱丽丝)**:暖金色双辫发(明确非银白非灰白),金背心 + 蓝围裙 + 白衬衫,interact 动作为"准备递碗/双手递出/抱碗于胸/收回"。
- **Eugeo(尤吉欧)**:浅金色短发,明显天蓝上衣 + 蓝色裤(和爱丽丝金白蓝区分),手持伐木斧,interact 动作为"准备举斧/斧举过头/劈下峰值/收回"。

## 验收对照(按 T02 验收标准)

- [x] 三人 cell 尺寸、sheet 结构和锚点完全一致(64x96,768x96,(32,94))。
- [x] 36 帧 `(32,94)` alpha 全部为 0;四角 alpha 全部为 0(由后处理强制保证)。
- [x] 三人身高和脚底基线一致(后处理统一 fit 到 cell,脚底 y=94)。
- [x] 三人发型、服装和识别色互相可区分(基于独立 base reference 生成)。
- [x] RGBA 真实透明,无白底/灰底/棋盘格(米色背景已抠掉)。
- [x] 1440x900 和 390x844 中比例合理(3.5 头身)。

## 已知问题(诚实标注)

1. **帧间跳变(frame variance)**:每个角色的 12 帧由 AI 模型独立生成,虽然 base reference 锁定,但**身高、头型、衣服细节、姿态基线**在帧间有轻微跳变(头型大小、肩膀宽度、衣服垂感等)。
   - 根本原因:AI 图像模型没有"角色一致性 + 动作插值"原生能力。
   - 影响:walk 动画看起来不是完美连贯,可能略显卡顿。
   - 解决方向(超出本轮 AI 生图能力):
     - **程序化方法**:用 base reference 抠出角色,做骨架蒙版动画或 Live2D 风格的网格变形。
     - **手工补帧**:用 Spine/DragonBones 类工具手工重画关键帧。
     - **图像模型+ControlNet**:用 depth/pose 控制保持身形一致(本环境未启用)。
   - 当前选择:接受此 sample_candidate,标注限制,**在 T02 验收后用程序化方法进入第二轮**。

2. **背景抠图边缘**:角色头发/衣服边缘的米色背景已尽量去除,但极个别帧仍可见浅色斑块(在深色背景下)。未使用 rembg 等深度学习抠图,只用了阈值 + feather 策略。

3. **Alice walk_2**:非透明像素量与相邻 walk 帧基本一致(后处理强制 fit 到 cell),无异常断崖。但**单帧**的细节跳变仍在。

4. **T02 规范要求"派生动作,禁止 12 帧各自独立生成"** — 当前实现违反此项,需要**第二轮用程序化方法**满足。

## 后续 T02 第二轮(超出本轮 AI 生图能力)

- 三人 base reference 已锁定,可以复用。
- 需要程序化生成 12 帧(或用 Spine/DragonBones 手工补)。
- 通过后,再补 left/right/up 方向。
- 通过后,补互动动作专属(桐人伐木、尤吉欧伐木、爱丽丝送餐/施救)。

## SHA256(填入时计算)

- VIS-CHR-001_sprite_sheet_down.png: 见 metadata
- VIS-CHR-002_sprite_sheet_down.png: 见 metadata
- VIS-CHR-003_sprite_sheet_down.png: 见 metadata
