# AI NPC 边界与双模式设计

- **状态**：Current
- **目标**：固定 NPC 现在完整可玩，Provider 适配器已落地，未来接 API 不重写世界规则。
- **适配器**：`docs/architecture/AI_PROVIDER_ADAPTER.md` / `backend/app/ai_provider.py`

## 模式

| 模式 | 行为 |
|---|---|
| `scripted` | 本地固定对话和规则；默认、离线、稳定基线 |
| `hybrid` | 模型增强表达/候选计划，规则验证；失败回退 |
| `agent` | 模型参与感知、计划、行动、反思，仍受工具白名单和规则约束 |

## 不变量

模型不能直接修改资源、时间、位置、奖励；不能绕过剧情/地点/时段；不能写未经筛选的永久事实；不能读取其他 run、密钥或任意文件；失败时不能阻塞 scripted 主线。

## 稳定输出

```json
{
  "mode_used": "scripted|hybrid|agent",
  "reply": "玩家可见文本",
  "emotion": "calm",
  "proposed_intent": null,
  "memory_candidate": {"type": "dialogue", "summary": "...", "weight": 3},
  "fallback_reason": null
}
```

`memory_candidate` 只是候选，Session 决定是否提交。

## Agent Loop

```text
Perceive（只读允许状态） → Plan（结构化候选）
→ Validate（规则/预算/剧情闸） → Act（后端工具）
→ Observe → Reflect（受限记忆候选）
```

## API 接入前条件

- scripted 基线测试固定；每 NPC 独立开关，默认关闭。
- StepFun / SenseTime / OpenAI-compatible 通过统一 `LLM_PROVIDER` 配置接入，不提交真实密钥。
- 适配器必须先通过 fake HTTP 的离线测试，再允许本机 API 灰度。
- 超时、限额、解析失败和违规输出自动回退。
- 记录模型、提示词版本、延迟、成本、候选与最终执行。
- 同一存档可切回 scripted，不影响权威状态。

## 当前 Agent Loop 落地状态（2026-08-05）

已落地“候选 → 白名单校验 → Session 审计 → 玩家确认执行”的第一步：

- `POST /api/npc/{npc_id}/intent/propose` 只返回预览，不直接提交世界效果；
- 候选只能引用当前 `NpcIntent` 与其 `response_options`；
- `intent_policy.py` 拒绝跨 NPC、未知 response、注入文本和低置信度模型候选；
- `player_action` 仍是唯一的效果提交入口；
- 每局 AI 调用受 `AgentBudget` 限制，超额回退 scripted / heuristic。

下一步才考虑在 NPC 自主行动中调用已验证的工具白名单，且每个工具都必须保持可回放、可撤销或可由 authored 规则重算。
