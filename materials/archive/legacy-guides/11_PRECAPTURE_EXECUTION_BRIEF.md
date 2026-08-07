# Pre-Capture 长期执行简报

- **建立日期**：2026-08-06
- **状态**：Current / 长期目标执行入口
- **目标版本**：`0.5.0-pre-capture`
- **终点**：爱丽丝越界并被整合骑士带走
- **当前素材返工交接**：[MATERIALS_REWORK_HANDOFF_20260807.md](../docs/delivery/MATERIALS_REWORK_HANDOFF_20260807.md)

> 2026-08-07 状态：四幕 authored 主线已达到 `story=ready`。本文第 1、3、4 节保留目标形成过程；当前素材执行以返工交接页、`REQUESTS.csv`、`MANIFEST.csv` 和当日素材审计为准。

## 1. 当前评估

现有项目已经建立稳定的 FastAPI 权威状态、scripted 离线基线、地图交互、活动选择、关系/记忆/承诺/紧张、日期闸门和自动化质量门。这些系统足以支撑一段成熟叙事 RPG，不需要推倒重写。

主要问题不是“内容太少”，而是内容重心偏移：当前主事件已扩展到 Day 117，但运行时仍没有尽头山脉、爱丽丝越界和整合骑士带走她的可玩终点；大量巡查、复盘、资源恢复和路线回访会削弱主线迫近感。数据中仍存在旧角色名和旧术语，正典显示层尚未彻底统一。

因此，下一阶段停止横向增加天数，改为把现有系统压缩到一条完整、紧凑、可回放的 Pre-Capture 主线。

## 2. 官方核实边界

- [Episode 1: Underworld](https://sao-alicization.com/1st/story/01.html)：卢利特村、巨神树天职、三人关系、尽头山脉洞穴和禁忌目录是童年篇起点。
- [Episode 3: The End Mountains](https://sao-alicization.com/1st/story/03.html)：爱丽丝已被 Axiom Church 带走，属于本阶段终点后的状态证据。
- 当前未确认“End of World”为独立正传电影名。若用户返还另一份明确素材，新增版本化参考，不覆盖这次核实。

## 3. 紧凑四幕方案

### Act 0：可信日常（2–3 个节点）

巨神树劳作、爱丽丝送食物、村庄关系和禁忌目录进入玩家行动。玩家先喜欢上三人日常，再看到规则的重量。

### Act 1：规则裂缝（2–3 个节点）

书库记录、村民口述和边境迹象互相矛盾。玩家决定告诉谁、相信谁、保留什么证据；差异必须在后续对话和行动中回响。

### Act 2：前往尽头山脉（2–3 个节点）

三人决定、补给、路线、天气、洞穴和禁忌压力逐步收紧。准备选择改变安全余量、同伴信任和抓捕前的临场表达，但不取消固定终点。

### Act 3：越界与带走（2–3 个节点）

爱丽丝越界，规则产生可感知反应，整合骑士执行抓捕。玩家决定最后一句话、最后动作和最后记录；结局固定，情感后果和留下的证据可变。

## 4. 现有内容处理

- 保留 Day 1–117 和现有测试，不做破坏性删除。
- 从现有事件中抽取最有效的“线索—选择—关系/记忆回响”节点，合并重复巡查、恢复和复盘。
- 在新的 Pre-Capture 路径稳定前，将 Day 31+ 长月循环视为候选内容库和系统压力测试，不视为正式主线节奏。
- 先统一玩家可见的爱丽丝、尤吉欧、桐人、卢利特村、巨神树、禁忌目录等术语；旧 ID 只保留兼容，不继续出现在新文本中。
- 带 Pre-Capture authored 标记的玩家可见文本会拒绝项目已废弃的旧译名和明确的抓捕后剧透；桐人/见习记录员的最终玩家显示名仍等待用户返还素材裁决，不在此阶段提前锁死。

## 5. 用户返还素材入口

优先接收以下请求 ID：

1. `NAR-CANON-001`：官方事实、时间线和具体参考链接。
2. `WORLD-MACRO-001`：人界、暗黑界、中央大教堂、整合骑士和禁忌目录的宏观关系。
3. `WORLD-MICRO-001`：卢利特村、家庭、教会、书库、伐木场、尽头山脉、食物、天气和工具。
4. `CHAR-DEPTH-001`：爱丽丝、尤吉欧、桐人、赛尔卡和支持角色的目标、恐惧、信息边界。
5. `NAR-PRECAP-001`：四幕事件、分支、固定终点和最后表达。
6. `NAR-ADAPT-001`：玩家能改变与不能改变的连续性规则。
7. `QA-CANON-001`：来源、人物阶段、术语、事件闸门和固定终点验收。

返还文件先放入 `materials/inbox/` 对应目录，文件名带请求 ID 和版本号；链接、文字、图片、音频都需要 sidecar 说明来源、用途和权利状态。官方影视截图只作为私人参考，不进入 `approved` 或 runtime。

每个版本化 sidecar 至少包含以下字段，并且 `request_id` 必须与目录请求一致：

```text
- request_id: NAR-...
- creator/source: 来源或提供者
- created_at: YYYY-MM-DD
- license: 权利状态
- source_url: 可核验链接；无链接时明确写明原因
- intended_use: 本项目中的预期用途
```

Pre-Capture readiness 会同时检查这些字段，以及 MANIFEST 的 `source_file` 是否位于该请求的交付目录内。

## 6. 完成定义

- 新游戏可连续完成四幕并到达固定抓捕终点。
- 8–12 个关键节点中没有纯填充事件；每个节点至少推动两个叙事或玩法维度。
- 三位核心角色的目标、恐惧和判断方式可以从行动中区分，而不是只靠设定说明。
- 至少三条玩家选择产生跨节点关系、记忆、承诺或临场表达差异。
- scripted 模式无需外部 API 可完整通关；AI 只能增强表达，不能改写事实终点。
- 正典连续性、内容可达性、后端、前端、build、E2E 通过。
- 至少 3 名陌生玩家完成盲测，并能解释目标、行动代价、禁忌目录和前往尽头山脉的原因。
## 7. Automated readiness check

Run the read-only report with:

```bash
python materials/tools/check_precapture_readiness.py
python materials/tools/check_runtime_asset_specs.py --require-complete
```

It reports seven narrative input requests, 16 first-phase runtime material requests, source registration, four authored acts, 8-12 marked key nodes, the fixed capture endpoint, and cross-node choice echoes. `materials=ready` now means both narrative inputs and required runtime inputs pass their request/sidecar/manifest gates; a received inbox binary cannot satisfy it by itself. The current expected result is `materials=pending, story=ready`; use `--require-complete` only after corrected runtime deliveries and the authored story pass review.
The preferred event metadata is:

```json
{
  "precapture_act": "act_0",
  "precapture_key_node": true,
  "precapture_endpoint": "alice_captured"
}
```

Only one event may set `precapture_endpoint`, it must be the final marked key node, and at least one of its choices must write the same allowed `ending_id`. Cross-node echoes are authored through normal flag writes and later event trigger reads, so the existing FastAPI state engine remains authoritative.
