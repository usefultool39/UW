<template>
  <div class="field-slice">
    <!-- Top header bar -->
    <FieldHeader
      :busy="busy"
      :npc-runtime="npcRuntime"
      @export-save="onExportSave"
      @import-save="onImportClick"
      @import-file="onImportFile"
      @refresh="onRefresh"
    />

    <OpeningCinematic
      :model-value="openingCinematicVisible"
      @focus-first-event="onOpeningFocusFirstEvent"
      @skip="onOpeningSkip"
    />

    <!-- Error banner -->
    <Transition name="err-slide">
      <div v-if="localError" class="field-err">
        <span>{{ localError }}</span>
        <button class="err-close" @click="localError = ''">×</button>
      </div>
    </Transition>

    <!-- Main playfield -->
    <div class="playfield-shell">
      <!-- Player HUD (top-left overlay) -->
      <PlayerHUD :sim-state="simState" :scene-label="sceneLabel" />

      <Transition name="brief-fade">
        <section v-if="openingBriefVisible" class="opening-brief" role="status">
          <div class="brief-kicker">清晨 · 细雨</div>
          <h3>巨神树下的午餐约定</h3>
          <p>尤吉欧还在完成今天的天职，爱丽丝已经带着午餐出发。先去巨神树与他们会合。</p>
          <div class="brief-actions">
            <button type="button" @click="focusFirstStoryEvent">查看线索</button>
            <button type="button" class="brief-ghost" @click="openingBriefDismissed = true">开始行动</button>
          </div>
        </section>
      </Transition>

      <!-- Phaser map canvas -->
      <FieldMap
        v-if="worldMapRef"
        :key="activeMapId"
        ref="mapRef"
        :sim-state="simState"
        :world-map="worldMapRef"
        :story-events="storyEvents"
        :scene-label="sceneLabel"
        :time-band-label="timeBandLabel"
        :busy="busy"
        :nearby-interact="effectiveNearbyInteract"
        :dev-mode="devMode"
        @tile-click="onTileClick"
        @npc-click="onNpcClick"
        @interact-click="openInteractPanel"
        @event-click="openStoryEvent"
        @ready="onSceneReady"
        @blocked-click="onBlockedTileClick"
      />
      <div v-else class="field-map-loading">正在同步村庄地图…</div>

      <!-- Right side quest tracker -->
      <QuestTracker
        :sim-state="simState"
        :story-events="storyEvents"
        :quest-guide="questGuide"
        :nearby-npc-label="nearbyNpcLabel"
        :nearby-interact-title="nearbyInteractTitle"
        :nearby-action-preview="nearbyActionPreview"
        :route-hint="newcomerRouteHint"
        :highlight-primary="newcomerGuideVisible"
        :busy="busy"
        @open-event="openRecommendedStoryEvent"
        @open-interact="openInteractPanel"
      />

      <!-- Bottom hotbar -->
      <Hotbar :busy="busy" :has-events="!!storyEvents.length" :day-gate="dayGateStatus" @action="onHotbarAction" />

      <ClueJournalPanel
        v-model="journalOpen"
        :sim-state="simState"
        :story-events="storyEvents"
        :month-plan="monthPlan"
        :recent-memories="recentJournalMemories"
        :npc-profiles="journalProfiles"
      />
    </div>

    <!-- Debug drawer (collapsed by default) -->
    <details v-if="devMode" class="debug-drawer">
      <summary>开发调试与操作说明</summary>
      <div class="field-toolbar">
        <div class="tb-group">
          <span class="tb-label">剧情闸</span>
          <button type="button" class="tb tb-ghost" :disabled="busy" @click="onFlag">标记「读完书」</button>
          <button type="button" class="tb tb-accent" :disabled="busy" @click="onStory">推进 → mq01</button>
        </div>
      </div>
      <p class="field-hint">
        左键点按目标格移动；右键或中键拖动大地图；小地图拖拽或点按可移动视野；滚轮缩放。走进亮框功能区后，点击地图上的「进入场景」按钮打开每日行动面板。
      </p>
    </details>

    <!-- Regions JSON (dev only) -->
    <details v-if="devMode && regionsJson" class="regions-details">
      <summary>区域表 JSON</summary>
      <pre class="regions-pre">{{ regionsJson }}</pre>
    </details>

    <!-- Modals -->
    <FieldInteractPanel
      v-model="interactOpen"
      :nearby-interact="effectiveNearbyInteract"
      :visible-interact-actions="visibleInteractActions"
      :sim-state="simState"
      :busy="busy"
      @interact-action="onInteractAction"
    />

    <NpcInteractPanel
      v-model="npcPanelOpen"
      :npc="selectedNpc"
      :busy="busy"
      @talk="onNpcTalk"
      @relationship="onNpcRelationship"
    />

    <DialoguePanel
      v-model="dialogueOpen"
      :npc="selectedNpc"
      :send-dialogue="sendDialogue"
      :player-scene-id="simState?.player?.scene_id || simState?.scene_id || ''"
    />

    <StoryEventPanel
      v-if="storyEventOpen && selectedStoryEvent"
      v-model="storyEventOpen"
      :event="selectedStoryEvent"
      :busy="busy"
      @choose="onStoryEventChoose"
    />

    <StoryEventPanel
      v-if="activityChoiceOpen && selectedActivityChoiceEvent"
      v-model="activityChoiceOpen"
      :event="selectedActivityChoiceEvent"
      :busy="busy"
      @choose="onActivityChoiceChoose"
    />

    <TrainingMiniGamePanel
      v-model="trainingGameOpen"
      :event="selectedStoryEvent"
      :busy="busy"
      @complete="onTrainingComplete"
    />

    <BoundaryProbeMiniGamePanel
      v-model="boundaryProbeOpen"
      :event="selectedStoryEvent"
      :busy="busy"
      @complete="onBoundaryProbeComplete"
    />

    <BoundaryVerdictMiniGamePanel
      v-model="boundaryVerdictOpen"
      :event="selectedStoryEvent"
      :busy="busy"
      @complete="onBoundaryVerdictComplete"
    />

    <ReadingMiniGamePanel
      v-model="readingGameOpen"
      :activity="pendingActivityAction?.activity"
      :busy="busy"
      @complete="onActivityComplete"
    />

    <MealChoicePanel
      v-model="mealChoiceOpen"
      :activity="pendingActivityAction?.activity"
      :busy="busy"
      @complete="onActivityComplete"
    />

    <BoundaryPatrolMiniGamePanel
      v-model="boundaryPatrolOpen"
      :activity="pendingActivityAction?.activity"
      :player="simState?.player"
      :busy="busy"
      @complete="onActivityComplete"
    />

    <StoryResultPanel
      v-model="storyResultOpen"
      :result="storyResult"
      @focus-event="onResultFocusEvent"
    />

    <NpcProfilePanel
      v-model="npcProfileOpen"
      :profile="npcProfile"
    />

    <!-- Toast notification -->
    <Toast v-model="toastOpen" :message="toastMessage" :type="toastType" />

    <!-- Hidden file input for import -->
    <input ref="saveFileEl" class="save-file" type="file" accept="application/json,.json" @change="onImportFile" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import FieldHeader from './FieldHeader.vue'
import PlayerHUD from './PlayerHUD.vue'
import FieldMap from './FieldMap.vue'
import QuestTracker from './QuestTracker.vue'
import Hotbar from './Hotbar.vue'
import FieldInteractPanel from './FieldInteractPanel.vue'
import NpcInteractPanel from './NpcInteractPanel.vue'
import DialoguePanel from './DialoguePanel.vue'
import StoryEventPanel from './StoryEventPanel.vue'
import StoryResultPanel from './StoryResultPanel.vue'
import NpcProfilePanel from './NpcProfilePanel.vue'
import ClueJournalPanel from './ClueJournalPanel.vue'
import OpeningCinematic from './OpeningCinematic.vue'
import TrainingMiniGamePanel from './TrainingMiniGamePanel.vue'
import BoundaryProbeMiniGamePanel from './BoundaryProbeMiniGamePanel.vue'
import BoundaryVerdictMiniGamePanel from './BoundaryVerdictMiniGamePanel.vue'
import ReadingMiniGamePanel from './ReadingMiniGamePanel.vue'
import MealChoicePanel from './MealChoicePanel.vue'
import BoundaryPatrolMiniGamePanel from './BoundaryPatrolMiniGamePanel.vue'
import Toast from './Toast.vue'
import { getAgentLabel, getQuestGuide, getSceneLabel, getTimeBandLabel } from '../field/gameContentConfig.js'
import { findNearbyInteractPoi } from '../field/interactPoi.js'
import { DEFAULT_MAP_ID } from '../field/sceneRegistry.js'
import { dedupeActivityActions } from '../field/interactActionMerge.js'
import { activityCompletionMessage, activityIdForAction, activityOpenMessage, activityPanelKind, activityResultExtras, shouldOpenActivityChoicePanel, shouldOpenActivityPanel } from '../field/activityRegistry.js'
import { useAudio } from '../composables/useAudio.js'
import { useFieldToast } from '../composables/useFieldToast.js'
import { compactPlayerText, uwCanonText } from '../utils/uwCanonText.js'

