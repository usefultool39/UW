<template>
  <div class="field-slice">
    <header class="field-header">
      <div class="field-title">
        <p class="field-kicker">{{ GAME_CHAPTER_INFO.kicker }}</p>
        <h2>{{ GAME_CHAPTER_INFO.title }}</h2>
      </div>
      <div class="header-actions">
        <button type="button" class="tb tb-ghost" :disabled="busy" @click="onExportSave">导出存档</button>
        <button type="button" class="tb tb-ghost" :disabled="busy" @click="onImportClick">导入存档</button>
        <button type="button" class="tb tb-ghost" :disabled="busy" @click="onRefresh">刷新</button>
        <button type="button" class="tb tb-primary" :disabled="busy" @click="onDaily">时间推进</button>
        <input
          ref="saveFileEl"
          class="save-file"
          type="file"
          accept="application/json,.json"
          @change="onImportFile"
        />
      </div>
    </header>

    <div v-if="localError" class="field-err">{{ localError }}</div>

    <div class="playfield-shell">
      <div class="mmo-player-frame">
        <div class="avatar-disc">你</div>
        <div class="player-vitals">
          <div class="vital-name">外来者 · Lv.1</div>
          <div class="bar hp"><span style="width: 92%"></span></div>
          <div class="bar mp"><span style="width: 68%"></span></div>
        </div>
      </div>

      <div class="mmo-scene-frame">
        <strong>{{ sceneLabel }}</strong>
        <span>Day {{ simState?.day ?? 1 }} · {{ timeBandLabel }}</span>
      </div>

      <aside class="quest-tracker" role="status">
        <div class="quest-rail-title">当前目标</div>
        <p class="quest-rail-body">{{ questGuide }}</p>
        <div v-if="storyEvents.length" class="event-strip">
          <button
            v-for="event in storyEvents"
            :key="event.id"
            type="button"
            :disabled="busy"
            @click="openStoryEvent(event.id)"
          >
            {{ event.title }}
          </button>
        </div>
        <div class="tracker-meta">
          <span>附近：{{ nearbyNpcLabel }}</span>
          <span>{{ simState?.story_node_id || 'mq00_tutorial' }}</span>
        </div>
      </aside>

      <div class="chat-strip">
        <span>系统</span>
        点击地图移动，靠近 NPC 或互动点后可触发对话与事件。
      </div>

      <nav class="action-hotbar" aria-label="快捷操作">
        <button type="button" :disabled="busy" @click="onHotbarTalk"><kbd>1</kbd><span>对话</span></button>
        <button type="button" :disabled="busy" @click="onHotbarRead"><kbd>2</kbd><span>读书</span></button>
        <button type="button" :disabled="busy" @click="onHotbarTrain"><kbd>3</kbd><span>训练</span></button>
        <button type="button" :disabled="busy" @click="onHotbarRest"><kbd>4</kbd><span>休息</span></button>
        <button type="button" :disabled="busy || !storyEvents.length" @click="onHotbarEvent"><kbd>5</kbd><span>事件</span></button>
      </nav>

      <div ref="hostEl" class="phaser-host" />
    </div>

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

    <div v-if="toastMessage" class="field-toast">{{ toastMessage }}</div>

    <details v-if="regionsJson" class="regions-details">
      <summary>区域表 JSON</summary>
      <pre class="regions-pre">{{ regionsJson }}</pre>
    </details>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import FieldInteractPanel from './FieldInteractPanel.vue'
import NpcInteractPanel from './NpcInteractPanel.vue'
import DialoguePanel from './DialoguePanel.vue'
import StoryEventPanel from './StoryEventPanel.vue'
import StoryResultPanel from './StoryResultPanel.vue'
import NpcProfilePanel from './NpcProfilePanel.vue'
import {
  GAME_CHAPTER_INFO,
  getAgentLabel,
  getQuestGuide,
  getSceneLabel,
  getTimeBandLabel
} from '../field/gameContentConfig.js'
import { findNearbyInteractPoi } from '../field/interactPoi.js'

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
  refresh: { type: Function, required: true }
})

