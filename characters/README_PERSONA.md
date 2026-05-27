# 角色 Persona 与阶段叠加

- **`persona.md`**：角色核心设定（当前默认 **露茵村童年期**）。
- **`overlay_<阶段键>.md`**：由后端 `persona_phase_key(state)` 选择并拼接到 Persona 末尾；用于主线/旗标推进后的**语气与心理微调**，不换年龄、不跳越到记录院骑士等后期人设，除非将来单独增加阶段键与 overlay。

## 阶段键一览（`backend/app/persona_phase.py`）

| 键 | 触发条件（摘要） |
|----|------------------|
| `childhood_rulid` | 默认（教程前期） |
| `childhood_post_reading` | 旗标 `prologue_reading_done` |
| `childhood_mq01` | 主线 `mq01_tree_arc`（优先于读书旗标） |
| `storia_academy` | **仅当** `story_node_id` 属于后端白名单 `_STORIA_ACADEMY_STORY_IDS`（见 `persona_phase.py`）；新增节点时务必把 id 加入该集合，勿用模糊前缀匹配 |

## 昼夜

LLM 的 `user` 消息含 `昼夜氛围`，由 `app.time_bands` 与 `config` 中分界常量分段（与 `system_base.md` 一致）；可在 overlay 中提示夜晚多休息，勿改动作枚举规则。

## 开发热读

- 设置环境变量 **`DEV_RELOAD_PERSONA=1`**（或 `true`/`yes`/`on`）时，`system_base.md` **不缓存**，每次 LLM 调用重新读盘。
- 未设置时，按 `system_base.md` 的 **mtime** 失效内存缓存，改文件后下一轮请求即生效（无需重启 uvicorn）。