// Audio composable for field ambience and interaction feedback
const { playSfx, startFieldAudio } = useAudio()
const { toastMessage, toastType, toastOpen, showToast, clearToastTimer } = useFieldToast()

const props = defineProps({
  simState: { type: Object, required: true },
  devMode: { type: Boolean, default: false },
  npcRuntime: { type: String, default: 'scripted' },
  dailyTick: { type: Function, required: true },
  playerAction: { type: Function, required: true },
  storyAdvance: { type: Function, required: true },
  fetchAvailableStoryEvents: { type: Function, required: true },
  chooseStoryEvent: { type: Function, required: true },
  fetchNpcProfile: { type: Function, required: true },
  sendDialogue: { type: Function, required: true },
  exportSave: { type: Function, required: true },
  importSave: { type: Function, required: true },
  fetchRegions: { type: Function, required: true },
  fetchWorldMap: { type: Function, required: true },
  fetchSceneActivities: { type: Function, required: true },
  fetchMonthPlan: { type: Function, required: true },
  refresh: { type: Function, required: true }
})

// --- Refs ---
const mapRef = ref(null)
const saveFileEl = ref(null)
const busy = ref(false)
const localError = ref('')
const regionsJson = ref('')
const worldMapRef = ref(null)
const sceneActivityIndex = ref({})
const storyEvents = ref([])
const monthPlan = ref(null)
const selectedStoryEventId = ref('')
const selectedNpcId = ref('')
const openingCinematicDismissed = ref(false)
const openingBriefDismissed = ref(false)
const journalOpen = ref(false)
const journalProfiles = ref({})
const recentJournalMemories = ref([])
const dayGateStatus = computed(() => ({
  day: Number(props.simState?.day || 1),
  ready: true,
  label: '剧情结算',
}))

// Modal states
const interactOpen = ref(false)
const npcPanelOpen = ref(false)
const dialogueOpen = ref(false)
const storyEventOpen = ref(false)
const activityChoiceOpen = ref(false)
const storyResultOpen = ref(false)
const npcProfileOpen = ref(false)
const trainingGameOpen = ref(false)
const boundaryProbeOpen = ref(false)
const boundaryVerdictOpen = ref(false)
const readingGameOpen = ref(false)
const mealChoiceOpen = ref(false)
const boundaryPatrolOpen = ref(false)
const pendingActivityAction = ref(null)
const storyResult = ref(null)

const activityPanelRefs = Object.freeze({
  reading: readingGameOpen,
  meal: mealChoiceOpen,
  patrol: boundaryPatrolOpen
})
const npcProfile = ref(null)

let sceneInstance = null


// --- Computed ---
const sceneLabel = computed(() => getSceneLabel(props.simState?.player?.scene_id || props.simState?.scene_id || ''))
const timeBandLabel = computed(() => getTimeBandLabel(props.simState?.time_band || 'morning'))
const activeMapId = computed(() => props.simState?.player?.map_id || props.simState?.map_id || DEFAULT_MAP_ID)

const nearbyInteract = computed(() =>
  findNearbyInteractPoi(worldMapRef.value, props.simState?.player)
)

const nearbyStoryEvents = computed(() => {
  const p = props.simState?.player
  if (!p) return []
  const px = Number(p.tile_x)
  const py = Number(p.tile_y)
  if (!Number.isFinite(px) || !Number.isFinite(py)) return []
  return storyEvents.value
    .map((event) => {
      const loc = event?.location || {}
      const tx = Number(loc.tile_x)
      const ty = Number(loc.tile_y)
      if (!Number.isFinite(tx) || !Number.isFinite(ty)) return null
      const dist = Math.max(Math.abs(px - tx), Math.abs(py - ty))
      const sameScene = String(loc.scene_id || '') && String(loc.scene_id || '') === String(p.scene_id || props.simState?.scene_id || '')
      if (dist > 4 && !(sameScene && dist <= 7)) return null
      return { event, dist }
    })
    .filter(Boolean)
    .sort((a, b) => a.dist - b.dist)
    .map((item) => item.event)
})

const npcIntents = computed(() =>
  Array.isArray(props.simState?.npc_intents) ? props.simState.npc_intents : []
)

const nearbyNpcIntents = computed(() => {
  const p = props.simState?.player
  if (!p) return []
  const px = Number(p.tile_x)
  const py = Number(p.tile_y)
  const playerScene = String(p.scene_id || props.simState?.scene_id || '')
  if (!Number.isFinite(px) || !Number.isFinite(py)) return []
  return npcIntents.value
    .map((intent) => {
      const tx = Number(intent?.tile_x)
      const ty = Number(intent?.tile_y)
      const sceneId = String(intent?.scene_id || '')
      if (!Number.isFinite(tx) || !Number.isFinite(ty)) return null
      const dist = Math.max(Math.abs(px - tx), Math.abs(py - ty))
      const sameScene = sceneId && sceneId === playerScene
      // 场景入口和 NPC 意图坐标可能分处同一场景的不同交互点。
      // 玩家已经进入目标场景时，应能直接从互动面板回应同伴，避免“目标就在这里却点不到”。
      if (!sameScene) return null
      return { intent, dist }
    })
    .filter(Boolean)
    .sort((a, b) => (Number(b.intent?.priority || 0) - Number(a.intent?.priority || 0)) || a.dist - b.dist)
    .map((item) => item.intent)
})

const effectiveNearbyInteract = computed(() => {
  if (nearbyInteract.value) return nearbyInteract.value
  const event = nearbyStoryEvents.value[0]
  if (!event) {
    const intent = nearbyNpcIntents.value[0]
    if (!intent) return null
    return {
      id: `intent_${intent.id}`,
      kind: 'interact',
      scene_id: intent.scene_id || props.simState?.player?.scene_id || props.simState?.scene_id,
      tile_x: Number(intent.tile_x) || Number(props.simState?.player?.tile_x) || 0,
      tile_y: Number(intent.tile_y) || Number(props.simState?.player?.tile_y) || 0,
      radius: 2,
      regionType: 'interact',
      zoneLabel: 'NPC 主动',
      label: 'NPC 主动',
      title: intent.title || '附近有人想和你确认一件事',
      body: intent.description || intent.reason || '这个 NPC 正在根据今天发生的事做出反应。',
      actions: []
    }
  }
  const loc = event.location || {}
  return {
    id: `story_${event.id}`,
    kind: 'interact',
    scene_id: loc.scene_id || props.simState?.player?.scene_id || props.simState?.scene_id,
    tile_x: Number(loc.tile_x) || Number(props.simState?.player?.tile_x) || 0,
    tile_y: Number(loc.tile_y) || Number(props.simState?.player?.tile_y) || 0,
    radius: 2,
    regionType: 'interact',
    zoneLabel: '线索地点',
    label: '线索地点',
    title: event.title || '附近线索',
    body: event.description || '这里有一段正在发生的剧情线索。',
    actions: []
  }
})

const naturalStoryEventActions = computed(() =>
  nearbyStoryEvents.value.map((event) => ({
    id: `story:${event.id}`,
    type: 'story_event',
    event_id: event.id,
    label: naturalStoryEventLabel(event),
    description: event.description || '',
    meta: storyEventMeta(event),
    storyEvent: event
  }))
)

const npcIntentActions = computed(() =>
  nearbyNpcIntents.value
    .flatMap(enrichNpcIntentActions)
    .filter(Boolean)
)