const hostEl = ref(null)
const saveFileEl = ref(null)
const busy = ref(false)
const localError = ref('')
const regionsJson = ref('')
const worldMapRef = ref(null)
const interactOpen = ref(false)
const npcPanelOpen = ref(false)
const dialogueOpen = ref(false)
const storyEventOpen = ref(false)
const storyEvents = ref([])
const selectedStoryEventId = ref('')
const storyResultOpen = ref(false)
const storyResult = ref(null)
const npcProfileOpen = ref(false)
const npcProfile = ref(null)
const selectedNpcId = ref('')
const toastMessage = ref('')
let toastTimer = null

let game = null
let sceneInstance = null

function showToast(msg) {
  toastMessage.value = msg
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
    toastTimer = null
  }, 3400)
}

const nearbyInteract = computed(() =>
  findNearbyInteractPoi(worldMapRef.value, props.simState?.player)
)

const visibleInteractActions = computed(() => {
  const poi = nearbyInteract.value
  const nid = props.simState?.story_node_id
  if (!poi?.actions) return []
  return poi.actions.filter((a) => !a.requires_story || a.requires_story === nid)
})

watch(nearbyInteract, (v) => {
  if (!v) interactOpen.value = false
})

const timeBandLabel = computed(() => {
  const band = props.simState?.time_band || 'morning'
  return getTimeBandLabel(band)
})

const sceneLabel = computed(() => {
  const scene = props.simState?.player?.scene_id || props.simState?.scene_id || ''
  return getSceneLabel(scene)
})

const agentsWithCoords = computed(() =>
  (props.simState?.agents || []).filter(
    (a) => Number.isFinite(Number(a?.tile_x)) && Number.isFinite(Number(a?.tile_y))
  )
)

const selectedNpc = computed(() => {
  const id = selectedNpcId.value
  return (props.simState?.agents || []).find((a) => a.id === id) || null
})

const selectedStoryEvent = computed(() => {
  const id = selectedStoryEventId.value
  return storyEvents.value.find((event) => event.id === id) || storyEvents.value[0] || null
})

const nearbyNpcs = computed(() => {
  const p = props.simState?.player
  if (!p) return []
  const px = Number(p.tile_x)
  const py = Number(p.tile_y)
  if (!Number.isFinite(px) || !Number.isFinite(py)) return []
  return agentsWithCoords.value.filter((a) => {
    const dx = Number(a.tile_x) - px
    const dy = Number(a.tile_y) - py
    return Math.sqrt(dx * dx + dy * dy) <= 3
  })
})

const nearbyNpcLabel = computed(() => {
  if (!nearbyNpcs.value.length) return '暂无'
  return nearbyNpcs.value.map((a) => getAgentLabel(a.id)).join('、')
})

const questGuide = computed(() => {
  if (storyEvents.value.length) {
    return '地图上出现了金色章节事件标记。点击事件标题或地图上的「！」推进第一章。'
  }
  return getQuestGuide(props.simState)
})

async function refreshStoryEvents() {
  try {
    const res = await props.fetchAvailableStoryEvents()
    storyEvents.value = Array.isArray(res?.events) ? res.events : []
    if (storyEventOpen.value && selectedStoryEventId.value) {
      const stillThere = storyEvents.value.some((event) => event.id === selectedStoryEventId.value)
      if (!stillThere) storyEventOpen.value = false
    }
    sceneInstance?.rebuildPois?.()
  } catch {
    storyEvents.value = []
  }
}

function openStoryEvent(eventId) {
  selectedStoryEventId.value = eventId
  storyEventOpen.value = true
}

function syncPlayerFromState() {
  if (!sceneInstance || !props.simState?.player) return
  const p = props.simState.player
  const ts = sceneInstance._tileSize
  sceneInstance.playerRoot.setPosition((p.tile_x + 0.5) * ts, (p.tile_y + 0.5) * ts)
  const hud = sceneInstance._hudText
  if (hud) {
    hud.setText(`${sceneLabel.value} · 第 ${props.simState.day} 天 · ${timeBandLabel.value}`)
  }
  sceneInstance?.syncNpcs?.()
}

