<template>
  <div class="field-slice">
    <!-- Top header bar -->
    <FieldHeader
      :busy="busy"
      @export-save="onExportSave"
      @import-save="onImportClick"
      @import-file="onImportFile"
      @refresh="onRefresh"
      @daily="onDaily"
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
        :nearby-interact="nearbyInteract"
        @tile-click="onTileClick"
        @npc-click="onNpcClick"
        @interact-click="interactOpen = true"
        @event-click="openStoryEvent"
        @ready="onSceneReady"
      />
      <div v-else class="field-map-loading">正在同步村庄地图…</div>

      <!-- Right side quest tracker -->
      <QuestTracker
        :sim-state="simState"
        :story-events="storyEvents"
        :quest-guide="questGuide"
        :nearby-npc-label="nearbyNpcLabel"
        :nearby-interact-title="nearbyInteractTitle"
        :busy="busy"
        @open-event="openStoryEvent"
      />

      <!-- Bottom chat strip -->
      <div class="chat-strip">
        <span>系统</span>
        点击地图移动，靠近 NPC 或互动点后可触发对话与事件。
      </div>

      <!-- Bottom hotbar -->
      <Hotbar :busy="busy" :has-events="!!storyEvents.length" @action="onHotbarAction" />
    </div>

    <!-- Debug drawer (collapsed by default) -->
    <details class="debug-drawer">
      <summary>开发调试与操作说明</summary>
      <div class="field-toolbar">
        <div class="tb-group">
          <span class="tb-label">剧情闸</span>
          <button type="button" class="tb tb-ghost" :disabled="busy" @click="onFlag">标记「读完书」</button>
          <button type="button" class="tb tb-accent" :disabled="busy" @click="onStory">推进 → mq01</button>
        </div>
      </div>
      <p class="field-hint">
        左键点按目标格移动；右键或中键拖动大地图；小地图拖拽或点按可移动视野；滚轮缩放。走近青色互动点时，点击地图上的「对话/互动」按钮打开面板。
      </p>
    </details>

    <!-- Regions JSON (dev only) -->
    <details v-if="regionsJson" class="regions-details">
      <summary>区域表 JSON</summary>
      <pre class="regions-pre">{{ regionsJson }}</pre>
    </details>

    <!-- Modals -->
    <FieldInteractPanel
      v-model="interactOpen"
      :nearby-interact="nearbyInteract"
      :visible-interact-actions="visibleInteractActions"
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
      v-model="storyEventOpen"
      :event="selectedStoryEvent"
      :busy="busy"
      @choose="onStoryEventChoose"
    />

    <StoryResultPanel
      v-model="storyResultOpen"
      :result="storyResult"
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
import Toast from './Toast.vue'
import { getAgentLabel, getQuestGuide, getSceneLabel, getTimeBandLabel } from '../field/gameContentConfig.js'
import { findNearbyInteractPoi } from '../field/interactPoi.js'
import { DEFAULT_MAP_ID } from '../field/sceneRegistry.js'

