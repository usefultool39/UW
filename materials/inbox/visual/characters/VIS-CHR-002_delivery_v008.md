# VIS-CHR-002_delivery_v008

- request_id: VIS-CHR-002
- status: received; 不得宣称 approved/integrated/materials=ready
- expected_version: v008 (替换 v007/v006/v005/v003/v002 失败审计证据；v002/v003 文件保留)
- delivery_dir: materials/inbox/visual/characters
- priority: P1, first-phase runtime blocker
- character: alice (麦金发 + 青蓝发带的村长之女)
- created_at: 2026-08-07
- runtime_status: prohibited until project owner acceptance chain passes

## 1. 工具栈与模型

- creator/source: 项目自有程序化绘制（v008 升级版）
- tool_model: procedural-sprite-v008 (Python 3.13.12 + Pillow 12.3.0)
- created_at: 2026-08-07
- Python 3.13.12（managed runtime）
- Pillow 12.3.0
- ImageDraw + ImageFilter（GaussianBlur radius=0.4）

## 2. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| Frame cell | 64x96 | 64x96 |
| Sheet 总尺寸 | 一角色一 sheet (4 方向 × 12 帧) | 768x384 |
| 方向 | down/left/right/up | down,left,right,up |
| idle 帧数 | 2 | 2 |
| walk 帧数 | 6 | 6 |
| interact 帧数 | 4 | 4 |
| 锚点 | bottom-center (32, 94) | (32, 94) |
| collision footprint | 12x6 底部居中 | 12x6 @ (26, 88) |
| 通道 | RGBA, 8-bit, 非隔行 | RGBA non-interlaced 8-bit |
| 总帧数 | 4×(2+6+4)=48 帧 | 48 |
| Alpha 检查 | 含真实透明与角色像素 | 已校验 |

## 3. 动画参数

| animation | frames | fps | duration_ms | loop |
|---|---|---|---|---|
| idle | 2 | 1.25 | 800 | True |
| walk | 6 | 7.1 | 140 | True |
| interact | 4 | 2.9 | 350 | False |

## 4. v008 与历史版本的关键差异

- v003 → 极简几何人偶，被返工
- v006 → 程序化彩绘，已通过技术校验但缺真实动画差异
- v007 → 第一版圆润剪影，walk 摆动过小
- **v008** → 圆润有机剪影 + 真实行走相位（左右腿交替、身体浮动）+ 4 帧可读交互动作（伸手、检查、持物、放手）
- 每个角色独立的发色、服装、识别色、装备剪影

## 5. alice (麦金发 + 青蓝发带的村长之女) 创作描述

- 主色：麦金 + 冷青蓝点缀
- 形状：稳定三角，护肩/披肩不过度夸张
- 物件：胸前圈注过的记录页
- 发型：金色长发用青蓝色发带束起，露出额头
- 服装：米白实用护衣 + 浅棕护肩披肩 + 浅褐长裤 + 棕色短靴
- 比例：儿童，约 3.5 头高，非 chibi

## 6. 通用负向约束

```
no checkerboard; no opaque RGB pretending to be alpha; no single pose per animation name;
no anime frames copied; no game sprite cloning; no baked shadow; no background;
no text; no UI; no scenery; no AI-copied material; no third-party art; no existing
franchise character likeness, costume, weapon, or accessory.
```

## 7. seed / settings / 修整

- 配色与装备：见各角色 palette dict（v008 脚本内）
- 帧 cell 64x96 全部角色一致；bottom-center 脚底锚点 (32, 94) 锁死
- walk 6 帧使用 sin 相位 (frame × π / 1.5) 驱动两腿前后 + 1-2px 身高下沉
- interact 4 帧：伸出 (-10x) → 检查 (-6x) → 持物 (-5x) → 放手 (-3x)
- idle 2 帧：sin 相位呼吸 (0.5-1px 上下)
- 方向渲染：down 双臂双腿 + 五官；up 仅头发；left/right 近侧完整 + 远侧半透明
- 输出 PNG RGBA optimize=True, non-interlaced alpha

## 8. 来源与权利

- license: owned
- source_url: none（程序化绘制，无外部素材/参考图/版权角色/IP 复刻）
- attribution_required: false
- intended_use: visual / character sprite (phaser runtime)
- rights statement: 本包 sprite 由项目自有代码（Python + Pillow）程序化绘制，采用原创几何形状 + 配色方案；不复制任何动漫/游戏原帧、不包含 AI 训练集参考或第三方美术。

## 9. 文件清单（带 SHA-256）

| 资产 | 文件 | SHA-256 | size |
|---|---|---|---|
| VIS-CHR-002-sprite-sheet-v008 | visual/characters/VIS-CHR-002_alice_sprite_sheet_v008.png | 9e4d921aebc4cd5e1630845df01d25839d94f5fa9f3a575028fc28d1bed01d79 | 22002 |
| VIS-CHR-002-frames-json-v008 | visual/characters/VIS-CHR-002_frames_v008.json | 747127d2862d98c1b6df38017df95a80a22621104202342a594d6f35c734be05 | 17942 |

## 10. Manifest 片段

- 路径: `materials/inbox/visual/characters/VIS-CHR-002_v008_manifest_fragment.csv`
- 18 列 schema, status=received, runtime_file/approved_by/approved_at/integrated_at 留空

## 11. supersedes

- VIS-CHR-002 v003 geometric puppet sprite sheet
- VIS-CHR-002 v005 partial painterly sprite
- VIS-CHR-002 v006 complete painterly sprite
- VIS-CHR-002 v007 first-pass organic silhouette
