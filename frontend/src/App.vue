<template>
  <div class="game-container" :class="{ 'field-mode': appTab === 'field' }">
    <nav v-if="showDevTabs" class="app-tabs" aria-label="视图切换">
      <button
        type="button"
        class="tab-btn"
        :class="{ active: appTab === 'overview' }"
        @click="appTab = 'overview'"
      >
        状态总览
      </button>
      <button
        type="button"
        class="tab-btn"
        :class="{ active: appTab === 'field' }"
        @click="appTab = 'field'"
      >
        地图探索
      </button>
    </nav>

    <FieldSlice
      v-if="appTab === 'field'"
      :sim-state="state"
      :dev-mode="showDevTabs"
      :daily-tick="dailyTick"
      :player-action="playerAction"
      :story-advance="storyAdvance"
      :fetch-available-story-events="fetchAvailableStoryEvents"
      :choose-story-event="chooseStoryEvent"
      :fetch-npc-profile="fetchNpcProfile"
      :send-dialogue="sendDialogue"
      :export-save="exportSave"
      :import-save="importSave"
      :fetch-regions="fetchRegions"
      :fetch-world-map="fetchWorldMap"
      :fetch-scene-activities="fetchSceneActivities"
      :fetch-month-plan="fetchMonthPlan"
      :refresh="refresh"
    />

    <div v-show="appTab === 'overview'" class="game-layout">
    <DialogueBanner :message="bannerMessage" />
    <aside class="side-panel">
      <GameHeader :state="state" />
      <ChapterGoals :state="state" :flags="narrative.flags || {}" />
      <TreeStatus :tree="state.tree" />
      <AgentPanel :agents="state.agents" />
      <BondPanel :narrative="narrative" :reset-narrative="resetNarrative" />
    </aside>

    <main class="main-area">
      <div v-if="lastError" class="card error-card">
        {{ lastError }}
      </div>
      <div class="game-viewport-column" :class="{ 'tick-flash': tickFlash }">
        <div class="viewport-stack sao-window">
          <SceneDisplay :state="state" :agents="state.agents" />
          <ControlPanel
            class="control-hud"
            :auto-running="running"
            :loading="isLoading"
            :speed="speed"
            :llm-configured="llmConfigured"
            :llm-provider="llmProvider"
            :mode="mode"
            @update:speed="handleSpeedChange"
            @update:mode="mode = $event"
            @reset="handleReset"
            @toggle-auto="handleToggleAuto"
          />
        </div>
        <TimelineCard :events="events" class="log-dock" />
      </div>
    </main>

    <aside class="side-panel">
      <CharacterGallery />
      <div class="card help-card">
        <div class="card-title">操作说明</div>
        <div class="help-lines">
          <div>开始：自动运行游戏</div>
          <div>暂停：停止时间流逝</div>
          <div>速度：1倍(慢) / 2倍 / 5倍(快)</div>
          <div>规则模式：按内置规则行动</div>
          <div>智能模式：由大模型决策</div>
        </div>
      </div>
      <div v-if="llmConfigured" class="card">
        <div class="card-title">智能服务状态</div>
        <div class="llm-ok">{{ llmProvider }} 已连接</div>
      </div>
    </aside>

    <StoryChoiceModal
      :open="choiceModal.open"
      :type="choiceModal.type"
      @pick="onStoryChoicePick"
      @close="choiceModal.open = false"
    />
    <StoryEndingModal
      :open="endingModal.open"
      :ending-id="endingModal.id"
      @close="endingModal.open = false"
    />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import GameHeader from './components/GameHeader.vue'