const props = defineProps({
  simState: { type: Object, required: true },
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
const selectedStoryEventId = ref('')
const selectedNpcId = ref('')
const toastMessage = ref('')
const toastType = ref('info')
const toastOpen = ref(false)

// Modal states
const interactOpen = ref(false)
const npcPanelOpen = ref(false)
const dialogueOpen = ref(false)
const storyEventOpen = ref(false)
const storyResultOpen = ref(false)
const npcProfileOpen = ref(false)
const storyResult = ref(null)
const npcProfile = ref(null)

let toastTimer = null
let sceneInstance = null

// --- Computed ---
const sceneLabel = computed(() => getSceneLabel(props.simState?.player?.scene_id || props.simState?.scene_id || ''))
const timeBandLabel = computed(() => getTimeBandLabel(props.simState?.time_band || 'morning'))
const activeMapId = computed(() => props.simState?.player?.map_id || props.simState?.map_id || DEFAULT_MAP_ID)

const nearbyInteract = computed(() =>
  findNearbyInteractPoi(worldMapRef.value, props.simState?.player)
)

const visibleInteractActions = computed(() => {
  const poi = nearbyInteract.value
  const nid = props.simState?.story_node_id
  if (!poi?.actions) return []
  return poi.actions
    .filter((a) => !a.requires_story || a.requires_story === nid)
    .map(enrichInteractAction)
})

const selectedNpc = computed(() =>
  (props.simState?.agents || []).find((a) => a.id === selectedNpcId.value) || null
)

const selectedStoryEvent = computed(() =>
  storyEvents.value.find((e) => e.id === selectedStoryEventId.value) || storyEvents.value[0] || null
)

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

const nearbyInteractTitle = computed(() => nearbyInteract.value?.title || '暂无地点')

const questGuide = computed(() => {
  if (storyEvents.value.length) {
    return '地图上出现了金色章节事件标记。点击事件标题或地图上的「！」推进第一章。'
  }
  return getQuestGuide(props.simState)
})

// --- Toast ---
function showToast(msg, type = 'info') {
  toastMessage.value = msg
  toastType.value = type
  clearTimeout(toastTimer)
  toastOpen.value = false
  nextTick(() => {
    toastOpen.value = true
  })
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
}

async function loadWorldMap(mapId = DEFAULT_MAP_ID) {
  worldMapRef.value = null
  try {
    worldMapRef.value = await props.fetchWorldMap(mapId)
    localError.value = ''
  } catch {
    localError.value = `地图加载失败：${mapId}`
    worldMapRef.value = { id: mapId, rows: [], width: 0, height: 0, tile_size: 32 }
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

  const requiredFlags = activity.requirements?.required_flags || {}
  const flags = props.simState?.flags || {}
  for (const [key, value] of Object.entries(requiredFlags)) {
    if (Number(flags[key] || 0) < Number(value || 0)) {
      return { ok: false, reason: '需要先完成前置线索' }
    }
  }
  return { ok: true, reason: '' }
}

function enrichInteractAction(action) {
  if (action?.type !== 'scene_activity') return action
  const activity = sceneActivityIndex.value[action.activity_id || action.id]
  if (!activity) return action
  const availability = activityAvailability(activity)
  const meta = []
  const timeCost = Number(activity.time_cost || 0)
  meta.push(timeCost > 0 ? `耗时 ${timeCost} 刻` : '不消耗时段')
  if (Array.isArray(activity.time_bands) && activity.time_bands.length) {
    meta.push(activity.time_bands.map(getTimeBandLabel).join(' / '))
  }
  if (!availability.ok && availability.reason) meta.push(availability.reason)
  return {
    ...action,
    label: activity.label || action.label,
    description: activity.description || action.description || '',
    meta: meta.join(' · '),
    blockedReason: availability.ok ? '' : availability.reason,
    activity
  }
}

function openStoryEvent(eventId) {
  selectedStoryEventId.value = eventId
  storyEventOpen.value = true
}

// --- Player Actions ---
async function onTileClick({ tile_x, tile_y }) {
  if (busy.value) return
  busy.value = true
  localError.value = ''
  try {
    const j = await props.playerAction(
      { kind: 'move_world', tile_x, tile_y },
      { deferRefresh: true }
    )
    const path = j.path || []
    if (sceneInstance?.playWalkPath) {
      await sceneInstance.playWalkPath(path)
    }
    mapRef.value?.triggerCameraShake?.()
    await props.refresh()
    if (sceneInstance?.syncPlayerFromState) sceneInstance.syncPlayerFromState()
  } catch (e) {
    const msg = e.message || String(e)
    if (msg.includes('unreachable_or_blocked')) {
      showToast('前方是尚未开放或无法通行的边界。先在村内完成当前目标。')
    } else {
      localError.value = msg
    }
  } finally {
    sceneInstance?.resumeCameraFollow?.()
    busy.value = false
  }
}

function onNpcClick(agentId) {
  selectedNpcId.value = agentId
  npcPanelOpen.value = true
}

async function onHotbarAction(actionId) {
  if (actionId === 'talk') {
    const npc = nearbyNpcs.value[0]
    if (!npc) { showToast('先靠近地图上的 NPC，再按对话。'); return }
    selectedNpcId.value = npc.id
    dialogueOpen.value = true
  } else if (actionId === 'read') {
    await doWithBusy(async () => {
      await props.playerAction({ kind: 'set_flag', flag_key: 'prologue_reading_done', flag_value: 1 })
      await refreshStoryEvents()
      showToast('已读完书页：规则与边界的线索被记下。', 'success')
    })
  } else if (actionId === 'train') {
    await doWithBusy(async () => {
      await props.dailyTick(1, 'heuristic')
      await refreshStoryEvents()
      showToast('训练推进了一个时刻。')
      sceneInstance?.syncPlayerFromState?.()
    })
  } else if (actionId === 'rest') {
    await doWithBusy(async () => {
      await props.playerAction({ kind: 'rest_until_next_day' })
      await refreshStoryEvents()
      showToast('你回到小屋休息。新的一天开始了。', 'success')
      sceneInstance?.syncPlayerFromState?.()
    })
  } else if (actionId === 'event') {
    const event = storyEvents.value[0]
    if (!event) { showToast('当前还没有可触发的章节事件。'); return }
    openStoryEvent(event.id)
  }
}

async function onInteractAction(act) {
  await doWithBusy(async () => {
    if (act.type === 'set_flag') {
      await props.playerAction({ kind: 'set_flag', flag_key: act.flag_key, flag_value: act.flag_value ?? 1 })
    } else if (act.type === 'daily_tick') {
      await props.dailyTick(Number(act.n) || 1, 'heuristic')
    } else if (act.type === 'compound_sleep') {
      await props.playerAction({ kind: 'set_location', location: 'home' })
      await props.dailyTick(Number(act.daily_n) || 1, 'heuristic')
    } else if (act.type === 'scene_activity') {
      const res = await props.playerAction({ kind: 'scene_activity', activity_id: act.activity_id || act.id })
      storyResult.value = {
        ...(res.activity_result || {}),
        relationship_changes: res.relationship_changes || res.activity_result?.relationship_changes || [],
        memory_written: res.memory_written || res.activity_result?.memory_written || []
      }
      storyResultOpen.value = true
    }
    showToast(act.toast || '完成', 'success')
    interactOpen.value = false
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
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

async function onDaily() {
  await doWithBusy(async () => {
    await props.dailyTick(1, 'heuristic')
    await refreshStoryEvents()
    sceneInstance?.syncPlayerFromState?.()
  })
}

// --- Keyboard shortcuts ---
function handleHotkey(e) {
  const tag = e.target?.tagName?.toLowerCase?.()
  if (tag === 'input' || tag === 'textarea' || tag === 'select') return
  if (dialogueOpen.value || npcPanelOpen.value || interactOpen.value) return
  const key = String(e.key || '').toLowerCase()
  if (key === '1') { e.preventDefault(); onHotbarAction('talk') }
  else if (key === '2') { e.preventDefault(); onHotbarAction('read') }
  else if (key === '3') { e.preventDefault(); onHotbarAction('train') }
  else if (key === '4') { e.preventDefault(); onHotbarAction('rest') }
  else if (key === '5') { e.preventDefault(); onHotbarAction('event') }
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
    } else if (msg.includes('wrong_scene')) {
      localError.value = '你还没有进入对应场景。先走到地图上的地点范围。'
    } else if (msg.includes('requirements_not_met')) {
      localError.value = '这个行动还有前置条件。先完成当前线索，或与对应 NPC 互动。'
    } else {
      localError.value = msg
    }
  } finally {
    busy.value = false
  }
}

// --- Lifecycle ---
onMounted(async () => {
  window.addEventListener('keydown', handleHotkey)
  await nextTick()
  try {
    const r = await props.fetchRegions()
    regionsJson.value = JSON.stringify(r, null, 2)
  } catch { regionsJson.value = '(regions 加载失败)' }
  await loadSceneActivities()
  await loadWorldMap(activeMapId.value)
  await refreshStoryEvents()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleHotkey)
  clearTimeout(toastTimer)
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
  max-width: 1440px;
  margin: 0 auto 1rem;
  padding: 0.75rem;
  position: relative;
}

.playfield-shell {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--field-frame);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.42), 0 18px 54px rgba(0, 0, 0, 0.5), 0 0 30px rgba(94, 207, 255, 0.08);
  background: var(--field-deep);
  will-change: transform;
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
  position: absolute;
  z-index: 4;
  left: 0.75rem;
  bottom: 5rem;
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

@media (max-width: 900px) {
  .field-slice { padding: 0.55rem; }
  .chat-strip { display: none; }
}
</style>