async function bootPhaser() {
  if (!hostEl.value || !worldMapRef.value) return
  const Phaser = (await import('phaser')).default
  const { createWorldFieldSceneClass } = await import('../field/createWorldFieldScene.js')

  const getMap = () => worldMapRef.value

  const onTilePick = async (tx, ty) => {
    if (busy.value) return
    busy.value = true
    localError.value = ''
    try {
      const j = await props.playerAction(
        { kind: 'move_world', tile_x: tx, tile_y: ty },
        { deferRefresh: true }
      )
      const path = j.path || []
      if (sceneInstance?.playWalkPath) {
        await sceneInstance.playWalkPath(path)
      }
      await props.refresh()
      syncPlayerFromState()
    } catch (e) {
      const msg = e.message || String(e)
      if (msg.includes('unreachable_or_blocked')) {
        showToast('前方是尚未开放或无法通行的边界。先在村内完成当前目标。')
        localError.value = ''
      } else {
        localError.value = msg
      }
    } finally {
      sceneInstance?.resumeCameraFollow?.()
      busy.value = false
    }
  }

  const SceneClass = createWorldFieldSceneClass(Phaser, {
    getMap,
    onTilePick,
    getSimState: () => props.simState,
    assignSceneInstance: (sc) => {
      sceneInstance = sc
    },
    syncPlayerFromState,
    openInteractPanel: () => {
      interactOpen.value = true
    },
    openNpcPanel: (agentId) => {
      selectedNpcId.value = agentId
      npcPanelOpen.value = true
    },
    isBusy: () => busy.value,
    getNearbyInteractPoi: () => findNearbyInteractPoi(worldMapRef.value, props.simState?.player),
    getStoryEvents: () => storyEvents.value,
    openStoryEventPanel: openStoryEvent
  })
  game = new Phaser.Game({
    type: Phaser.AUTO,
    width: 1280,
    height: 720,
    parent: hostEl.value,
    transparent: true,
    scene: SceneClass,
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH }
  })
}

onMounted(async () => {
  window.addEventListener('keydown', handleHotkey)
  await nextTick()
  try {
    const r = await props.fetchRegions()
    regionsJson.value = JSON.stringify(r, null, 2)
  } catch (e) {
    regionsJson.value = '(regions 加载失败)'
  }
  try {
    worldMapRef.value = await props.fetchWorldMap()
  } catch (e) {
    localError.value = '地图加载失败: ' + (e.message || e)
    worldMapRef.value = { rows: [], width: 0, height: 0, tile_size: 32 }
  }
  await refreshStoryEvents()
  await nextTick()
  await bootPhaser()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleHotkey)
  if (toastTimer) {
    clearTimeout(toastTimer)
    toastTimer = null
  }
  sceneInstance = null
  if (game) {
    game.destroy(true)
    game = null
  }
})

watch(
  () => props.simState,
  () => {
    syncPlayerFromState()
    sceneInstance?.rebuildPois?.()
    sceneInstance?.syncNpcs?.()
    refreshStoryEvents()
    if (npcPanelOpen.value && selectedNpcId.value && !selectedNpc.value) {
      npcPanelOpen.value = false
    }
  },
  { deep: true }
)

function onNpcTalk() {
  npcPanelOpen.value = false
  dialogueOpen.value = true
}

async function onNpcRelationship() {
  if (!selectedNpc.value?.id || busy.value) return
  busy.value = true
  localError.value = ''
  try {
    const res = await props.fetchNpcProfile(selectedNpc.value.id)
    npcProfile.value = res.profile
    npcPanelOpen.value = false
    npcProfileOpen.value = true
  } catch (e) {
    localError.value = e.message || String(e)
  } finally {
    busy.value = false
  }
}