import ChapterGoals from './components/ChapterGoals.vue'
import TreeStatus from './components/TreeStatus.vue'
import AgentPanel from './components/AgentPanel.vue'
import SceneDisplay from './components/SceneDisplay.vue'
import ControlPanel from './components/ControlPanel.vue'
import TimelineCard from './components/TimelineCard.vue'
import CharacterGallery from './components/CharacterGallery.vue'
import BondPanel from './components/BondPanel.vue'
import DialogueBanner from './components/DialogueBanner.vue'
import StoryChoiceModal from './components/StoryChoiceModal.vue'
import StoryEndingModal from './components/StoryEndingModal.vue'
import FieldSlice from './components/FieldSlice.vue'
import { useGameApi } from './composables/useGameApi'
import { useNarrativeProgress } from './composables/useNarrativeProgress.js'
import { sceneFromAgents } from './utils/sceneFromAgents.js'
import { CH1_CHOICE_PRESETS, BOND_LEADER_MIN } from './data/ch1Choices.js'
import { SCENE_ENTER_LINES, CHOICE_AFTER } from './data/ch1Dialogue.js'

const {
  state,
  events,
  running,
  llmConfigured,
  llmProvider,
  lastError,
  refresh,
  step,
  reset,
  toggleRun,
  checkLlm,
  setSpeed,
  dailyTick,
  playerAction,
  storyAdvance,
  fetchAvailableStoryEvents,
  chooseStoryEvent,
  fetchNpcProfile,
  sendDialogue,
  exportSave,
  importSave,
  fetchRegions,
  fetchWorldMap,
  fetchSceneActivities,
  fetchMonthPlan
} = useGameApi()

const appTab = ref('field')
const showDevTabs = computed(() => {
  if (typeof window === 'undefined') return false
  return new URLSearchParams(window.location.search).get('dev') === '1'
})

const {
  narrative,
  applyDeltas,
  resetNarrative,
  resetChapterFlags,
  setSyncedRunId,
  markC1Done,
  markC2Done,
  markEndingShown
} = useNarrativeProgress()

const speed = ref(1)
const mode = ref('heuristic')
const isLoading = ref(false)
const tickFlash = ref(false)

const choiceModal = ref({ open: false, type: 'c1' })
const endingModal = ref({ open: false, id: 'neutral' })
const bannerMessage = ref('')
let bannerTimer

const currentScene = computed(() => sceneFromAgents(state.value.agents || []))
const prevScene = ref(null)

function showBanner(msg, ms = 5200) {
  clearTimeout(bannerTimer)
  bannerMessage.value = msg
  bannerTimer = setTimeout(() => {
    bannerMessage.value = ''
  }, ms)
}

watch(currentScene, (scene) => {
  if (prevScene.value === null) {
    prevScene.value = scene
    return
  }
  if (prevScene.value === scene) return
  prevScene.value = scene
  const pool = SCENE_ENTER_LINES[scene]
  if (pool?.length) {
    const line = pool[Math.floor(Math.random() * pool.length)]
    showBanner(line)
  }
})

watch(
  () => state.value.tick,
  (tick, oldTick) => {
    if (oldTick === undefined) return
    if (choiceModal.value.open) return
    tickFlash.value = true
    setTimeout(() => { tickFlash.value = false }, 150)
  }
)

watch(
  () => [state.value.tree?.hp, state.value.tree?.state],
  () => {
    const tree = state.value.tree
    if (!tree) return
    const fallen = tree.hp <= 0 || tree.state === 'fallen'
    if (!fallen || narrative.value.endingShown) return
    markEndingShown()
    const b = narrative.value.bond
    const ids = ['alice', 'eugeo']
    let leader = 'alice'
    let max = -1
    for (const id of ids) {
      const v = b[id] ?? 0
      if (v > max) {
        max = v
        leader = id
      }
    }
    const endingId = max >= BOND_LEADER_MIN ? leader : 'neutral'
    endingModal.value = { open: true, id: endingId }
  },
  { deep: true }
)

function onStoryChoicePick(key) {
  const preset = CH1_CHOICE_PRESETS[key]
  if (preset) applyDeltas(preset.deltas, preset.label)
  if (String(key).startsWith('c1')) markC1Done()
  if (String(key).startsWith('c2')) markC2Done()
  choiceModal.value.open = false
  const after = CHOICE_AFTER[key]
  if (after) showBanner(after)
  nextTick(() => {
    const t = state.value.tick
    const f = narrative.value.flags
    if (!choiceModal.value.open && !f.c2Done && f.c1Done && t >= 30) {
      choiceModal.value = { open: true, type: 'c2' }
    }
  })
}

