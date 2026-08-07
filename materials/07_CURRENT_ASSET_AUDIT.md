# 当前素材审计（0.4.0-preview.1）

- 审计日期：2026-08-04
- 范围：`frontend/public`、前端素材引用、音频实现、tileset manifest

## 1. 当前可用素材

### 世界与开场

- `frontend/public/assets/game/field-bg-tv-v3.jpg`：1672×941，当前主地图和开场共用。
- `frontend/public/assets/game/field-bg.png`：1536×1024，旧/兼容背景。
- `frontend/public/assets/generated/world-village-bg.png`：1536×1024，生成源候选。
- 风险：一张图承担地图、开场和多场景气氛；移动端只能裁切；没有正式分层源和来源 sidecar。

### 角色

- 玩家、爱丽丝、尤吉欧有透明 token 候选图。
- 实际 Phaser 配置仍以 `procedural_pixel` 为主，确保离线 fallback。
- 赛尔卡、加利塔、加斯夫特只有程序化角色，没有正式 sprite/portrait。
- 风险：现有 token 不是统一动画 sheet；角色肖像体系不完整；生成源和运行时版本并存但缺 manifest。

### UI

- Kenney UI 部分切片有许可证与 attribution。
- 大多数当前 UI 使用 CSS，层级已经能工作。
- 风险：缺统一原创图标系统；资源、关系、紧张、记忆主要靠文字 chip，视觉识别还可加强。

### 音频

- 当前无正式音频文件目录。
- `useAudio.js` 用 WebAudio 程序化生成村庄晨间 BGM、细雨 ambience、脚步与活动提示音，并对缺失 URL 安全回退。
- 优点：scripted 离线可玩、不因缺素材报错。
- 风险：听觉辨识和情绪层次有限，不能支撑 Day 1 日常→Day 2 静默→Day 3 决断的升级。

### Tileset

- `luin_village_v1.json` 已定义语义、颜色、可走性、角色 token 路径。
- 正式 tile 图片仍未提供；Vue/Phaser 与 Cocos 都回退到程序化 tile。
- 这意味着可以逐步替换素材，但不应直接删除 fallback。

## 2. 缺口排序

1. **视觉方向未锁定**：先做方向板，不宜直接全量生产。
2. **开场关键图缺移动构图与来源规范**：最高可见度，适合作为第一张正式图。
3. **三核心人物肖像缺统一语言**：关系回响已经存在，但缺少情绪载体。
4. **核心图标缺失**：数值决策已经清楚，图标可提升扫读速度。
5. **正式音频缺失**：程序化 fallback 可用，适合低风险替换。
6. **地图重绘与角色动画**：价值高但成本大，必须在方向批准后做。
7. **叙事语料与真实试玩证据**：决定未来 scripted/agent 表达和下一轮改动，不能忽视。

## 3. 不建议现在做

- 不先做 20+ 场景大图。
- 不先做所有 NPC 的完整 4 向 8 帧动画。
- 不先替换现有可用 UI 框架为重拟物整套皮肤。
- 不先生成完整配音。
- 不删除程序化地图、角色和音频 fallback。

## 4. 首轮接入目标

只选择：1 张开场图、3 人肖像、12 图标、1 首 BGM、1 条 ambience。接入后再用 3 名首次玩家测试是否真的提升“看懂目标、愿意继续、感到人物关系”。如果没有提升，不扩量。
# 2026-08-07 current snapshot

This file keeps the original 2026-08-04 audit for history. The current authoritative asset snapshot is `docs/delivery/MATERIALS_AUDIT_20260807.md`.
As of 2026-08-07, the first key-art, portrait, icon, BGM, and ambience samples exist. A new map, core-character, six-scene, and second-wave audio batch was received in `materials/inbox`, but it is `changes_requested`, not approved or integrated. The map is a flattened/non-playable illustration package, character files are non-transparent single poses rather than animation sheets, and audio measurements/durations are invalid for acceptance. VFX, capture presentation, SFX, interaction animation, and tile/prop packages remain undelivered.

`check_precapture_readiness.py` now reports `materials=pending, story=ready`; `check_materials.py` reports 68 missing-sidecar errors. See the request-scoped `REWORK_*_20260807.md` files and the authoritative delivery audit before asking for regeneration or runtime promotion.