function handleHotkey(e) {
  const tag = e.target?.tagName?.toLowerCase?.()
  if (tag === 'input' || tag === 'textarea' || tag === 'select') return
  if (dialogueOpen.value || npcPanelOpen.value || interactOpen.value) return
  const key = String(e.key || '').toLowerCase()
  if (key === '1') {
    e.preventDefault()
    onHotbarTalk()
  } else if (key === '2') {
    e.preventDefault()
    onHotbarRead()
  } else if (key === '3') {
    e.preventDefault()
    onHotbarTrain()
  } else if (key === '4') {
    e.preventDefault()
    onHotbarRest()
  } else if (key === '5') {
    e.preventDefault()
    onHotbarEvent()
  } else if (key === 'r') {
    e.preventDefault()
    onRefresh()
  }
}

function onHotbarEvent() {
  const event = storyEvents.value[0]
  if (!event) {
    showToast('当前还没有可触发的章节事件。')
    return
  }
  openStoryEvent(event.id)
}

function onHotbarTalk() {
  const npc = nearbyNpcs.value[0]
  if (!npc) {
    showToast('先靠近地图上的 NPC，再按对话。')
    return
  }
  selectedNpcId.value = npc.id
  dialogueOpen.value = true
}

async function onHotbarRead() {
  if (busy.value) return
  busy.value = true
  localError.value = ''
  try {
    await props.playerAction({
      kind: 'set_flag',
      flag_key: 'prologue_reading_done',
      flag_value: 1
    })
    await refreshStoryEvents()
    showToast('已读完书页：规则与边界的线索被记下。')
    syncPlayerFromState()
  } catch (e) {
    localError.value = e.message || String(e)
  } finally {
    busy.value = false
  }
}

async function onHotbarTrain() {
  if (busy.value) return
  busy.value = true
  localError.value = ''
  try {
    await props.dailyTick(1, 'heuristic')
    await refreshStoryEvents()
    showToast('训练推进了一个时刻。')
    syncPlayerFromState()
  } catch (e) {
    localError.value = e.message || String(e)
  } finally {
    busy.value = false
  }
}

async function onHotbarRest() {
  if (busy.value) return
  busy.value = true
  localError.value = ''
  try {
    await props.playerAction({ kind: 'rest_until_next_day' })
    await refreshStoryEvents()
    showToast('你回到小屋休息。新的一天开始了。')
    syncPlayerFromState()
  } catch (e) {
    localError.value = e.message || String(e)
  } finally {
    busy.value = false
  }
}

async function onInteractAction(act) {
  busy.value = true
  localError.value = ''
  try {
    if (act.type === 'set_flag') {
      await props.playerAction({
        kind: 'set_flag',
        flag_key: act.flag_key,
        flag_value: act.flag_value ?? 1
      })
    } else if (act.type === 'daily_tick') {
      await props.dailyTick(Number(act.n) || 1, 'heuristic')
    } else if (act.type === 'compound_sleep') {
      await props.playerAction({ kind: 'set_location', location: 'home' })
      await props.dailyTick(Number(act.daily_n) || 1, 'heuristic')
    } else {
      throw new Error('未知互动类型')
    }
    showToast(act.toast || '完成')
    interactOpen.value = false
    await refreshStoryEvents()
  } catch (e) {
    localError.value = e.message || String(e)
  } finally {
    busy.value = false
  }
}

async function onRefresh() {
  busy.value = true
  localError.value = ''
  try {
    await props.refresh()
    await refreshStoryEvents()
    syncPlayerFromState()
  } catch (e) {
    localError.value = e.message || String(e)
  } finally {
    busy.value = false
  }
}

async function onDaily() {
  busy.value = true
  localError.value = ''
  try {
    await props.dailyTick(1, 'heuristic')
    await refreshStoryEvents()
    syncPlayerFromState()
  } catch (e) {
    localError.value = e.message || String(e)
  } finally {
    busy.value = false
  }
}