onMounted(async () => {
  try {
    await refresh()
    await checkLlm()
  } catch (e) {
    alert('初始化失败: ' + (e.message || '未知错误'))
  }
})

onUnmounted(() => clearTimeout(bannerTimer))

async function handleReset() {
  try {
    isLoading.value = true
    const j = await reset()
    resetChapterFlags()
    if (j?.run_id) setSyncedRunId(j.run_id)
  } catch (e) {
    alert('重置失败: ' + (e.message || '未知错误'))
  } finally {
    isLoading.value = false
  }
}

function handleToggleAuto() {
  if (running.value) {
    toggleRun()
  } else {
    toggleRun(1, mode.value)
  }
}

function handleSpeedChange(s) {
  setSpeed(s)
}
</script>

<style scoped>
.game-container {
  display: flex;
  flex-direction: column;
  max-width: 1320px;
  margin: 0 auto;
  min-height: 100vh;
  gap: 0.55rem;
  padding: 0.55rem 0.85rem 1rem;
}

.game-container.field-mode {
  max-width: none;
  width: 100%;
  height: 100vh;
  min-height: 100vh;
  padding: 0;
  gap: 0;
  overflow: hidden;
}

.field-mode .app-tabs {
  position: fixed;
  top: 0.7rem;
  right: 0.8rem;
  z-index: 120;
  width: auto;
  background: rgba(4, 8, 18, 0.72);
}

.app-tabs {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
  width: fit-content;
  padding: 0.22rem;
  border-radius: 10px;
  background: rgba(7, 12, 24, 0.72);
  border: 1px solid var(--sao-border-dim);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.tab-btn {
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0;
  padding: 0.42rem 0.82rem;
  border-radius: 8px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  transition: color 0.18s ease, border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
}

.tab-btn:hover:not(.active) {
  color: var(--ink);
  background: rgba(94, 207, 255, 0.06);
  border-color: var(--sao-border-dim);
}

.tab-btn.active {
  color: #fff;
  border-color: var(--sao-border);
  box-shadow: var(--sao-glow), inset 0 1px 0 rgba(255, 255, 255, 0.08);
  background-color: rgba(15, 23, 42, 0.5);
  background-image: linear-gradient(180deg, rgba(94, 207, 255, 0.12), rgba(15, 23, 42, 0.6));
  background-size: 100% 100%;
  background-repeat: no-repeat;
  background-position: center;
}

.game-layout {
  display: flex;
  flex: 1;
  gap: 1rem;
  align-items: flex-start;
  min-height: 0;
}

.side-panel {
  flex: 0 0 280px;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 960px;
  margin: 0 auto;
  min-width: 0;
}

.game-viewport-column {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

@keyframes tick-flash {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

.tick-flash {
  animation: tick-flash 0.15s ease-out;
}

.viewport-stack {
  position: relative;
  border-radius: 14px 14px 0 0;
  overflow: hidden;
  padding: 0;
}

.viewport-stack :deep(.scene-wrapper) {
  border-radius: 0;
}

.control-hud {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 12;
}

.log-dock {
  margin-top: -1px;
  border-radius: 0 0 14px 14px;
}

.help-lines {
  font-size: 0.75rem;
  color: var(--muted);
  line-height: 1.65;
}

.llm-ok {
  font-size: 0.8rem;
  color: var(--ok);
}

@media (max-width: 900px) {
  .game-container {
    padding: 0.45rem;
  }

  .app-tabs {
    width: 100%;
  }

  .field-mode .app-tabs {
    top: 0.55rem;
    right: 0.55rem;
    width: auto;
  }

  .tab-btn {
    flex: 1;
  }

  .game-layout {
    flex-direction: column;
  }

  .side-panel {
    flex: none;
    width: 100%;
  }
}
</style>
