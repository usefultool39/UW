# Underworld NPC 意图 Agent Loop

- **状态**：Current / 预览推荐已落地，自动执行仍需显式 Session 工具调用
- **实现**：`backend/app/npc_intent_agent.py`、`backend/app/intent_policy.py`
- **入口**：`POST /api/npc/{npc_id}/intent/propose`

## 目标

让 NPC 可以用模型理解当前关系、记忆和 authored 事件，并推荐“此刻最值得回应的 NPC 主动事件”，但不允许模型创造剧情事实。第一阶段只做**预览推荐**：玩家或 UI 仍通过 `player_action(kind=respond_npc_intent)` 执行回应。

## 安全链路

```text
当前 WorldState + 当前 authored NpcIntent 列表 + 受限记忆
    ↓
Agent 只输出 intent_id / response_id / confidence / reason
    ↓
intent_policy.py：NPC 所属、当前目录、response 白名单、文本标记、置信度校验
    ↓
Session 记录 npc_intent_proposal JSONL 审计
    ↓
玩家确认后进入 player_action
    ↓
Session 再次查当前 intent 和 response，才提交 flags / relationship / memory
```

模型无法提供或修改：

- 新 intent、新 response 或任意 action/effects；
- 日期、位置、资源、剧情 flag、关系最终值、奖励和存档；
- 其他 run 的记忆、项目外文件或密钥。

## 离线与预算

- 没有 Provider、endpoint 或密钥时使用当前最高优先级 authored intent 的确定性 fallback。
- Provider 错误、非法 JSON、未知 intent、未知 response 和低置信度候选都不会改变世界。
- `AgentBudget` 按单局 run 限制 `action`、`dialogue`、`intent` 调用；预算耗尽自动回退，并把原因写入返回值、事件 JSONL 和动作事件。
- 默认预算：每局总计 24 次；action 12 次、dialogue 12 次、intent 6 次。可用 `.env` 覆盖。

## 手工验证

```bash
cd /Users/lzm/Desktop/UW/backend
../backend/.venv/bin/python -m pytest -q \
  tests/test_intent_policy.py tests/test_npc_intent_agent.py tests/test_agent_budget.py
```

默认 scripted 游戏无需调用此入口，仍保持完整离线可玩。
