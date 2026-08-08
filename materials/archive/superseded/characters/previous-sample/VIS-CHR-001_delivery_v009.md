# VIS-CHR-001 kirito down sprite sample sheet (v009)

- request_id: VIS-CHR-001
- status: sample_candidate; 不得宣称 approved/integrated/materials=ready
- expected_version: v009 (single-direction sample, down only)
- delivery_dir: materials/inbox/visual/characters/v009
- priority: P1, first-phase runtime blocker
- character: kirito (深墨黑发 + 冷蓝识别的卢利特村男孩)
- created_at: 2026-08-08
- runtime_status: prohibited until project owner acceptance chain passes

## 1. 工具栈与模型

- creator/source: AI 单帧生成 (Mavis image_synthesize) + 程序化拼合 (Python 3.13.14 + Pillow 11.3.0)
- tool_model: Mavis image_synthesize 1K 2:3 + PIL LANCZOS resize + 灰色软边 knockout
- 12 个 prompt 见 `_prompts.json` 同目录 v009 文件夹归档

## 2. 规格与实测

| 项目 | spec | 实测 |
|---|---|---|
| Frame cell | 64×96 | 64×96 |
| Sheet 总尺寸 | 一方向一行 768×96 | 768×96 |
| 方向 | down | down（其它方向未交付） |
| idle 帧数 | 2 | 2 |
| walk 帧数 | 6 | 6 |
| interact 帧数 | 4 | 4 |
| 锚点 | bottom-center (32, 94) | (32, 94) |
| 通道 | RGBA, 8-bit, 非隔行 | RGBA non-interlaced 8-bit |
| 总帧数 | 4×(2+6+4)=48 帧 (4 方向全包) | 12 帧 (1 方向) |

## 3. v008 → v009 关键差异

- v008 程序化绘制圆+矩形，walk 几乎无跨步，interact 4 帧差异弱。
- v009 用 AI 单帧生成 12 张 1K 图，每张独立 prompt，12 帧姿态差异由 AI 模型真实绘制。
- 优势：跨步可见、互动动作（伸手/检查/持物/放手）可读、识别色和服装一致。
- 代价：AI 输出无 alpha 通道，缩放后保留"灰色软边"和"脚下白色光晕"（详见 §4）。

## 4. v009 已知限制（必须人工确认）

1. **灰色软边残留**（idle 帧最严重）：AI 输出图背景是 RGB (98, 97, 95) 灰，角色衣服是 RGB (12, 25, 53) 深蓝，缩放后两色交界处形成"软渐变"。本包用 `(R+G+B) ∈ [200, 540] AND |R-G|+|G-B|+|R-B| < 18` 的灰色软边 knockout 处理，但因角色衣服本身接近灰，部分帧（idle0/1, walk2, int0）仍有可见灰色矩形残留。
2. **脚下白色光晕**（walk2, int0 帧）：AI 渲染的"地面反射"是接近白色，被白底 knockout (R+G+B > 700) 漏掉，在 dark 背景上呈现亮色光圈。
3. **帧间头部位置漂移 ±2-3 像素**：AI 模型无法保证 12 张图严格对齐，PIL 缩放后每帧角色头部在 cell 内 y 坐标略不同。运行时建议加 1-2px 抖动容忍。
4. **只交付 down 1 个方向**：up/left/right 仍未生成，需用相同方法补齐 36 张（3×12）。

## 5. 验收建议

- 选项 A：**接受 v009 限制**。运行时用 Phaser blendMode NORMAL + 接受灰色软边，作为内部纵向切片样张。后续用 LCM / animatediff 工具重做。
- 选项 B：**重新设计 prompt 减弱灰边**。例如明确"完全黑色背景"、"角色剪影外 5px 内全部透明"、"无地面反射"。需要新一组 AI 调用。
- 选项 C：**回到程序化绘制**。v008 升级版（v009 procedural），保证 alpha 干净但视觉风格有限。

## 6. 来源与权利

- license: project-original
- source_url: none（AI 单帧由项目自有 prompt 生成；拼合、knockout、resize 全部本地 Python + Pillow）
- attribution_required: false
- intended_use: 视觉 / character sprite (phaser runtime)
- rights statement: 12 张 1K 图由 Mavis image_synthesize 在项目私有 prompt 体系下生成，不引用任何原作画面、角色外形、第三方美术或 AI 训练集参考。

## 7. 文件清单（SHA-256）

| 资产 | 文件 | SHA-256 | size |
|---|---|---|---|
| VIS-CHR-001-sprite-sheet-v009-down | visual/characters/v009/VIS-CHR-001_kirito_sprite_sheet_v009_down.png | aa6364b3df3a3895e38e69bb5ae803478f9bc6830ca5b793088d2ad395514b91 | 37432 |
| VIS-CHR-001-assemble-json-v009 | visual/characters/v009/VIS-CHR-001_kirito_sprite_sheet_v009_down.assemble.json | fa2c9c1e4ec807597bc7f0c36316b8e7dbcd59622ef83fc937477f74c0596899 | 4893 |
| VIS-CHR-001-assemble-script-v009 | visual/characters/v009/VIS-CHR-001_assemble_v009.py | 531d648752e26db98ba80133fee02c5f8a6681da13777e93d925aa5cc46e25ef | 4435 |
| VIS-CHR-001-sample-1440x900 | visual/characters/v009/VIS-CHR-001_v009_sample_1440x900.png | 9984c67052fe8542f4536826214b6ce1366184891c0b32cda4867ba4e94bf160 | 53419 |
| VIS-CHR-001-sample-1to1 | visual/characters/v009/VIS-CHR-001_v009_sample_1440x900_1to1.png | 191e73d4ea575ad8c61bd3631560709229b64577f2913a453e344d4b9c11e1ab | 47945 |
| VIS-CHR-001-sample-mobile | visual/characters/v009/VIS-CHR-001_v009_sample_mobile_390x844.png | 10a598304bb767b0e3165e4a16edcb9a7b47b46925c6795998e656e6addcad10 | 11170 |

## 8. supersedes

- VIS-CHR-001 v003 极简几何人偶
- VIS-CHR-001 v005 / v006 / v007 partial painterly sprite
- VIS-CHR-001 v008 程序化 sprite（虽然 delivery md 自称"圆润有机剪影 + 真实行走相位"但实际效果不达标）

## 9. 不在本次范围

- up / left / right 三个方向（需另起 v009-up / v009-left / v009-right 同样 12 帧）
- 爱丽丝、尤吉欧的同款 sheet
- VIS-ANIM-001 互动动作包（依赖 v009 全方向完成）
- VIS-CHR-004 支持 NPC sprite（依赖 v009 风格定稿）
