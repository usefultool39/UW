<template>
  <div class="field-map-shell" :class="{ shake: shakeActive }">
    <div class="map-corner tl" />
    <div class="map-corner tr" />
    <div class="map-corner bl" />
    <div class="map-corner br" />
    <div ref="hostEl" class="phaser-host" />
    <div class="atmosphere-layer" :class="[timeBand, weatherCode]" />
    <div class="weather-note">{{ weatherNote }}</div>
    <div
      v-if="miniWidth && miniHeight"
      class="dom-minimap"
      role="button"
      aria-label="小地图"
      tabindex="0"
      @pointerdown.stop.prevent
      @click.stop.prevent="handleMiniMapClick"
    >
      <div class="dom-minimap-head">
        <span>北境地图</span>
        <span>N</span>
      </div>
      <svg class="dom-minimap-svg" :viewBox="`0 0 ${miniWidth} ${miniHeight}`" preserveAspectRatio="none">
        <rect
          v-for="tile in miniTiles"
          :key="tile.key"
          :x="tile.x"
          :y="tile.y"
          width="1"
          height="1"
          :fill="tile.color"
        />
        <rect
          v-for="zone in miniZones"
          :key="zone.id"
          class="dom-minimap-zone"
          :x="zone.x"
          :y="zone.y"
          :width="zone.w"
          :height="zone.h"
          :stroke="zone.color"
        />
        <rect
          v-if="miniViewport"
          class="dom-minimap-viewport"
          :x="miniViewport.x"
          :y="miniViewport.y"
          :width="miniViewport.w"
          :height="miniViewport.h"
        />
        <circle
          v-for="agent in miniAgents"
          :key="agent.id"
          class="dom-minimap-agent"
          :cx="agent.x + 0.5"
          :cy="agent.y + 0.5"
          r="0.42"
          :fill="agent.color"
        />
        <path
          v-for="event in miniEvents"
          :key="event.id"
          class="dom-minimap-event"
          :d="`M ${event.x + 0.5} ${event.y + 0.08} L ${event.x + 0.92} ${event.y + 0.5} L ${event.x + 0.5} ${event.y + 0.92} L ${event.x + 0.08} ${event.y + 0.5} Z`"
        />
        <circle
          v-if="miniPlayer"
          class="dom-minimap-player"
          :cx="miniPlayer.x + 0.5"
          :cy="miniPlayer.y + 0.5"
          r="0.52"
        />
      </svg>
      <div v-if="miniLegend.length" class="dom-minimap-legend" aria-hidden="true">
        <span v-for="item in miniLegend" :key="item.key">
          <i :style="{ background: item.color }" />
          {{ item.label }}
        </span>
      </div>
      <div class="dom-minimap-foot">亮框为可进入功能区</div>
    </div>
    <div class="scene-badge">
      <span class="badge-dot" :class="timeBand" />
      {{ sceneLabel }} · 第 {{ day }} 天 · {{ timeBandLabel }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { SCENE_DEFINITIONS } from '../field/sceneRegistry.js'

const props = defineProps({
  simState: { type: Object, required: true },
  worldMap: { type: Object, required: true },
  storyEvents: { type: Array, default: () => [] },
  timeBandLabel: { type: String, default: '早晨' },
  sceneLabel: { type: String, default: '——' },
  busy: { type: Boolean, default: false },
  nearbyInteract: { type: Object, default: null }
})

const emit = defineEmits([
  'tile-click',
  'blocked-click',
  'npc-click',
  'interact-click',
  'event-click',
  'ready'
])

const hostEl = ref(null)
const shakeActive = ref(false)
let shakeTimer = null
let game = null
let sceneInstance = null
let miniTimer = null
let miniLastUpdate = 0
let resizeObserver = null

const day = ref(1)
const timeBand = ref('morning')
const miniViewport = ref(null)
const weatherCode = computed(() => props.simState?.weather || 'clear')
const weatherNote = computed(() => props.simState?.weather_note || '清亮的风穿过北境村道。')

const MINI_COLORS = {
  0: '#6f9362',
  1: '#223c2d',
  2: '#4b8fa0',
  3: '#bca982',
  4: '#766f65'
}

const miniRows = computed(() => props.worldMap?.rows || [])
const miniWidth = computed(() => miniRows.value[0]?.length || 0)
const miniHeight = computed(() => miniRows.value.length || 0)

// Cache tiles — recompute only when worldMap reference changes, not every reactive update
const miniTilesCache = ref([])
let lastWorldMapId = null

watch(
  () => props.worldMap,
  (map) => {
    const mapId = map?.id || ''
    if (mapId === lastWorldMapId) return
    lastWorldMapId = mapId
    const tiles = []
    const rows = map?.rows || []
    rows.forEach((row, y) => {
      String(row || '').split('').forEach((ch, x) => {
        tiles.push({ key: `${x}-${y}`, x, y, color: MINI_COLORS[ch] || MINI_COLORS[0] })
      })
    })
    miniTilesCache.value = tiles
  },
  { immediate: true }
)

const miniTiles = computed(() => miniTilesCache.value)

function cssColorFromNumber(value, fallback = '#7dd3fc') {
  const n = Number(value)
  if (!Number.isFinite(n)) return fallback
  return `#${n.toString(16).padStart(6, '0').slice(-6)}`
}

const miniZones = computed(() => {
  const zones = Array.isArray(props.worldMap?.scene_zones) ? props.worldMap.scene_zones : []
  return zones
    .map((zone) => {
      const id = String(zone.scene_id || '')
      const def = SCENE_DEFINITIONS[id] || {}
      const regionType = zone.regionType || def.regionType || def.role || 'explore'
      const x1 = Number(zone.x1 ?? 0)
      const y1 = Number(zone.y1 ?? 0)
      const x2 = Number(zone.x2 ?? x1)
      const y2 = Number(zone.y2 ?? y1)
      return {
        id,
        role: def.role || regionType,
        regionType,
        label: zone.label || def.roleLabel || def.label || '功能区',
        x: Math.min(x1, x2),
        y: Math.min(y1, y2),
        w: Math.abs(x2 - x1) + 1,
        h: Math.abs(y2 - y1) + 1,
        color: cssColorFromNumber(def.zoneColor, '#7dd3fc')
      }
    })
    .filter((zone) => zone.id)
})

const miniLegend = computed(() => {
  const byRole = new Map()
  miniZones.value.forEach((zone) => {
    const key = zone.regionType || zone.role
    if (key === 'explore' || byRole.has(key)) return
    byRole.set(key, {
      key,
      label: zone.label,
      color: zone.color
    })
  })
  return Array.from(byRole.values())
})

const miniPlayer = computed(() => {
  const p = props.simState?.player
  if (!p) return null
  return { x: Number(p.tile_x) || 0, y: Number(p.tile_y) || 0 }
})

const miniAgents = computed(() => {
  const colors = {
    alice: '#70e0bb',
    eugeo: '#a78bfa',
    kirito: '#5ecfff'
  }
  return (props.simState?.agents || [])
    .map((agent) => ({
      id: agent.id,
      x: Number(agent.tile_x),
      y: Number(agent.tile_y),
      color: colors[agent.id] || '#5ecfff'
    }))
    .filter((agent) => Number.isFinite(agent.x) && Number.isFinite(agent.y))
})

const miniEvents = computed(() => (props.storyEvents || [])
  .map((event) => ({
    id: event.id,
    x: Number(event.location?.tile_x),
    y: Number(event.location?.tile_y)
  }))
  .filter((event) => Number.isFinite(event.x) && Number.isFinite(event.y)))

function updateMiniViewport() {
  const now = Date.now()
  if (now - (miniLastUpdate || 0) < 100) {
    return
  }
  miniLastUpdate = now
  if (sceneInstance?.cameras?.main && sceneInstance._tileSize) {
    const view = sceneInstance.cameras.main.worldView
    const ts = sceneInstance._tileSize
    const width = Math.max(1, miniWidth.value)
    const height = Math.max(1, miniHeight.value)
    const w = Math.min(width, Math.max(0.6, view.width / ts))
    const h = Math.min(height, Math.max(0.6, view.height / ts))
    const x = Math.min(Math.max(0, view.x / ts), Math.max(0, width - w))
    const y = Math.min(Math.max(0, view.y / ts), Math.max(0, height - h))
    miniViewport.value = {
      x,
      y,
      w,
      h
    }
  }
}

function handleMiniMapClick(event) {
  const w = miniWidth.value
  const h = miniHeight.value
  if (!w || !h || !sceneInstance?.centerCameraOnTile) return
  const rect = event.currentTarget.getBoundingClientRect()
  const u = (event.clientX - rect.left) / Math.max(1, rect.width)
  const v = (event.clientY - rect.top) / Math.max(1, rect.height)
  sceneInstance.centerCameraOnTile(Math.floor(u * w), Math.floor(v * h))
}

function triggerShake() {
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  shakeActive.value = true
  clearTimeout(shakeTimer)
  shakeTimer = setTimeout(() => { shakeActive.value = false }, 220)
}

function triggerCameraShake() {
  if (!sceneInstance?.cameras?.main) return
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  sceneInstance.cameras.main.shake(180, 0.004)
  triggerShake()
}

watch(
  () => props.simState?.day,
  (d) => { day.value = d ?? 1 }
)

watch(
  () => props.simState?.time_band,
  (tb) => { timeBand.value = tb || 'morning' }
)

async function bootPhaser() {
  if (!hostEl.value) return
  const Phaser = (await import('phaser')).default
  const { createWorldFieldSceneClass } = await import('../field/createWorldFieldScene.js')

  const getMap = () => props.worldMap

  const onTilePick = async (tx, ty) => {
    emit('tile-click', { tile_x: tx, tile_y: ty })
  }

  const onBlockedTilePick = (payload) => {
    emit('blocked-click', payload)
  }

  const openInteractPanel = () => emit('interact-click')
  const openNpcPanel = (agentId) => emit('npc-click', agentId)
  const openStoryEventPanel = (eventId) => emit('event-click', eventId)

  const SceneClass = createWorldFieldSceneClass(Phaser, {
    getMap,
    onTilePick,
    getSimState: () => props.simState,
    assignSceneInstance: (sc) => {
      sceneInstance = sc
      emit('ready', sc)
    },
    syncPlayerFromState: () => {
      if (!sceneInstance || !props.simState?.player) return
      const p = props.simState.player
      const ts = sceneInstance._tileSize
      sceneInstance.playerRoot?.setPosition?.((p.tile_x + 0.5) * ts, (p.tile_y + 0.5) * ts)
      sceneInstance._hudText?.setText?.(`${props.sceneLabel} · 第 ${props.simState.day} 天 · ${props.timeBandLabel}`)
      sceneInstance.syncNpcs?.()
    },
    openInteractPanel,
    openNpcPanel,
    isBusy: () => props.busy,
    getNearbyInteractPoi: () => props.nearbyInteract,
    getStoryEvents: () => props.storyEvents,
    openStoryEventPanel: openStoryEventPanel,
    onBlockedTilePick
  })

  const rect = hostEl.value.getBoundingClientRect()
  const initialWidth = Math.max(960, Math.floor(rect.width || window.innerWidth || 1280))
  const initialHeight = Math.max(540, Math.floor(rect.height || window.innerHeight || 720))

  game = new Phaser.Game({
    type: Phaser.AUTO,
    width: initialWidth,
    height: initialHeight,
    parent: hostEl.value,
    transparent: true,
    scene: SceneClass,
    scale: { mode: Phaser.Scale.RESIZE, autoCenter: Phaser.Scale.NO_CENTER }
  })

  resizeObserver = new ResizeObserver((entries) => {
    const box = entries[0]?.contentRect
    if (!box || !game) return
    const w = Math.max(640, Math.floor(box.width))
    const h = Math.max(420, Math.floor(box.height))
    game.scale.resize(w, h)
    sceneInstance?.handleViewportResize?.(w, h)
    updateMiniViewport()
  })
  resizeObserver.observe(hostEl.value)
}

onMounted(async () => {
  await nextTick()
  await bootPhaser()
  if (typeof window !== 'undefined') {
    updateMiniViewport()
    miniTimer = window.setInterval(updateMiniViewport, 120)
  }
})

onUnmounted(() => {
  clearTimeout(shakeTimer)
  if (miniTimer) {
    window.clearInterval(miniTimer)
    miniTimer = null
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (game) {
    game.destroy(true)
    game = null
  }
  sceneInstance = null
})

// Expose shake trigger for parent
defineExpose({ triggerShake, triggerCameraShake, sceneInstance: () => sceneInstance })

watch(
  () => props.storyEvents,
  () => {
    sceneInstance?.rebuildPois?.()
  },
  { deep: true }
)
</script>

<style scoped>
.field-map-shell {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 100vh;
  border-radius: 0;
  overflow: hidden;
  border: 0;
  box-shadow: none;
  background: var(--field-deep);
  will-change: transform;
}

.field-map-shell.shake {
  animation: map-shake 0.22s ease;
}

@keyframes map-shake {
  0%, 100% { transform: translate(0, 0); }
  20% { transform: translate(2px, -1px); }
  40% { transform: translate(-2px, 1px); }
  60% { transform: translate(2px, 1px); }
  80% { transform: translate(-1px, -1px); }
}

/* Decorative corner brackets */
.map-corner {
  display: none;
  position: absolute;
  width: 16px;
  height: 16px;
  pointer-events: none;
  z-index: 6;
}

.map-corner.tl {
  top: 6px;
  left: 6px;
  border-top: 2px solid var(--sao-cyan);
  border-left: 2px solid var(--sao-cyan);
  opacity: 0.7;
}

.map-corner.tr {
  top: 6px;
  right: 6px;
  border-top: 2px solid var(--sao-cyan);
  border-right: 2px solid var(--sao-cyan);
  opacity: 0.7;
}

.map-corner.bl {
  bottom: 6px;
  left: 6px;
  border-bottom: 2px solid var(--sao-gold);
  border-left: 2px solid var(--sao-gold);
  opacity: 0.6;
}

.map-corner.br {
  bottom: 6px;
  right: 6px;
  border-bottom: 2px solid var(--sao-gold);
  border-right: 2px solid var(--sao-gold);
  opacity: 0.6;
}

.phaser-host {
  width: 100%;
  height: 100%;
  min-height: 100vh;
  overflow: hidden;
  background: radial-gradient(ellipse 100% 80% at 50% 0%, rgba(94, 207, 255, 0.06), transparent 55%),
    var(--field-deep);
  display: block;
}

.atmosphere-layer {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  mix-blend-mode: soft-light;
  opacity: 0.35;
}

.atmosphere-layer.morning {
  background: linear-gradient(180deg, rgba(255, 244, 214, 0.2), transparent 42%);
}

.atmosphere-layer.afternoon {
  background: linear-gradient(180deg, rgba(255, 226, 173, 0.14), transparent 48%);
}

.atmosphere-layer.evening {
  background: linear-gradient(180deg, rgba(251, 146, 60, 0.15), rgba(88, 28, 135, 0.16));
}

.atmosphere-layer.night {
  opacity: 0.62;
  background: linear-gradient(180deg, rgba(8, 18, 48, 0.42), rgba(2, 6, 23, 0.55));
}

.atmosphere-layer.mist {
  opacity: 0.48;
  background:
    linear-gradient(100deg, rgba(226, 232, 240, 0.24), transparent 34%, rgba(226, 232, 240, 0.16) 68%, transparent),
    linear-gradient(180deg, rgba(186, 230, 253, 0.12), transparent 60%);
}

.atmosphere-layer.drizzle {
  opacity: 0.42;
  background:
    repeating-linear-gradient(110deg, rgba(226, 232, 240, 0.16) 0 1px, transparent 1px 13px),
    linear-gradient(180deg, rgba(30, 64, 175, 0.12), transparent 56%);
}

.weather-note {
  display: none;
  position: absolute;
  z-index: 4;
  left: 0.75rem;
  bottom: 5.4rem;
  max-width: min(460px, calc(100% - 1.5rem));
  padding: 0.42rem 0.62rem;
  border-radius: 8px;
  background: rgba(5, 10, 18, 0.64);
  border: 1px solid rgba(186, 230, 253, 0.14);
  color: #dbeafe;
  font-size: 0.72rem;
  line-height: 1.45;
  pointer-events: none;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.dom-minimap {
  position: absolute;
  top: 4rem;
  right: 0.8rem;
  z-index: 30;
  width: clamp(132px, 12vw, 178px);
  min-width: 132px;
  padding: 0.34rem 0.38rem 0.34rem;
  border: 1px solid rgba(246, 211, 110, 0.2);
  background: rgba(4, 10, 18, 0.58);
  box-shadow: 0 12px 26px rgba(0, 0, 0, 0.28), inset 0 0 0 1px rgba(94, 207, 255, 0.08);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  cursor: pointer;
  pointer-events: auto;
}

.dom-minimap:hover {
  border-color: rgba(246, 211, 110, 0.42);
  background: rgba(4, 10, 18, 0.82);
}

.dom-minimap:focus-visible {
  outline: 2px solid var(--sao-cyan);
  outline-offset: 3px;
}

.dom-minimap-head,
.dom-minimap-foot {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  font-size: 0.56rem;
  font-weight: 800;
  color: #fde68a;
  line-height: 1;
}

.dom-minimap-head span:last-child {
  color: #bae6fd;
  font-family: Georgia, serif;
}

.dom-minimap-svg {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 9;
  margin-top: 0.28rem;
  border: 1px solid rgba(94, 207, 255, 0.25);
  background: #020617;
  image-rendering: crisp-edges;
}

.dom-minimap-foot {
  display: none;
  margin-top: 0.32rem;
  justify-content: flex-start;
  color: #cbd5e1;
  font-size: 0.56rem;
  font-weight: 700;
}

.dom-minimap-legend {
  display: none;
  flex-wrap: wrap;
  gap: 0.24rem 0.42rem;
  margin-top: 0.36rem;
  color: #e2e8f0;
  font-size: 0.56rem;
  line-height: 1.2;
}

.dom-minimap-legend span {
  display: inline-flex;
  align-items: center;
  gap: 0.22rem;
  white-space: nowrap;
}

.dom-minimap-legend i {
  width: 0.42rem;
  height: 0.42rem;
  border-radius: 50%;
  box-shadow: 0 0 0 1px rgba(255, 247, 214, 0.35);
}

.dom-minimap-viewport {
  fill: rgba(255, 255, 255, 0.06);
  stroke: #fbbf24;
  stroke-width: 0.22;
  vector-effect: non-scaling-stroke;
}

.dom-minimap-zone {
  fill: rgba(255, 255, 255, 0.03);
  stroke-width: 0.55;
  vector-effect: non-scaling-stroke;
  stroke-dasharray: 1.4 0.9;
}

.dom-minimap-agent {
  stroke: #05111c;
  stroke-width: 0.16;
  vector-effect: non-scaling-stroke;
}

.dom-minimap-event {
  fill: #fde047;
  stroke: #422006;
  stroke-width: 0.14;
  vector-effect: non-scaling-stroke;
}

.dom-minimap-player {
  fill: #fbbf24;
  stroke: #1a1209;
  stroke-width: 0.18;
  vector-effect: non-scaling-stroke;
}

.scene-badge {
  display: none;
  position: absolute;
  top: 0.75rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 4;
  padding: 0.4rem 0.75rem;
  border-radius: 999px;
  text-align: center;
  background: rgba(6, 12, 24, 0.76);
  border: 1px solid rgba(94, 207, 255, 0.24);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  font-size: 0.72rem;
  color: var(--ink);
  white-space: nowrap;
  pointer-events: none;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.badge-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: #94a3b8;
  flex: 0 0 auto;
}

.badge-dot.morning { background: #fbbf24; }
.badge-dot.afternoon { background: #fb923c; }
.badge-dot.evening { background: #a78bfa; }
.badge-dot.night { background: #60a5fa; }

@media (max-width: 900px) {
  .scene-badge {
    top: 0.55rem;
    left: 0.55rem;
    right: auto;
    transform: none;
    font-size: 0.66rem;
    padding: 0.32rem 0.55rem;
  }

  .dom-minimap {
    top: 3.5rem;
    right: 0.55rem;
    width: clamp(120px, 30vw, 150px);
  }
}
</style>
