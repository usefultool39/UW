<template>
  <div class="field-map-shell" :class="{ shake: shakeActive }">
    <div class="map-corner tl" />
    <div class="map-corner tr" />
    <div class="map-corner bl" />
    <div class="map-corner br" />
    <div ref="hostEl" class="phaser-host" />
    <div class="scene-badge">
      <span class="badge-dot" :class="timeBand" />
      {{ sceneLabel }} · 第 {{ day }} 天 · {{ timeBandLabel }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  simState: { type: Object, required: true },
  worldMap: { type: Object, required: true },
  storyEvents: { type: Array, default: () => [] },
  timeBandLabel: { type: String, default: '早晨' },
  sceneLabel: { type: String, default: '——' }
})

const emit = defineEmits([
  'tile-click',
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

const day = ref(1)
const timeBand = ref('morning')

function triggerShake() {
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  shakeActive.value = true
  clearTimeout(shakeTimer)
  shakeTimer = setTimeout(() => { shakeActive.value = false }, 220)
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
    isBusy: () => false,
    getNearbyInteractPoi: () => null,
    getStoryEvents: () => props.storyEvents,
    openStoryEventPanel: openStoryEventPanel
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
  await nextTick()
  await bootPhaser()
})

onUnmounted(() => {
  clearTimeout(shakeTimer)
  if (game) {
    game.destroy(true)
    game = null
  }
  sceneInstance = null
})

// Expose shake trigger for parent
defineExpose({ triggerShake, sceneInstance: () => sceneInstance })
</script>

<style scoped>
.field-map-shell {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--field-frame);
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.42),
    0 18px 54px rgba(0, 0, 0, 0.5),
    0 0 30px rgba(94, 207, 255, 0.08);
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
  aspect-ratio: 1280 / 720;
  overflow: hidden;
  background: radial-gradient(ellipse 100% 80% at 50% 0%, rgba(94, 207, 255, 0.06), transparent 55%),
    var(--field-deep);
  display: block;
}

.scene-badge {
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
}
</style>
