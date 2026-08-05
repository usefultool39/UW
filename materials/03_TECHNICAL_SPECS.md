# 素材技术规格与命名规范

## 1. 总体交付原则

- **源文件**与**运行时文件**分开。源文件放 `materials/approved/`；运行时压缩版由开发侧进入 `frontend/public/assets/...`。
- 所有文件使用 sRGB；透明图避免半透明脏边；不要把色彩配置文件搞成 CMYK。
- 不在图像里烘焙中文文字、按钮、数值或任务名。
- 交付原尺寸，禁止先小图再 AI 放大冒充细节。
- 每个文件必须有 request ID、版本号和 sidecar。

## 2. 命名

```text
<REQUEST_ID>_<slug>_v<NNN>[_variant][_size].<ext>
```

示例：

```text
VIS-KA-001_rulid_drizzle_v001_desktop.png
VIS-POR-001_alice_v003_concerned.png
AUD-BGM-001_village_morning_v002_loop.wav
NAR-LORE-001_north_record_07_v001.md
```

规则：ASCII 小写 slug；空格改 `_`；版本固定三位；不要使用“最终版、最终2、最新版”。

## 3. Sidecar

二进制旁必须有同名 `.md`。至少记录：request_id、作者/来源、日期、工具与模型、完整 prompt/negative prompt、seed、许可证、URL、修改、用途。缺 sidecar 的文件只能留在 inbox。

## 4. 图像规格

### 开场关键图

- Desktop master：2560×1440 PNG 或高质量无损 WebP；后续可转 JPEG/WebP。
- Mobile master：1440×1920；必须重新构图。
- 推荐分层：background / weather / focal light / foreground / optional characters。
- 文字安全区：desktop 左 45%；mobile 下 45%。

### 地图

- Master：4096×2304；runtime 候选 2048×1152。
- 无角色、无地名、无 UI、无固定任务光标。
- 高对比地标与道路必须在 50% 缩放可读。
- 若交分层 PSD/CLIP，同时交扁平 PNG，避免工具不兼容。

### 肖像

- 1024×1024 transparent PNG；人物占画布 78–88%。
- 统一脚本命名表情：`neutral/warm/concerned/tense/resolved`。
- 边缘检查：1px 黑/白底均无明显白边、黑边、残留背景。

### Sprite sheet

- 建议单格 64×96 或 96×128；整组统一。
- 方向顺序固定：down, left, right, up。
- 每方向：idle 2 帧，walk 6 帧；脚底锚点一致。
- 透明 PNG + JSON frame manifest；不要把投影烘焙到角色脚上，除非全组一致。

### UI 图标

- 首选 SVG；必须确认 path 可编辑、无外链字体和嵌入位图。
- PNG fallback：24/48/96px；像素对齐；透明背景。
- 24px 下笔画不少于 1.5px 等效宽度。

### VFX

- 透明 PNG 序列或 atlas；2 的幂次纹理优先（1024/2048）。
- 标注帧率、帧尺寸、blend mode 建议、循环与否。
- 移动端避免大面积 alpha 叠加；单次特效尽量 < 1.5 秒。

## 5. 音频规格

### 源文件

- 48kHz / 24-bit WAV；stereo，脚步等可 mono。
- 不要先交低码率 MP3 再转 WAV。
- 循环素材必须说明 loop start/end；最好从 0 到文件结尾即可无缝循环。

### 运行时候选

- BGM/ambience：OGG Vorbis 160–224 kbps；Safari 兼容时可另出 AAC/MP3。
- SFX：OGG 或 WAV；极短 UI 音效可保留 WAV。
- 不同格式从同一 master 导出。

### 响度目标

| 类型 | Integrated LUFS | True Peak |
|---|---:|---:|
| BGM | -20 至 -17 | ≤ -1 dBTP |
| Ambience | -26 至 -22 | ≤ -2 dBTP |
| UI SFX | 依上下文，通常 -22 至 -16 | ≤ -1 dBTP |
| Impact/reward | 可稍高，但短时 | ≤ -1 dBTP |

- 不要在 master 上过度限制器压扁动态。
- 试听时检查手机小扬声器、普通耳机、低音量三种场景。

## 6. 文本/叙事素材

- UTF-8 Markdown 或 CSV；不要只交截图。
- 每条内容带稳定 ID、角色/地点/时段/条件标签。
- 中文标点全角；玩家可见文本不混用爱丽丝/艾琳、尤吉欧/尤里等旧名。
- 未来 agent 语料必须区分：世界事实、语气建议、禁止编造、fallback 文案。

## 7. 参考与权利

- 参考图本身也要记录 URL/作者/许可/仅参考状态。
- `仅参考` 不等于可以剪贴或训练后直接复刻。
- 商用可用性不明确时写 `unknown`，不得批准。

## 8. 运行时预算（首轮）

- 单张开场 runtime 图：目标 < 1.2 MB。
- 单张场景图：目标 < 900 KB。
- 单个肖像 PNG：目标 < 450 KB；可按需转 WebP。
- 核心图标总包：目标 < 250 KB。
- 单首 90 秒 OGG：目标 1.5–3 MB。
- 首屏新增资源总量尽量 < 4 MB；非首屏资产应延迟加载。

## 9. 文件健康检查

批准前检查：能否打开、尺寸/采样率正确、透明边缘、色彩空间、循环点、命名、sidecar、许可、重复哈希、手机可读性。任何一项失败都只能进入 `changes_requested`。