async function onFlag() {
  busy.value = true
  localError.value = ''
  try {
    await props.playerAction({
      kind: 'set_flag',
      flag_key: 'prologue_reading_done',
      flag_value: 1
    })
    await refreshStoryEvents()
    syncPlayerFromState()
  } catch (e) {
    localError.value = e.message || String(e)
  } finally {
    busy.value = false
  }
}

async function onStory() {
  busy.value = true
  localError.value = ''
  try {
    await props.storyAdvance('mq01_tree_arc')
    await refreshStoryEvents()
    syncPlayerFromState()
  } catch (e) {
    localError.value = e.message || String(e)
  } finally {
    busy.value = false
  }
}

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
    showToast('当前旅程已导出为本地存档。')
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
  busy.value = true
  localError.value = ''
  try {
    const text = await file.text()
    const save = JSON.parse(text)
    await props.importSave(save)
    await refreshStoryEvents()
    syncPlayerFromState()
    showToast('存档已导入，旅程状态恢复完成。')
  } catch (err) {
    localError.value = err.message || String(err)
  } finally {
    if (saveFileEl.value) saveFileEl.value.value = ''
    busy.value = false
  }
}

async function onStoryEventChoose(choice) {
  const event = selectedStoryEvent.value
  if (!event?.id || !choice?.id || busy.value) return
  busy.value = true
  localError.value = ''
  try {
    const res = await props.chooseStoryEvent({
      event_id: event.id,
      choice_id: choice.id
    })
    const text = res?.choice?.result_text || `${event.title} 已完成。`
    showToast(text)
    storyResult.value = {
      ...res,
      event_title: event.title
    }
    storyResultOpen.value = true
    storyEventOpen.value = false
    storyEvents.value = Array.isArray(res?.available_events) ? res.available_events : storyEvents.value
    await refreshStoryEvents()
    syncPlayerFromState()
  } catch (e) {
    localError.value = e.message || String(e)
  } finally {
    busy.value = false
  }
}
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
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.42),
    0 18px 54px rgba(0, 0, 0, 0.5),
    0 0 30px rgba(94, 207, 255, 0.08);
  background: var(--field-deep);
}

.mmo-player-frame {
  position: absolute;
  z-index: 3;
  top: 0.75rem;
  left: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  width: min(330px, calc(100% - 1.5rem));
  padding: 0.58rem 0.68rem;
  border-radius: 10px;
  background: linear-gradient(90deg, rgba(8, 13, 23, 0.9), rgba(16, 28, 45, 0.7));
  border: 1px solid rgba(229, 196, 92, 0.36);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.32);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  pointer-events: none;
}

