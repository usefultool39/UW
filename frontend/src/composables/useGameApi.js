import { ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
const DEFAULT_WORLD_MAP_ID = 'novice_open'
/** 普通接口（状态、配置、启发式 step） */
const REQUEST_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS) || 15000
/** 超过该阈值的超时文案走「AI 慢」提示 */
const LONG_REQUEST_THRESHOLD_MS = 20000

/**
 * AI 模式：一步内会为多名角色各调一次模型，后端单次 HTTP 可达 45s+；
 * 超时 = 基础值 + 每 tick 预留（多 tick 会循环多次完整回合）。
 */
function stepTimeoutMs(mode, n) {
  if (mode !== 'llm') return REQUEST_TIMEOUT_MS
  const ticks = Math.max(1, Math.min(Number(n) || 1, 200))
  const fromEnv = Number(import.meta.env.VITE_API_STEP_LLM_TIMEOUT_MS)
  if (fromEnv > 0) return fromEnv
  /* 每 tick 最多 3 次模型调用，单次后端约 45s；留足余量避免误杀 */
  return Math.min(600_000, 120_000 + ticks * 180_000)
}

export function useGameApi() {
  const state = ref({ tick: 0, day: 1, tree: { hp: 800, hp_max: 800 }, agents: [] })
  const events = ref([])
  const running = ref(false)
  const runInterval = ref(null)
  const llmConfigured = ref(false)
  const llmProvider = ref('')
  const lastError = ref('')
  const runId = ref(null)
  const checkpoint = ref(null)
  const speed = ref(1)
  const pendingCount = ref(0)

  const SPEED_GAP_MS = { 1: 1000, 2: 500, 5: 200 }
  const HEURISTIC_GAP_MS = { 1: 800, 2: 400, 5: 150 }

  function getGapMs(mode) {
    if (mode === 'llm') {
      return SPEED_GAP_MS[speed.value] || 500
    }
    return HEURISTIC_GAP_MS[speed.value] || 800
  }

  function saveCheckpoint() {
    checkpoint.value = {
      state: JSON.parse(JSON.stringify(state.value)),
      eventsLength: events.value.length,
      runId: runId.value
    }
  }

  function clearCheckpoint() {
    checkpoint.value = null
  }

  async function resumeFromCheckpoint() {
    if (!checkpoint.value) return false
    try {
      await refresh()
      lastError.value = ''
      return true
    } catch (e) {
      lastError.value = e.message || '恢复失败'
      return false
    }
  }

  async function requestJson(path, options, timeoutMs = REQUEST_TIMEOUT_MS) {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), timeoutMs)
    let r
    try {
      r = await fetch(`${API_BASE}${path}`, {
        ...options,
        signal: controller.signal
      })
    } catch (e) {
      if (e?.name === 'AbortError') {
        if (timeoutMs > LONG_REQUEST_THRESHOLD_MS) {
          throw new Error(
            '请求超时：AI 模式会多次调用模型，耗时可能达到数分钟。请尝试减少「每步 tick 数」、检查网络与 API 配额，或稍后重试。'
          )
        }
        throw new Error('请求超时：请确认后端已启动 (127.0.0.1:8765)')
      }
      throw new Error('网络错误：无法连接后端 (127.0.0.1:8765)')
    } finally {
      clearTimeout(timer)
    }

    let payload = null
    try {
      payload = await r.json()
    } catch {
      payload = null
    }

    if (!r.ok) {
      const message = payload?.error || payload?.detail || `请求失败（状态码 ${r.status}）`
      throw new Error(message)
    }
    return payload
  }

  async function fetchState() {
    state.value = await requestJson('/api/state')
  }

  async function fetchEvents(limit = 200) {
    events.value = await requestJson(`/api/events?limit=${limit}`)
  }

  async function refresh() {
    try {
      await Promise.all([fetchState(), fetchEvents()])
      lastError.value = ''
    } catch (e) {
      lastError.value = e.message || '刷新失败'
      throw e
    }
  }

  async function step(n = 1, mode = 'heuristic') {
    const j = await requestJson(
      '/api/step',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ n, mode })
      },
      stepTimeoutMs(mode, n)
    )
    if (j?.ok === false) throw new Error(j.error || 'step failed')
    if (j.run_id) runId.value = j.run_id
    await refresh()
    lastError.value = ''
    return j
  }

  async function reset() {
    if (running.value) stopRun()
    clearCheckpoint()
    const j = await requestJson('/api/reset', { method: 'POST' })
    if (j.run_id) runId.value = j.run_id
    await refresh()
    lastError.value = ''
    return j
  }

  async function fetchRegions() {
    return requestJson('/api/world/regions')
  }

  async function fetchWorldMap(mapId = '') {
    const id = String(mapId || '').trim()
    if (!id || id === DEFAULT_WORLD_MAP_ID) return requestJson('/api/world/map')
    return requestJson(`/api/world/maps/${encodeURIComponent(id)}`)
  }

  async function fetchSceneActivities() {
    return requestJson('/api/world/scene_activities')
  }

  async function fetchStoryCatalog() {
    return requestJson('/api/story/catalog')
  }

  async function fetchAvailableStoryEvents() {
    return requestJson('/api/story/available_events')
  }

  /** 与 POST /api/step 等价，命名对齐后端「日常 tick」 */
  async function dailyTick(n = 1, mode = 'heuristic') {
    const j = await requestJson(
      '/api/sim/daily_tick',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ n, mode })
      },
      stepTimeoutMs(mode, n)
    )
    if (j?.ok === false) throw new Error(j.error || 'daily_tick failed')
    await refresh()
    lastError.value = ''
    return j
  }

  /**
   * @param {Record<string, unknown>} body
   * @param {{ deferRefresh?: boolean }} [opts]
   * deferRefresh: 仅返回 JSON（含 path），不立刻拉 state；用于移动动画播完后再 refresh。
   */
  async function playerAction(body, opts = {}) {
    const j = await requestJson('/api/player/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (j?.ok === false) throw new Error(j.error || j.detail || 'player_action failed')
    if (!opts.deferRefresh) {
      await refresh()
    }
    lastError.value = ''
    return j
  }

  async function storyAdvance(targetId) {
    const j = await requestJson('/api/story/advance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_id: targetId })
    })
    if (j?.ok === false) throw new Error(j.error || 'story_advance failed')
    await refresh()
    lastError.value = ''
    return j
  }

  async function chooseStoryEvent(body) {
    const j = await requestJson('/api/story/choose', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (j?.ok === false) throw new Error(j.error || 'story_choose failed')
    await refresh()
    lastError.value = ''
    return j
  }

  async function fetchNpcProfile(npcId) {
    return requestJson(`/api/npc/${encodeURIComponent(npcId)}/profile`)
  }

  async function sendDialogue(body) {
    const j = await requestJson('/api/dialogue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (j?.ok === false) throw new Error(j.error || 'dialogue failed')
    await refresh()
    lastError.value = ''
    return j
  }

  async function exportSave() {
    return requestJson('/api/save/export')
  }

  async function importSave(save) {
    const j = await requestJson('/api/save/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(save)
    })
    if (j?.ok === false) throw new Error(j.error || 'save_import failed')
    await refresh()
    lastError.value = ''
    return j
  }

  async function checkLlm() {
    const c = await requestJson('/api/config')
    llmConfigured.value = c.llm_configured
    llmProvider.value = c.provider_hint
  }

  function startRun(n, mode) {
    running.value = true
    saveCheckpoint()
    const gapMs = getGapMs(mode)

    async function loop() {
      if (!running.value) return
      pendingCount.value = 1
      try {
        const result = await step(n, mode)
        // 巨树 1e8 HP 时通常不会倒；保留判断以免特殊剧本改 hp
        if (result.state?.tree?.hp <= 0 || result.state?.tree?.state === 'fallen') {
          stopRun()
          clearCheckpoint()
          return
        }
      } catch (e) {
        lastError.value = e.message || '连续运行失败'
        stopRun()
        return
      } finally {
        pendingCount.value = 0
      }

      if (!running.value) return
      runInterval.value = setTimeout(loop, gapMs)
    }

    runInterval.value = setTimeout(loop, gapMs)
  }

  function stopRun() {
    running.value = false
    if (runInterval.value) {
      clearTimeout(runInterval.value)
      runInterval.value = null
    }
    pendingCount.value = 0
  }

  function toggleRun(n, mode) {
    if (running.value) {
      stopRun()
    } else {
      startRun(n, mode)
    }
  }

  function setSpeed(s) {
    speed.value = s
  }

  return {
    state,
    events,
    running,
    llmConfigured,
    llmProvider,
    lastError,
    runId,
    checkpoint,
    speed,
    pendingCount,
    fetchState,
    fetchEvents,
    refresh,
    step,
    reset,
    checkLlm,
    startRun,
    stopRun,
    toggleRun,
    setSpeed,
    saveCheckpoint,
    clearCheckpoint,
    resumeFromCheckpoint,
    fetchRegions,
    fetchWorldMap,
    fetchSceneActivities,
    fetchStoryCatalog,
    fetchAvailableStoryEvents,
    dailyTick,
    playerAction,
    storyAdvance,
    chooseStoryEvent,
    fetchNpcProfile,
    sendDialogue,
    exportSave,
    importSave
  }
}