const visibleInteractActions = computed(() => {
  const poi = nearbyInteract.value
  const nid = props.simState?.story_node_id
  const base = poi?.actions
    ? poi.actions
      .filter((a) => !a.requires_story || a.requires_story === nid)
      .map(enrichInteractAction)
    : []
  return dedupeActivityActions([
    ...npcIntentActions.value,
    ...naturalStoryEventActions.value,
    ...base
  ])
})

const selectedNpc = computed(() =>
  (props.simState?.agents || []).find((a) => a.id === selectedNpcId.value) || null
)

const selectedStoryEvent = computed(() =>
  storyEvents.value.find((e) => e.id === selectedStoryEventId.value) || storyEvents.value[0] || null
)

const selectedActivityChoiceEvent = computed(() => {
  const activity = pendingActivityAction.value?.activity
  if (!activity) return null
  return {
    id: activity.id,
    kind: 'scene_activity',
    title: activity.title || activity.label || '选择行动方式',
    description: activity.description || '',
    location: { scene_id: activity.scene_id || props.simState?.player?.scene_id || '' },
    participants: activity.participants || [],
    choices: activity.choices || []
  }
})

const nearbyNpcs = computed(() => {
  const p = props.simState?.player
  if (!p) return []
  const px = Number(p.tile_x)
  const py = Number(p.tile_y)
  if (!Number.isFinite(px) || !Number.isFinite(py)) return []
  return (props.simState?.agents || [])
    .filter((a) => Number.isFinite(Number(a?.tile_x)) && Number.isFinite(Number(a?.tile_y)))
    .filter((a) => {
      const dx = Number(a.tile_x) - px
      const dy = Number(a.tile_y) - py
      return Math.sqrt(dx * dx + dy * dy) <= 3
    })
})

const nearbyNpcLabel = computed(() => {
  if (!nearbyNpcs.value.length) return '暂无 NPC'
  return nearbyNpcs.value.map((a) => getAgentLabel(a.id)).join('、')
})

const nearbyInteractTitle = computed(() => {
  const poi = effectiveNearbyInteract.value
  if (!poi) return '暂无地点'
  if (poi.zoneEntry && poi.zoneLabel) return `${poi.zoneLabel} · ${poi.title || poi.label || '可互动'}`
  return poi.title || '暂无地点'
})

function actionPreviewMeta(action) {
  if (action?.type === 'npc_intent_response') return `${getAgentLabel(action.npc_id)}会记住你的态度`
  if (action?.source === 'npc_intent') return '同伴主动事件'
  if (action?.type === 'story_event') return `主线 · ${getSceneLabel(action?.storyEvent?.location?.scene_id || '')}`
  if (action?.type === 'scene_activity') return action?.blockedReason || action?.meta || '消耗时间，获得进展'
  return action?.blockedReason || action?.meta || ''
}

const nearbyActionPreview = computed(() =>
  visibleInteractActions.value.slice(0, 2).map((action) => ({
    id: action.id,
    label: compactPlayerText(action.label, 34),
    meta: compactPlayerText(actionPreviewMeta(action), 42),
    blocked: !!action.blockedReason
  }))
)

const playerSceneId = computed(() => props.simState?.player?.scene_id || props.simState?.scene_id || '')

function storyEventDistance(event) {
  const p = props.simState?.player
  const loc = event?.location || {}
  const px = Number(p?.tile_x)
  const py = Number(p?.tile_y)
  const tx = Number(loc.tile_x)
  const ty = Number(loc.tile_y)
  if (![px, py, tx, ty].every(Number.isFinite)) return null
  return Math.max(Math.abs(px - tx), Math.abs(py - ty))
}

function isStoryEventReachable(event) {
  const loc = event?.location || {}
  const eventScene = String(loc.scene_id || '')
  const currentScene = String(playerSceneId.value || '')
  if (eventScene && currentScene && eventScene !== currentScene) return false
  const dist = storyEventDistance(event)
  if (!Number.isFinite(dist)) return true
  return dist <= 7
}

function focusStoryEventLocation(event) {
  const loc = event?.location || {}
  const tx = Number(loc.tile_x)
  const ty = Number(loc.tile_y)
  if (Number.isFinite(tx) && Number.isFinite(ty)) {
    sceneInstance?.centerCameraOnTile?.(tx, ty)
  }
}

function guideToStoryEvent(event) {
  focusStoryEventLocation(event)
  const scene = event?.location?.scene_id ? getSceneLabel(event.location.scene_id) : '线索地点'
  showToast(`先去${scene}附近，再打开互动回应。`, 'info')
}

const primaryStoryEvent = computed(() => storyEvents.value[0] || null)

const primaryEventDistance = computed(() => storyEventDistance(primaryStoryEvent.value))

const primaryEventSameScene = computed(() => {
  const loc = primaryStoryEvent.value?.location || {}
  return !!loc.scene_id && String(loc.scene_id) === String(playerSceneId.value)
})

const newcomerRouteHint = computed(() => {
  const event = primaryStoryEvent.value
  if (!event) return ''
  const scene = event?.location?.scene_id ? getSceneLabel(event.location.scene_id) : ''
  const dist = primaryEventDistance.value
  if (primaryEventSameScene.value && Number.isFinite(dist)) {
    if (dist <= 4) return `${scene || '线索点'}就在附近`
    return `${scene || '线索点'} · 约 ${dist} 格`
  }
  return scene ? `前往 ${scene}` : '跟随金色线索'
})

const anyModalOpen = computed(() =>
  interactOpen.value ||
  npcPanelOpen.value ||
  dialogueOpen.value ||
  storyEventOpen.value ||
  activityChoiceOpen.value ||
  storyResultOpen.value ||
  npcProfileOpen.value ||
  trainingGameOpen.value ||
  boundaryProbeOpen.value ||
  boundaryVerdictOpen.value ||
  readingGameOpen.value ||
  mealChoiceOpen.value ||
  boundaryPatrolOpen.value ||
  journalOpen.value
)

// 新手信息只保留开场与右侧主线卡，避免三个引导层同时争夺注意力。
const newcomerGuideVisible = computed(() =>
  shouldShowDayOneOpening.value &&
  openingCinematicDismissed.value &&
  openingBriefDismissed.value
)