.avatar-disc {
  flex: 0 0 auto;
  width: 2.55rem;
  height: 2.55rem;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff8dc;
  font-weight: 800;
  background:
    radial-gradient(circle at 38% 30%, rgba(255, 255, 255, 0.35), transparent 28%),
    linear-gradient(145deg, #b67a28, #4a2d16 72%);
  border: 2px solid rgba(255, 232, 151, 0.68);
  box-shadow: 0 0 18px rgba(212, 175, 55, 0.24);
}

.player-vitals {
  flex: 1;
  min-width: 0;
}

.vital-name {
  font-size: 0.78rem;
  color: #fff7d6;
  font-weight: 800;
  margin-bottom: 0.28rem;
  text-shadow: 0 1px 2px #000;
}

.bar {
  height: 0.48rem;
  border-radius: 999px;
  overflow: hidden;
  margin-top: 0.22rem;
  background: rgba(2, 6, 14, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
}

.bar.hp span {
  background: linear-gradient(90deg, #e11d48, #fb7185);
}

.bar.mp span {
  background: linear-gradient(90deg, #0ea5e9, #67e8f9);
}

.mmo-scene-frame {
  position: absolute;
  z-index: 3;
  top: 0.75rem;
  left: 50%;
  transform: translateX(-50%);
  min-width: 11rem;
  padding: 0.48rem 0.8rem;
  border-radius: 999px;
  text-align: center;
  background: rgba(6, 12, 24, 0.72);
  border: 1px solid rgba(94, 207, 255, 0.24);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  pointer-events: none;
}

.mmo-scene-frame strong,
.mmo-scene-frame span {
  display: block;
}

.mmo-scene-frame strong {
  font-size: 0.84rem;
  color: #f8fafc;
}

.mmo-scene-frame span {
  margin-top: 0.08rem;
  font-size: 0.66rem;
  color: var(--muted);
}

.quest-tracker {
  position: absolute;
  z-index: 3;
  right: 0.75rem;
  top: 13.25rem;
  width: min(310px, calc(100% - 1.5rem));
  padding: 0.68rem 0.75rem;
  border-radius: 10px;
  background: rgba(6, 12, 24, 0.76);
  border: 1px solid rgba(94, 207, 255, 0.22);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.32);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  pointer-events: auto;
}

.quest-rail-title {
  font-size: 0.65rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sao-gold);
  margin-bottom: 0.35rem;
  font-weight: 700;
}

.quest-rail-body {
  margin: 0;
  font-size: 0.78rem;
  line-height: 1.55;
  color: var(--ink);
  opacity: 0.92;
}

.tracker-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.55rem;
}

.event-strip {
  display: grid;
  gap: 0.32rem;
  margin-top: 0.58rem;
}

.event-strip button {
  width: 100%;
  min-height: 1.9rem;
  padding: 0.34rem 0.48rem;
  border-radius: 8px;
  border: 1px solid rgba(246, 211, 110, 0.28);
  background: rgba(78, 56, 25, 0.72);
  color: #fff7d6;
  font-size: 0.72rem;
  font-weight: 800;
  text-align: left;
  cursor: pointer;
}

.event-strip button:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.78);
  box-shadow: 0 0 15px rgba(212, 175, 55, 0.2);
}

.event-strip button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tracker-meta span {
  padding: 0.22rem 0.42rem;
  border-radius: 999px;
  color: #dbeafe;
  background: rgba(30, 64, 175, 0.28);
  border: 1px solid rgba(147, 197, 253, 0.18);
  font-size: 0.66rem;
}

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

.action-hotbar {
  position: absolute;
  z-index: 5;
  left: 50%;
  bottom: 0.72rem;
  transform: translateX(-50%);
  display: grid;
  grid-template-columns: repeat(5, minmax(3.7rem, 1fr));
  gap: 0.45rem;
  width: min(520px, calc(100% - 1.5rem));
  padding: 0.45rem;
  border-radius: 12px;
  background: rgba(4, 8, 18, 0.78);
  border: 1px solid rgba(229, 196, 92, 0.3);
  box-shadow: 0 18px 38px rgba(0, 0, 0, 0.38), inset 0 1px 0 rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.action-hotbar button {
  min-height: 3.1rem;
  padding: 0.35rem 0.28rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.18rem;
  background:
    linear-gradient(180deg, rgba(82, 63, 35, 0.92), rgba(18, 25, 38, 0.96)),
    url("/assets/kenney-ui/buttonSquare_blue.png") center / 100% 100% no-repeat;
  border-color: rgba(245, 208, 112, 0.34);
  color: #f8fafc;
}

.action-hotbar button:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.8);
  box-shadow: 0 0 18px rgba(212, 175, 55, 0.34);
}

.action-hotbar kbd {
  min-width: 1.2rem;
  height: 1.2rem;
  display: inline-grid;
  place-items: center;
  border-radius: 4px;
  color: #1f2937;
  background: #f8fafc;
  border: 1px solid rgba(255, 255, 255, 0.55);
  font-size: 0.68rem;
  font-weight: 900;
  font-family: inherit;
}

.action-hotbar span {
  font-size: 0.72rem;
  font-weight: 800;
}

.field-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.55rem;
}

.field-kicker {
  margin: 0 0 0.1rem;
  font-size: 0.66rem;
  letter-spacing: 0.12em;
  color: var(--sao-cyan);
  font-weight: 700;
}

