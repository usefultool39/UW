# Underworld AI Provider 适配器

- **状态**：已实现，可离线回退
- **实现**：`backend/app/ai_provider.py`
- **目标**：让阶跃星辰、商汤或其他 OpenAI-compatible API 可以逐个 NPC 灰度测试，同时不改变世界规则、存档和 scripted 主线。

## 使用边界

Provider 只提供一段模型文本。它不能：

- 修改日期、位置、资源、剧情 flag 或奖励；
- 直接写入永久记忆；
- 绕过 Session 的行动验证；
- 读取项目外文件、其他 run 或密钥内容；
- 阻塞没有 API 的 scripted 游戏。

`llm_agent.py` 和 `dialogue_agent.py` 负责解析结构化输出；Session / Story Director 负责最终裁决。

## 配置

默认不设置 `LLM_PROVIDER`，继续走已有 MiniMax / Anthropic 兼容逻辑。实验 Provider 必须显式设置：

```env
NPC_RUNTIME=hybrid
NPC_RUNTIME_ALICE=agent
LLM_PROVIDER=stepfun
LLM_API_KEY="..."
LLM_BASE_URL="https://provider.example/v1"
LLM_MODEL="provider-model-id"
LLM_TIMEOUT_SECONDS=45
```

支持的 Provider 名称和别名：

| 配置值 | 适配协议 | 密钥 | Base URL |
|---|---|---|---|
| `stepfun` / `阶跃工坊` | OpenAI-compatible `/chat/completions` | `LLM_API_KEY` 或 `STEPFUN_API_KEY` | `LLM_BASE_URL` 或 `STEPFUN_BASE_URL` |
| `sensetime` / `商汤工坊` | OpenAI-compatible `/chat/completions` | `LLM_API_KEY` 或 `SENSETIME_API_KEY` | `LLM_BASE_URL` 或 `SENSETIME_BASE_URL` |
| `openai-compatible` | OpenAI-compatible `/chat/completions` | `LLM_API_KEY` / `OPENAI_API_KEY` | `LLM_BASE_URL` / `OPENAI_BASE_URL` |
| `minimax` | 统一适配器的 OpenAI-compatible 入口 | `LLM_API_KEY` 或 `MINIMAX_API_KEY` | `LLM_BASE_URL` / `MINIMAX_OPENAI_BASE_URL` |
| `anthropic` | Anthropic Messages | `LLM_API_KEY` 或 `ANTHROPIC_API_KEY` | 可选 `LLM_BASE_URL` |

仓库不会保存真实密钥。用户本机 API 的实际 endpoint 和 model id 只放在未提交的 `.env` 中。

## 请求和回退

```text
NPC runtime
  → dialogue_agent / llm_agent
  → ai_provider.generate_text
  → 解析 JSON
  → 规则验证
  → 返回候选表达/意图
  → 失败时 fallback_dialogue / heuristic
```

以下情况都会回退：

- 未配置密钥或 endpoint；
- timeout / HTTP 错误；
- 响应没有 `choices` 或文本；
- 对话 JSON 无法解析；
- action 名称不在 `ActionName` 白名单；
- NPC runtime 不是显式 `hybrid` / `agent`。

回退不会改变世界事实，只会把 `source` 标记为 `fallback`，并保留可审计的错误原因。

## 离线测试

Provider 适配器使用 fake HTTP client 测试，不向真实 API 发请求：

```bash
cd backend
.venv/bin/python -m pytest -q tests/test_ai_provider.py
```

完整游戏仍必须在以下环境可玩：

1. 没有任何 API key；
2. Provider endpoint 不可达；
3. Provider 返回错误或非法 JSON。