function compactGuideText(value, maxLength = 30) {
  const text = String(value || '').replace(/\s+/g, ' ').trim()
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, maxLength - 1)}…` : text
}

function buildIntentQuestGuide(intent) {
  const agent = getAgentLabel(intent?.npc_id)
  const title = compactGuideText(intent?.title || intent?.reason || '回应这次主动邀约', 28)
  const scene = intent?.scene_id ? getSceneLabel(intent.scene_id) : ''
  const placeHint = scene ? `去${scene}` : '走近同伴'
  const action = intent?.action?.type === 'training' ? '开始训练' : '打开互动回应'
  return `${agent}在等你：${title}。${placeHint}，${action}。`
}

function buildEventQuestGuide(event) {
  if (event?.id === 'ch1_d24_expedition_pack') {
    return '远征准备：去小屋整理远征包。这个选择会决定第二月偏稳妥推进，还是扩大调查范围。'
  }
  const title = compactGuideText(event?.title || '新的线索', 30)
  const scene = event?.location?.scene_id ? getSceneLabel(event.location.scene_id) : ''
  const placeHint = scene ? `去${scene}` : '靠近金色标记'
  return `${title}：${placeHint}处理这条线索。`
}

const questGuide = computed(() => {
  // 主线永远保持单一焦点；附近的 NPC 主动事件显示为可选互动，
  // 避免“去书库”和“回应同伴”同时被标成当前目标。
  if (storyEvents.value.length) {
    return uwCanonText(buildEventQuestGuide(storyEvents.value[0]))
  }
  const intent = nearbyNpcIntents.value[0] || npcIntents.value[0]
  if (intent) {
    return uwCanonText(buildIntentQuestGuide(intent))
  }
  return uwCanonText(getQuestGuide(props.simState))
})

const shouldShowDayOneOpening = computed(() =>
  Number(props.simState?.day || 1) === 1 &&
  String(props.simState?.story_node_id || '') === 'mq00_tutorial' &&
  String(playerSceneId.value) === 'village_square' &&
  !props.simState?.chapter_ending_id &&
  storyEvents.value.length > 0
)

const openingCinematicVisible = computed(() =>
  !openingCinematicDismissed.value &&
  shouldShowDayOneOpening.value
)

const openingBriefVisible = computed(() =>
  openingCinematicDismissed.value &&
  !openingBriefDismissed.value &&
  shouldShowDayOneOpening.value
)

async function startOpeningAudio() {
  await startFieldAudio(props.simState?.weather || 'drizzle')
}

async function onOpeningFocusFirstEvent() {
  openingCinematicDismissed.value = true
  openingBriefDismissed.value = true
  await startOpeningAudio()
  await nextTick()
  focusFirstStoryEvent()
}

async function onOpeningSkip() {
  openingCinematicDismissed.value = true
  openingBriefDismissed.value = true
  await startOpeningAudio()
  showToast('跟随金色指引，先去教会书库确认异常记录。', 'info')
}

// --- Scene ---
function onSceneReady(sc) {
  sceneInstance = sc
}

// --- Story Events ---
async function refreshStoryEvents() {
  try {
    const res = await props.fetchAvailableStoryEvents()
    storyEvents.value = Array.isArray(res?.events) ? res.events : []
  } catch {
    storyEvents.value = []
  }
  await refreshMonthPlan()
}

function getActiveMonthPlanId() {
  return 'month_01'
}

async function refreshMonthPlan() {
  try {
    const res = await props.fetchMonthPlan(getActiveMonthPlanId())
    monthPlan.value = res?.ok === false ? null : res
  } catch {
    monthPlan.value = null
  }
}

async function loadWorldMap(mapId = DEFAULT_MAP_ID) {
  worldMapRef.value = null
  try {
    worldMapRef.value = await props.fetchWorldMap(mapId)
    localError.value = ''
  } catch {
    localError.value = `地图加载失败：${mapId}`
    worldMapRef.value = { id: mapId, rows: [], width: 0, height: 0, tile_size: 28 }
  }
}

async function loadSceneActivities() {
  try {
    const res = await props.fetchSceneActivities()
    const activities = Array.isArray(res?.activities) ? res.activities : []
    sceneActivityIndex.value = Object.fromEntries(
      activities.filter((a) => a?.id).map((a) => [a.id, a])
    )
  } catch {
    sceneActivityIndex.value = {}
  }
}

function activityAvailability(activity) {
  if (!activity) return { ok: true, reason: '' }
  const playerScene = props.simState?.player?.scene_id || props.simState?.scene_id || ''
  const sceneIds = Array.isArray(activity.scene_ids)
    ? activity.scene_ids
    : activity.scene_id
      ? [activity.scene_id]
      : []
  if (sceneIds.length && !sceneIds.includes(playerScene)) {
    return { ok: false, reason: '走到对应地点范围后可用' }
  }

  const timeBand = props.simState?.time_band || 'morning'
  const timeBands = Array.isArray(activity.time_bands) ? activity.time_bands : []
  if (timeBands.length && !timeBands.includes(timeBand)) {
    return { ok: false, reason: `开放时段：${timeBands.map(getTimeBandLabel).join('、')}` }
  }

  const currentDay = Number(props.simState?.day || 1)
  const dayMin = activity.requirements?.day_min
  const dayMax = activity.requirements?.day_max
  if (dayMin != null && currentDay < Number(dayMin)) {
    return { ok: false, reason: `第 ${dayMin} 天起开放` }
  }
  if (dayMax != null && currentDay > Number(dayMax)) {
    return { ok: false, reason: `已在第 ${dayMax} 天结束` }
  }

  const requiredFlags = activity.requirements?.required_flags || {}
  const flags = props.simState?.flags || {}
  for (const [key, value] of Object.entries(requiredFlags)) {
    if (Number(flags[key] || 0) < Number(value || 0)) {
      return { ok: false, reason: '需要先完成前置线索' }
    }
  }

  const requiredAnyFlags = activity.requirements?.required_any_flags || {}
  if (Object.keys(requiredAnyFlags).length) {
    const anyMet = Object.entries(requiredAnyFlags).some(
      ([key, value]) => Number(flags[key] || 0) >= Number(value || 0)
    )
    if (!anyMet) {
      return { ok: false, reason: '需要先完成任一前置线索' }
    }
  }

  const repeat = activity.repeat || 'free'
  if (repeat === 'once' && Number(flags[`activity_done.${activity.id}`] || 0) >= 1) {
    return { ok: false, reason: '已经完成' }
  }
  if (repeat === 'daily' && Number(flags[`activity_day.${activity.id}`] || -1) === Number(props.simState?.day || 1)) {
    return { ok: false, reason: '今天已完成' }
  }
  return { ok: true, reason: '' }
}

function enrichInteractAction(action) {
  if (action?.type !== 'scene_activity') return action
  const activity = sceneActivityIndex.value[action.activity_id || action.id]
  if (!activity) return action
  const availability = activityAvailability(activity)
  const meta = []
  if (action.meta) meta.push(action.meta)
  const timeCost = Number(activity.time_cost || 0)
  meta.push(timeCost > 0 ? `耗时 ${timeCost} 刻` : '不消耗时段')
  if (activity.repeat === 'daily') meta.push('每日一次')
  if (activity.repeat === 'once') meta.push('一次性')
  if (Array.isArray(activity.time_bands) && activity.time_bands.length) {
    meta.push(activity.time_bands.map(getTimeBandLabel).join(' / '))
  }
  if (!availability.ok && availability.reason) meta.push(availability.reason)
  return {
    ...action,
    label: action.label || activity.label,
    description: action.description || activity.description || '',
    meta: meta.join(' · '),
    blockedReason: availability.ok ? '' : availability.reason,
    activity
  }
}

function naturalStoryEventLabel(event) {
  const kind = String(event?.kind || '')
  if (event?.id === 'ch1_d24_expedition_pack') return '整理远征包'
  if (kind === 'clue') return '调查边界记录'
  if (kind === 'training') return '开始巨树训练'
  if (kind === 'anomaly') return '确认森林异常'
  if (kind === 'conflict') return '进入晚餐分歧'
  if (kind === 'final_choice') return '走向边界线'
  return event?.title ? `处理：${event.title}` : '触发章节线索'
}

function storyEventMeta(event) {
  const parts = ['章节事件']
  const participants = Array.isArray(event?.participants) ? event.participants : []
  if (participants.length) parts.push(`相关：${participants.map(getAgentLabel).join('、')}`)
  const sceneId = event?.location?.scene_id
  if (sceneId) parts.push(getSceneLabel(sceneId))
  return parts.join(' · ')
}

function enrichNpcIntentActions(intent) {
  const responses = Array.isArray(intent?.response_options) ? intent.response_options : []
  const responseActions = responses.map((option) => enrichNpcIntentResponseAction(intent, option)).filter(Boolean)
  const primary = enrichNpcIntentAction(intent)
  return primary ? [...responseActions, primary] : responseActions
}

function enrichNpcIntentResponseAction(intent, option) {
  const responseId = String(option?.id || '').trim()
  if (!responseId) return null
  const stakes = Array.isArray(intent?.stakes) ? intent.stakes.filter(Boolean).slice(0, 1) : []
  const meta = [
    `NPC回应 · ${getAgentLabel(intent.npc_id)}`,
    getSceneLabel(intent.scene_id),
    option?.tone ? `语气：${option.tone}` : '',
    ...stakes
  ].filter(Boolean).join(' · ')
  return {
    id: `intent-response:${intent.id}:${responseId}`,
    type: 'npc_intent_response',
    intent_id: intent.id,
    response_id: responseId,
    npc_id: intent.npc_id,
    label: option.label || '回应 NPC',
    description: option.hint || intent.description || intent.reason || '',
    meta,
    source: 'npc_intent',
    npcIntent: intent,
    responseOption: option
  }
}

function enrichNpcIntentAction(intent) {
  const action = intent?.action || {}
  const type = action.type || ''
  const stakes = Array.isArray(intent?.stakes) ? intent.stakes.filter(Boolean).slice(0, 1) : []
  const baseMeta = [`NPC主动 · ${getAgentLabel(intent.npc_id)}`, getSceneLabel(intent.scene_id), ...stakes].filter(Boolean).join(' · ')
  if (type === 'story_event' && action.event_id) {
    return {
      id: `intent:${intent.id}`,
      type: 'story_event',
      event_id: action.event_id,
      label: intent.title || '回应 NPC',
      description: intent.description || intent.reason || '',
      meta: baseMeta,
      source: 'npc_intent',
      npcIntent: intent
    }
  }
  if (type === 'scene_activity' && action.activity_id) {
    const activity = sceneActivityIndex.value[action.activity_id]
    return enrichInteractAction({
      id: `intent:${intent.id}`,
      type: 'scene_activity',
      activity_id: action.activity_id,
      label: intent.title
        ? `${intent.title}${activity?.label ? ` · ${activity.label}` : ''}`
        : activity?.label || '回应 NPC',
      description: intent.description || activity?.description || '',
      meta: baseMeta,
      source: 'npc_intent',
      activity,
      npcIntent: intent
    })
  }
  if (type === 'dialogue') {
    return {
      id: `intent:${intent.id}`,
      type: 'npc_dialogue',
      npc_id: intent.npc_id,
      label: intent.title || `和 ${getAgentLabel(intent.npc_id)} 交谈`,
      description: intent.description || intent.reason || '',
      meta: baseMeta,
      source: 'npc_intent',
      npcIntent: intent
    }
  }
  return null
}

function openStoryEvent(eventId, options = {}) {
  selectedStoryEventId.value = eventId
  const event = storyEvents.value.find((e) => e.id === eventId) || selectedStoryEvent.value
  if (options.requireReachable && !isStoryEventReachable(event)) {
    guideToStoryEvent(event)
    return false
  }
  if (event?.kind === 'training') {
    trainingGameOpen.value = true
    return true
  }
  if (event?.kind === 'anomaly') {
    boundaryProbeOpen.value = true
    return true
  }
  if (event?.kind === 'final_choice') {
    boundaryVerdictOpen.value = true
    return true
  }
  storyEventOpen.value = true
  return true
}

function openRecommendedStoryEvent(eventId) {
  if (!eventId) return false
  return openStoryEvent(eventId, { requireReachable: true })
}

function openInteractPanel() {
  const modalOpen =
    storyResultOpen.value ||
    storyEventOpen.value ||
    activityChoiceOpen.value ||
    trainingGameOpen.value ||
    boundaryProbeOpen.value ||
    boundaryVerdictOpen.value ||
    readingGameOpen.value ||
    mealChoiceOpen.value ||
    boundaryPatrolOpen.value ||
    dialogueOpen.value ||
    npcPanelOpen.value ||
    npcProfileOpen.value ||
    journalOpen.value
  if (busy.value || modalOpen) return
  interactOpen.value = true
}

function focusFirstStoryEvent() {
  const event = storyEvents.value[0]
  focusStoryEventLocation(event)
  openingBriefDismissed.value = true
  if (event?.id) {
    window.setTimeout(() => openRecommendedStoryEvent(event.id), 180)
  }
}

function onResultFocusEvent(payload) {
  const loc = payload?.location || {}
  const tx = Number(loc.tile_x)
  const ty = Number(loc.tile_y)
  if (Number.isFinite(tx) && Number.isFinite(ty)) {
    sceneInstance?.centerCameraOnTile?.(tx, ty)
    storyResultOpen.value = false
    showToast('镜头已带到下一条线索附近。')
  }
}

// --- Player Actions ---
async function onTileClick({ tile_x, tile_y }) {
  if (busy.value) return
  busy.value = true
  localError.value = ''
  let walkPromise = null
  let walkStarted = false
  try {
    const localPath = sceneInstance?.buildLocalPathTo?.(tile_x, tile_y)
    if (sceneInstance?.playWalkPath && Array.isArray(localPath) && localPath.length > 1) {
      walkStarted = true
      walkPromise = sceneInstance.playWalkPath(localPath)
      playSfx('/assets/audio/sfx_step.mp3')
    }
    const j = await props.playerAction(
      { kind: 'move_map', map_id: activeMapId.value, tile_x, tile_y },
      { deferRefresh: true }
    )
    const path = j.path || []
    if (!walkStarted && sceneInstance?.playWalkPath) {
      walkPromise = sceneInstance.playWalkPath(path)
      if (path.length > 1) playSfx('/assets/audio/sfx_step.mp3')
    }
    if (walkPromise) await walkPromise
    await props.refresh()
    if (sceneInstance?.syncPlayerFromState) sceneInstance.syncPlayerFromState()
  } catch (e) {
    sceneInstance?.cancelWalk?.()
    sceneInstance?.syncPlayerFromState?.()
    const msg = e.message || String(e)
    if (msg.includes('zone_locked') || msg.includes('scene_locked')) {
      showToast('这里还没开放。先完成当前目标，之后再回来探索边界。')
    } else if (msg.includes('unreachable_or_blocked')) {
      showToast('前方是尚未开放或无法通行的边界。先在村内完成当前目标。')
    } else {
      localError.value = msg
    }
    sceneInstance?.triggerCameraShake?.()
  } finally {
    sceneInstance?.resumeCameraFollow?.()
    busy.value = false
  }
}

function onBlockedTileClick(payload) {
  const label = payload?.terrainLabel || payload?.zone?.label || '未开放区域'
  if (payload?.reason === 'terrain_blocked') {
    showToast(`${label}不能通行。沿着浅色道路和草地边缘移动会更安全。`)
    sceneInstance?.triggerCameraShake?.()
    return
  }
  showToast(`${label} 还没开放。先完成当前目标，之后再回来探索边界。`)
}

function onNpcClick(agentId) {
  selectedNpcId.value = agentId
  npcPanelOpen.value = true
  showToast(`靠近 ${getAgentLabel(agentId)}：可以对话或查看关系。`)
}

async function onHotbarAction(actionId) {
  if (actionId === 'talk') {
    const npc = nearbyNpcs.value[0]
    if (!npc) { showToast('先靠近地图上的 NPC，再按对话。'); return }
    selectedNpcId.value = npc.id
    dialogueOpen.value = true
  } else if (actionId === 'read') {
    const activity = sceneActivityIndex.value.church_read_sacred_arts
    const availability = activityAvailability(activity)
    if (!activity || !availability.ok) {
      showToast(availability.reason || '先走到书库阅览台附近，再调查旧记录。')
      return
    }
    const action = {
      id: 'church_read_sacred_arts',
      type: 'scene_activity',
      activity_id: 'church_read_sacred_arts',
      activity
    }
    pendingActivityAction.value = action
    setActivityPanelOpen(action, true)
  } else if (actionId === 'train') {
    const trainingEvent = nearbyStoryEvents.value.find((event) => event?.kind === 'training')
      || storyEvents.value.find((event) => event?.kind === 'training' && (event?.location?.scene_id === props.simState?.player?.scene_id))
    if (trainingEvent?.id) {
      selectedStoryEventId.value = trainingEvent.id
      trainingGameOpen.value = true
      showToast('尤吉欧已经摆好训练节奏。先完成三次出手，再决定怎么回应他。')
      return
    }
    const trainingIntent = nearbyNpcIntents.value.find((intent) => intent?.action?.event_id === 'ch1_d1_training_with_eugeo')
    if (trainingIntent?.action?.event_id) {
      selectedStoryEventId.value = trainingIntent.action.event_id
      trainingGameOpen.value = true
      showToast('尤吉欧向你示意：训练从现在开始。')
      return
    }
    showToast('先走到巨神树伐木场，靠近尤吉欧后再开始训练。')
  } else if (actionId === 'rest') {
    await doWithBusy(async () => {
      const beforeDay = Number(props.simState?.day || 1)
      const res = await props.playerAction({ kind: 'rest_until_next_day' })
      await refreshStoryEvents()
      storyResult.value = buildDaySettlementResult(res?.state || props.simState, storyEvents.value, beforeDay)
      storyResultOpen.value = true
      showToast(res?.day_transition ? '今日剧情已结算，新的日期自动开启。' : '你回到小屋休息。', 'success')
      sceneInstance?.syncPlayerFromState?.()
    })
  } else if (actionId === 'journal') {
    await openJournal()
  }
}

async function onInteractAction(act) {
  if (act?.type === 'npc_intent_response' && act?.intent_id && act?.response_id) {
    await doWithBusy(async () => {
      const res = await props.playerAction({
        kind: 'respond_npc_intent',
        intent_id: act.intent_id,
        response_id: act.response_id
      })
      storyResult.value = {
        ...(res.intent_result || {}),
        relationship_changes: res.relationship_changes || res.intent_result?.relationship_changes || [],
        memory_written: res.memory_written || res.intent_result?.memory_written || [],
        promises: res.intent_result?.promises || {},
        tensions: res.intent_result?.tensions || {}
      }
      rememberJournalMemories(storyResult.value.memory_written)
      interactOpen.value = false
      storyResultOpen.value = true
      showToast('你的回应已经写入关系和记忆。', 'success')
      await refreshStoryEvents()
      sceneInstance?.syncPlayerFromState?.()
    })
    return
  }
  if (act?.type === 'story_event') {
    interactOpen.value = false
    openStoryEvent(act.event_id)
    return
  }
  if (act?.type === 'npc_dialogue' && act?.npc_id) {
    selectedNpcId.value = act.npc_id
    interactOpen.value = false
    dialogueOpen.value = true
    return
  }
  if (act?.type === 'scene_activity' && shouldOpenActivityPanel(act)) {
    pendingActivityAction.value = act
    interactOpen.value = false
    setActivityPanelOpen(act, true)
    showToast(activityOpenMessage(act))
    return
  }
  if (shouldOpenActivityChoicePanel(act)) {
    pendingActivityAction.value = act
    interactOpen.value = false
    activityChoiceOpen.value = true
    showToast('选择一种做法；同伴会记住你的决定。')
    return
  }
  await doWithBusy(async () => {
    if (act.type === 'set_flag') {
      await props.playerAction({ kind: 'set_flag', flag_key: act.flag_key, flag_value: act.flag_value ?? 1 })
    } else if (act.type === 'daily_tick') {
      await props.playerAction({ kind: 'daily_tick', n: Number(act.n) || 1 })
    } else if (act.type === 'compound_sleep') {
      await props.playerAction({ kind: 'compound_sleep', daily_n: Number(act.daily_n) || 1 })
    } else if (act.type === 'scene_activity') {
      await runSceneActivity(act)
    }
    showToast(act.toast || '完成', 'success')
    interactOpen.value = false
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
}

function setActivityPanelOpen(action, open) {
  const panelKind = activityPanelKind(action)
  const panelRef = activityPanelRefs[panelKind]
  if (!panelRef) return false
  panelRef.value = open
  return true
}

async function runSceneActivity(act, extra = {}) {
  const activityId = activityIdForAction(act)
  interactOpen.value = false
  const res = await props.playerAction({
    kind: 'interact_with_hub',
    poi_id: nearbyInteract.value?.id || effectiveNearbyInteract.value?.id || act?.activity?.poi_id,
    activity_id: activityId,
    activity_choice: extra.activity_choice || undefined
  })
  storyResult.value = {
    ...(res.activity_result || {}),
    ...activityResultExtras(act, extra.mini_game_result),
    relationship_changes: res.relationship_changes || res.activity_result?.relationship_changes || [],
    memory_written: res.memory_written || res.activity_result?.memory_written || [],
    promises: res.activity_result?.promises || {},
    tensions: res.activity_result?.tensions || {}
  }
  rememberJournalMemories(storyResult.value.memory_written)
  storyResultOpen.value = true
  playSfx('/assets/audio/sfx_activity.mp3')
}

async function openJournal() {
  journalOpen.value = true
  await refreshMonthPlan()
  const agents = Array.isArray(props.simState?.agents) ? props.simState.agents : []
  if (!agents.length) return
  const nextProfiles = { ...journalProfiles.value }
  const settled = await Promise.allSettled(
    agents.map(async (agent) => {
      const res = await props.fetchNpcProfile(agent.id)
      return [agent.id, res?.profile]
    })
  )
  for (const item of settled) {
    if (item.status !== 'fulfilled') continue
    const [npcId, profile] = item.value || []
    if (npcId && profile) nextProfiles[npcId] = profile
  }
  journalProfiles.value = nextProfiles
}

function rememberJournalMemories(rows) {
  const incoming = Array.isArray(rows) ? rows.filter((item) => item?.npc_id && item?.summary) : []
  if (!incoming.length) return
  const merged = [...incoming, ...recentJournalMemories.value]
  const seen = new Set()
  recentJournalMemories.value = merged.filter((item) => {
    const key = `${item.npc_id}:${item.summary}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  }).slice(0, 16)
}