.field-title h2 {
  margin: 0;
  font-size: 1.24rem;
  font-weight: 700;
  letter-spacing: 0;
  background: linear-gradient(110deg, #fff 0%, var(--sao-cyan) 55%, var(--sao-gold) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.save-file {
  display: none;
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

.field-err {
  padding: 0.45rem 0.65rem;
  margin-bottom: 0.5rem;
  border-radius: 10px;
  background: rgba(127, 29, 29, 0.35);
  border: 1px solid rgba(248, 113, 113, 0.35);
  color: #fecaca;
  font-size: 0.82rem;
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
}

.field-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem 1rem;
  margin-top: 0.55rem;
  padding: 0.6rem 0.75rem;
  border-radius: 10px;
  background: linear-gradient(160deg, rgba(94, 207, 255, 0.06), rgba(15, 23, 42, 0.75));
  border: 1px solid var(--sao-border-dim);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
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
  font-size: 0.76rem;
  padding: 0.38rem 0.65rem;
  border-radius: 9px;
  border: 1px solid var(--sao-border-dim);
  background: rgba(15, 23, 42, 0.55);
  color: var(--ink);
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
}

.tb:hover:not(:disabled) {
  background: rgba(94, 207, 255, 0.1);
  border-color: var(--sao-border);
  box-shadow: var(--sao-glow);
}

.tb-ghost {
  background: rgba(12, 20, 36, 0.5);
}

.tb-primary {
  background: linear-gradient(180deg, var(--accent), #b8324a);
  border-color: rgba(251, 113, 133, 0.45);
  color: #fff;
  font-weight: 600;
}

.tb-accent {
  background: linear-gradient(180deg, #6366f1, #4f46e5);
  border-color: rgba(165, 180, 252, 0.45);
  color: #fff;
  font-weight: 600;
}

.tb:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.phaser-host {
  aspect-ratio: 1280 / 720;
  width: 100%;
  max-height: calc(100vh - 7.5rem);
  overflow: hidden;
  background: radial-gradient(ellipse 100% 80% at 50% 0%, rgba(94, 207, 255, 0.06), transparent 55%),
    var(--field-deep);
}

.regions-details {
  margin-top: 0.65rem;
  font-size: 0.78rem;
  color: var(--muted);
}

.regions-details summary {
  cursor: pointer;
  color: var(--sao-cyan);
}

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

.field-toast {
  position: fixed;
  bottom: 1.25rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 90;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  background: linear-gradient(165deg, rgba(22, 101, 52, 0.95), rgba(15, 60, 30, 0.98));
  border: 1px solid rgba(134, 239, 172, 0.4);
  color: #ecfccb;
  font-size: 0.82rem;
  max-width: min(92vw, 480px);
  text-align: center;
  pointer-events: none;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35), 0 0 20px rgba(78, 204, 163, 0.15);
}

@media (max-width: 900px) {
  .field-slice {
    padding: 0.55rem;
  }

  .field-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .mmo-player-frame,
  .mmo-scene-frame,
  .quest-tracker,
  .chat-strip {
    position: absolute;
  }

  .mmo-scene-frame {
    top: 4.45rem;
    left: 0.55rem;
    right: auto;
    transform: none;
    min-width: 0;
  }

  .quest-tracker {
    top: 10.75rem;
    left: auto;
    right: 0.55rem;
    bottom: auto;
    width: min(270px, calc(100% - 1.1rem));
    padding: 0.52rem 0.6rem;
  }

  .quest-rail-body {
    display: -webkit-box;
    overflow: hidden;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .tracker-meta {
    margin-top: 0.35rem;
  }

  .chat-strip {
    display: none;
  }

  .action-hotbar {
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 0.28rem;
    width: calc(100% - 1rem);
    bottom: 0.5rem;
    padding: 0.35rem;
  }

  .action-hotbar button {
    min-height: 2.75rem;
  }

  .action-hotbar span {
    font-size: 0.66rem;
  }

}
</style>