// --- NPC ---
function onNpcTalk() {
  npcPanelOpen.value = false
  dialogueOpen.value = true
}

async function onNpcRelationship() {
  if (!selectedNpc.value?.id || busy.value) return
  await doWithBusy(async () => {
    const res = await props.fetchNpcProfile(selectedNpc.value.id)
    npcProfile.value = res.profile
    npcPanelOpen.value = false
    npcProfileOpen.value = true
  })
}

// --- Story Events ---
async function onStoryEventChoose(choice) {
  const event = selectedStoryEvent.value
  if (!event?.id || !choice?.id || busy.value) return
  await doWithBusy(async () => {
    const res = await props.chooseStoryEvent({ event_id: event.id, choice_id: choice.id })
    const text = res?.choice?.result_text || `${event.title} 已完成。`
    showToast(text, 'success')
    storyResult.value = { ...res, event_title: event.title }
    rememberJournalMemories(res?.memory_written)
    storyResultOpen.value = true
    storyEventOpen.value = false
    storyEvents.value = Array.isArray(res?.available_events) ? res.available_events : storyEvents.value
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
}

// --- Toolbar actions ---
async function onFlag() {
  await doWithBusy(async () => {
    await props.playerAction({ kind: 'set_flag', flag_key: 'prologue_reading_done', flag_value: 1 })
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
}

async function onStory() {
  await doWithBusy(async () => {
    await props.storyAdvance('mq01_tree_arc')
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
}

// --- Save/Load ---
async function onExportSave() {
  if (busy.value) return
  busy.value = true
  localError.value = ''
  try {
    const save = await props.exportSave()
    const blob = new Blob([JSON.stringify(save, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `30town-save-day${props.simState?.day || 1}.json`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    showToast('当前旅程已导出为本地存档。', 'success')
  } catch (e) {
    localError.value = e.message || String(e)
  } finally {
    busy.value = false
  }
}

function onImportClick() {
  saveFileEl.value?.click?.()
}

async function onImportFile(e) {
  const file = e.target?.files?.[0]
  if (!file || busy.value) return
  await doWithBusy(async () => {
    const text = await file.text()
    const save = JSON.parse(text)
    await props.importSave(save)
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
    showToast('存档已导入，旅程状态恢复完成。', 'success')
    if (saveFileEl.value) saveFileEl.value.value = ''
  })
}

async function onRefresh() {
  await doWithBusy(async () => {
    await props.refresh()
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
}


async function onTrainingComplete(payload) {
  const event = selectedStoryEvent.value
  const choice = (event?.choices || []).find((item) => item.id === payload?.choice_id) || event?.choices?.[0]
  if (!event?.id || !choice?.id || busy.value) return
  await doWithBusy(async () => {
    const res = await props.chooseStoryEvent({ event_id: event.id, choice_id: choice.id })
    const training = payload?.result || null
    const text = res?.choice?.result_text || `${event.title} 已完成。`
    showToast(training ? `训练${training.label}：${text}` : text, 'success')
    storyResult.value = {
      ...res,
      event_title: event.title,
      training_result: training
    }
    rememberJournalMemories(res?.memory_written)
    storyResultOpen.value = true
    trainingGameOpen.value = false
    storyEvents.value = Array.isArray(res?.available_events) ? res.available_events : storyEvents.value
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
}

async function onBoundaryProbeComplete(payload) {
  const event = selectedStoryEvent.value
  const choice = (event?.choices || []).find((item) => item.id === payload?.choice_id) || event?.choices?.[0]
  if (!event?.id || !choice?.id || busy.value) return
  await doWithBusy(async () => {
    const res = await props.chooseStoryEvent({ event_id: event.id, choice_id: choice.id })
    const probe = payload?.result || null
    const text = res?.choice?.result_text || `${event.title} 已完成。`
    showToast(probe ? `边界读数${probe.label}：${text}` : text, 'success')
    storyResult.value = {
      ...res,
      event_title: event.title,
      anomaly_result: probe
    }
    rememberJournalMemories(res?.memory_written)
    storyResultOpen.value = true
    boundaryProbeOpen.value = false
    storyEvents.value = Array.isArray(res?.available_events) ? res.available_events : storyEvents.value
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
}

async function onBoundaryVerdictComplete(payload) {
  const event = selectedStoryEvent.value
  const choice = (event?.choices || []).find((item) => item.id === payload?.choice_id) || event?.choices?.[0]
  if (!event?.id || !choice?.id || busy.value) return
  await doWithBusy(async () => {
    const res = await props.chooseStoryEvent({ event_id: event.id, choice_id: choice.id })
    const verdict = payload?.result || null
    const text = res?.choice?.result_text || `${event.title} 已完成。`
    showToast(verdict ? `边界判定：${verdict.label}` : text, 'success')
    storyResult.value = {
      ...res,
      event_title: event.title,
      final_result: verdict
    }
    rememberJournalMemories(res?.memory_written)
    storyResultOpen.value = true
    boundaryVerdictOpen.value = false
    storyEvents.value = Array.isArray(res?.available_events) ? res.available_events : storyEvents.value
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
}

async function onActivityChoiceChoose(choice) {
  const act = pendingActivityAction.value
  if (!act || !choice?.id || busy.value) return
  await doWithBusy(async () => {
    await runSceneActivity(act, { activity_choice: choice.id })
    activityChoiceOpen.value = false
    pendingActivityAction.value = null
    showToast('这次选择已经写入关系、记忆和后续路线。', 'success')
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
}

async function onActivityComplete(payload) {
  const act = pendingActivityAction.value
  if (!act || busy.value) return
  await doWithBusy(async () => {
    await runSceneActivity(act, {
      activity_choice: payload?.choice_id,
      mini_game_result: payload?.result || null
    })
    setActivityPanelOpen(act, false)
    pendingActivityAction.value = null
    showToast(activityCompletionMessage(act) || '活动结果已写入今天的旅程。', 'success')
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
}

// --- Keyboard shortcuts ---
function handleHotkey(e) {
  const tag = e.target?.tagName?.toLowerCase?.()
  if (tag === 'input' || tag === 'textarea' || tag === 'select') return
  if (dialogueOpen.value || npcPanelOpen.value || interactOpen.value || storyEventOpen.value || activityChoiceOpen.value || storyResultOpen.value || npcProfileOpen.value || journalOpen.value || trainingGameOpen.value || boundaryProbeOpen.value || boundaryVerdictOpen.value || readingGameOpen.value || mealChoiceOpen.value || boundaryPatrolOpen.value) return
  const key = String(e.key || '').toLowerCase()
  if (props.devMode && key === 'v' && (e.ctrlKey || e.metaKey || e.shiftKey)) {
    e.preventDefault()
    sceneInstance?.toggleNavigationOverlay?.()
    showToast('已切换可走层调试视图。绿色可走，蓝色水域，红色阻挡。')
    return
  }
  const moveKeys = {
    w: [0, -1],
    arrowup: [0, -1],
    s: [0, 1],
    arrowdown: [0, 1],
    a: [-1, 0],
    arrowleft: [-1, 0],
    d: [1, 0],
    arrowright: [1, 0]
  }
  if (moveKeys[key] && sceneInstance?.tryKeyboardStep) {
    e.preventDefault()
    e.__uwHandled = true
    const [dx, dy] = moveKeys[key]
    sceneInstance.tryKeyboardStep(dx, dy)
    return
  }
  if (key === '1') { e.preventDefault(); onHotbarAction('talk') }
  else if (key === '2') { e.preventDefault(); onHotbarAction('read') }
  else if (key === '3') { e.preventDefault(); onHotbarAction('train') }
  else if (key === '4') { e.preventDefault(); onHotbarAction('rest') }
  else if (key === '5') { e.preventDefault(); onHotbarAction('journal') }
  else if (key === 'r') { e.preventDefault(); onRefresh() }
}

// --- Helpers ---
async function doWithBusy(fn) {
  busy.value = true
  localError.value = ''
  try {
    await fn()
  } catch (e) {
    const msg = e.message || String(e)
    if (msg.includes('wrong_time_band')) {
      localError.value = '现在时段不适合这个行动。先推进时间，或去做当前时段的场景活动。'
    } else if (msg.includes('wrong_day_range')) {
      localError.value = '这个行动不在当前剧情日期开放。先完成今天的关键目标并推进剧情。'
    } else if (msg.includes('wrong_scene')) {
      localError.value = '你还没有进入对应场景。先走到地图上的地点范围。'
    } else if (msg.includes('requirements_not_met')) {
      localError.value = '这个行动还有前置条件。先完成当前线索，或与对应 NPC 互动。'
    } else if (msg.includes('day_end_gate_incomplete')) {
      localError.value = '今天还有关键剧情没有完成。先完成目标，再回到炉火处结算。'
    } else if (msg.includes('already_done_today')) {
      localError.value = '这个行动今天已经完成。可以继续完成当天剧情。'
    } else if (msg.includes('already_done')) {
      localError.value = '这个行动已经完成。去探索新的地点或推进章节事件吧。'
    } else {
      localError.value = msg
    }
  } finally {
    busy.value = false
  }
}

function buildDailySummaryResult(res, nextEvents = []) {
  const events = Array.isArray(res?.events) ? res.events : []
  const state = res?.state || props.simState || {}
  const timeLabel = getTimeBandLabel(state.time_band || props.simState?.time_band || '')
  const activeNames = events
    .map((event) => event.actor_name || getAgentLabel(event.actor))
    .filter(Boolean)
  const actorText = [...new Set(activeNames)].slice(0, 3).join('、') || '村子'
  return {
    kind: 'daily_summary',
    day: state.day,
    time_band: timeLabel,
    events,
    next_events: nextEvents,
    result_text: `${actorText}在这一刻继续行动。你推进的不只是时间，也是在让 NPC 的体力、饥饿、目标和日常选择继续变化。`
  }
}

function buildDaySettlementResult(state, nextEvents = [], beforeDay = 1) {
  const currentDay = Number(state?.day || beforeDay + 1)
  const nextTitles = nextEvents.map((event) => event.title).filter(Boolean)
  const nextText = nextTitles.length
    ? `新的线索已经浮现：${nextTitles.slice(0, 2).join('、')}。`
    : '暂时没有新的章节事件，但 NPC 的日常仍在继续。'
  return {
    kind: 'day_settlement',
    day: currentDay,
    time_band: getTimeBandLabel(state?.time_band || 'morning'),
    next_events: nextEvents,
    result_text: `Day ${beforeDay} 结束了。${nextText} 明天的对话会带着今天留下的关系和记忆。`
  }
}

// --- Lifecycle ---
onMounted(async () => {
  window.addEventListener('keydown', handleHotkey)
  await nextTick()
  if (props.devMode) {
    try {
      const r = await props.fetchRegions()
      regionsJson.value = JSON.stringify(r, null, 2)
    } catch { regionsJson.value = '(regions 加载失败)' }
  }
  await loadSceneActivities()
  await loadWorldMap(activeMapId.value)
  await refreshStoryEvents()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleHotkey)
  clearToastTimer()
  clearTimeout(syncTimer)
  clearTimeout(storyRefreshTimer)
  sceneInstance = null
})

const storyRefreshKey = computed(() => JSON.stringify({
  day: props.simState?.day,
  time_band: props.simState?.time_band,
  story_node_id: props.simState?.story_node_id,
  flags: props.simState?.flags || {},
  completed_event_ids: props.simState?.completed_event_ids || [],
  chapter_ending_id: props.simState?.chapter_ending_id || ''
}))

// Sync visual state without re-fetching on every agent stat change.
// Only watch player position and agent list length for actual sync needs.
let syncTimer = null
watch(storyResultOpen, (open) => {
  if (open) interactOpen.value = false
})

watch(
  () => [props.simState?.player?.tile_x, props.simState?.player?.tile_y, props.simState?.agents?.length],
  () => {
    clearTimeout(syncTimer)
    syncTimer = setTimeout(() => {
      sceneInstance?.syncPlayerFromState?.()
      if (npcPanelOpen.value && selectedNpcId.value && !selectedNpc.value) {
        npcPanelOpen.value = false
      }
    }, 80)
  }
)

let storyRefreshTimer = null
watch(storyRefreshKey, () => {
  clearTimeout(storyRefreshTimer)
  storyRefreshTimer = setTimeout(() => {
    refreshStoryEvents()
  }, 180)
})

watch(activeMapId, async (mapId, oldMapId) => {
  if (!mapId || mapId === oldMapId) return
  await loadWorldMap(mapId)
  await nextTick()
  sceneInstance?.syncPlayerFromState?.()
})
</script>

<style scoped>
.field-slice {
  width: 100%;
  max-width: none;
  height: 100vh;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  position: relative;
  overflow: hidden;
}

.playfield-shell {
  position: relative;
  height: 100%;
  min-height: 100vh;
  border-radius: 0;
  overflow: hidden;
  border: 0;
  box-shadow: none;
  background: var(--field-deep);
  will-change: transform;
}

.opening-brief {
  position: absolute;
  z-index: 44;
  left: 0.85rem;
  bottom: 10.45rem;
  width: min(390px, calc(100% - 2rem));
  padding: 0.82rem 0.92rem;
  border-radius: 8px;
  color: #fff7df;
  background:
    linear-gradient(135deg, rgba(45, 32, 24, 0.9), rgba(25, 42, 34, 0.78)),
    linear-gradient(180deg, rgba(12, 20, 26, 0.18), rgba(12, 20, 26, 0.72)),
    url('/assets/runtime/keyart/village-desktop.png') center / cover,
    radial-gradient(circle at 18% 0%, rgba(246, 211, 110, 0.2), transparent 44%);
  border: 1px solid rgba(255, 239, 198, 0.32);
  box-shadow: 0 18px 42px rgba(25, 18, 10, 0.36), 0 0 24px rgba(246, 211, 110, 0.08);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  pointer-events: auto;
}

.brief-kicker {
  color: #ffe2a3;
  font-size: 0.66rem;
  font-weight: 900;
}

.opening-brief h3 {
  margin: 0.18rem 0 0.32rem;
  color: #fff7df;
  font-size: 1.02rem;
  line-height: 1.2;
}

.opening-brief p {
  margin: 0;
  color: #e9dcc2;
  font-size: 0.78rem;
  line-height: 1.55;
}

.brief-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.7rem;
}

.brief-actions button {
  min-height: 2.1rem;
  padding: 0 0.8rem;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 900;
  color: #332414;
  background: linear-gradient(180deg, #ffe6a6, #d99545);
  border: 1px solid rgba(255, 247, 214, 0.74);
  box-shadow: 0 0 18px rgba(246, 211, 110, 0.18);
}

.brief-actions .brief-ghost {
  color: #fff7df;
  background: rgba(44, 38, 26, 0.72);
  border-color: rgba(255, 239, 198, 0.24);
  box-shadow: none;
}

.field-slice :deep(.field-header) {
  position: absolute;
  z-index: 50;
  top: 0.7rem;
  left: 0.8rem;
  right: 12rem;
  margin: 0;
  padding: 0.5rem 0.6rem;
  border-radius: 8px;
  background: rgba(47, 38, 24, 0.72);
  border: 1px solid rgba(255, 239, 198, 0.16);
  box-shadow: 0 8px 20px rgba(25, 18, 10, 0.18);
}

.field-slice :deep(.field-title h2) {
  font-size: 1rem;
}

.field-slice :deep(.field-kicker) {
  font-size: 0.56rem;
}

.field-slice :deep(.header-actions .tb) {
  padding: 0.3rem 0.5rem;
  font-size: 0.68rem;
}

.field-map-loading {
  aspect-ratio: 1280 / 720;
  display: grid;
  place-items: center;
  border-radius: 12px;
  color: var(--muted);
  background:
    linear-gradient(180deg, rgba(19, 31, 44, 0.96), rgba(8, 14, 22, 0.98));
  border: 1px solid var(--field-frame);
  font-size: 0.86rem;
}

.field-err {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.45rem 0.65rem;
  margin-bottom: 0.5rem;
  border-radius: 10px;
  background: rgba(127, 29, 29, 0.35);
  border: 1px solid rgba(248, 113, 113, 0.35);
  color: #fecaca;
  font-size: 0.82rem;
}

.err-close {
  background: transparent;
  border: none;
  color: inherit;
  opacity: 0.7;
  cursor: pointer;
  font-size: 1rem;
  padding: 0;
  line-height: 1;
  box-shadow: none;
}

.err-close:hover { opacity: 1; background: transparent; border-color: transparent; }

.chat-strip {
  display: none;
  position: absolute;
  z-index: 4;
  left: 0.75rem;
  bottom: 6.2rem;
  width: min(470px, calc(100% - 1.5rem));
  padding: 0.45rem 0.62rem;
  border-radius: 9px;
  color: #cbd5e1;
  background: rgba(3, 7, 18, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.18);
  font-size: 0.74rem;
  line-height: 1.45;
  pointer-events: none;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.chat-strip span {
  color: var(--sao-gold);
  font-weight: 800;
  margin-right: 0.38rem;
}

.field-hint {
  font-size: 0.76rem;
  color: var(--ok);
  margin: 0.55rem 0 0;
  padding: 0.45rem 0.55rem;
  border-radius: 8px;
  background: rgba(78, 204, 163, 0.06);
  border: 1px solid rgba(78, 204, 163, 0.16);
}

.debug-drawer {
  display: none;
  position: relative;
  margin-top: 0.55rem;
  padding: 0.55rem 0.65rem;
  border-radius: 10px;
  background: rgba(7, 12, 24, 0.55);
  border: 1px solid var(--sao-border-dim);
  color: var(--muted);
  font-size: 0.78rem;
}

.debug-drawer summary {
  cursor: pointer;
  color: var(--sao-cyan);
  font-weight: 700;
  list-style: none;
}

.debug-drawer summary::-webkit-details-marker { display: none; }

.field-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem 1rem;
  margin-top: 0.55rem;
  padding: 0.6rem 0.75rem;
  border-radius: 10px;
  background: linear-gradient(160deg, rgba(94, 207, 255, 0.06), rgba(15, 23, 42, 0.75));
  border: 1px solid var(--sao-border-dim);
}

.tb-group {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.3rem;
}

.tb-label {
  font-size: 0.6rem;
  letter-spacing: 0.08em;
  color: var(--muted);
  width: 100%;
}

.tb {
  font-size: 0.74rem;
  padding: 0.38rem 0.65rem;
  border-radius: 9px;
  border: 1px solid var(--sao-border-dim);
  background: rgba(15, 23, 42, 0.55);
  color: var(--ink);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
}

.tb:hover:not(:disabled) {
  background: rgba(94, 207, 255, 0.1);
  border-color: var(--sao-border);
  box-shadow: var(--sao-glow);
}

.tb:disabled { opacity: 0.45; cursor: not-allowed; }
.tb-ghost { background: rgba(12, 20, 36, 0.5); }
.tb-accent { background: linear-gradient(180deg, #6366f1, #4f46e5); border-color: rgba(165, 180, 252, 0.45); color: #fff; font-weight: 600; }
.tb-primary { background: linear-gradient(180deg, var(--accent), #b8324a); border-color: rgba(251, 113, 133, 0.45); color: #fff; font-weight: 600; }

.save-file { display: none; }

.regions-details {
  display: none;
  margin-top: 0.65rem;
  font-size: 0.78rem;
  color: var(--muted);
}

.regions-details summary { cursor: pointer; color: var(--sao-cyan); }

.regions-pre {
  margin: 0.45rem 0 0;
  font-size: 0.62rem;
  max-height: 100px;
  overflow: auto;
  padding: 0.45rem;
  background: rgba(7, 10, 18, 0.65);
  border-radius: 8px;
  border: 1px solid var(--sao-border-dim);
}

/* Error slide transition */
.err-slide-enter-active,
.err-slide-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.err-slide-enter-from,
.err-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.brief-fade-enter-active,
.brief-fade-leave-active {
  transition: opacity 0.28s ease, transform 0.28s ease;
}

.brief-fade-enter-from,
.brief-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (max-width: 900px) {
  .field-slice { padding: 0; }
  .field-slice :deep(.field-header) {
    top: auto;
    left: auto;
    right: 0.55rem;
    bottom: 5.35rem;
    width: auto;
    padding: 0.45rem;
    background: rgba(47, 38, 24, 0.58);
  }
  .field-slice :deep(.field-title) { display: none; }
  .field-slice :deep(.header-actions) { gap: 0.3rem; }
  .opening-brief {
    top: 5.9rem;
    bottom: auto;
    left: 0.55rem;
    right: auto;
    width: min(235px, calc(100% - 1.1rem));
    padding: 0.68rem 0.72rem;
  }
  .opening-brief h3 { font-size: 0.94rem; }
  .opening-brief p { font-size: 0.74rem; }
  .brief-actions button { flex: 1; padding: 0 0.45rem; }
  .chat-strip { display: none; }
}
</style>
