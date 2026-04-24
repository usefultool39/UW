<template>
  <div class="scene-wrapper" :class="{ shake: shakeActive }">
    <div class="scene-layers" :data-scene="currentScene">
      <div class="scene-bg-base" :class="currentScene" />
      <div class="scene-bg-glow" :class="currentScene" />
      <div class="scene-bg-silhouette" :class="currentScene" />
    </div>
    <div class="scene-overlay">
      <div class="scene-title" :key="currentScene">{{ sceneTitles[currentScene] }}</div>
      <div class="scene-characters">
        <div v-for="agent in agentsHere" :key="agent.id" class="scene-char">
          <img
            :src="getAgentMeta(agent.id).img"
            :alt="getAgentMeta(agent.id).display"
            @error="onAgentImgError($event, getAgentMeta(agent.id))"
          />
          <div class="scene-char-name">{{ getAgentMeta(agent.id).display }}</div>
          <div
            class="scene-char-action"
            :class="{ fail: agent.last_action_ok === false }"
          >
            {{ actionLabels[agent.last_action] || agent.last_action }}
          </div>
        </div>
      </div>
    </div>
    <div class="scene-labels" aria-hidden="true">
      <span class="scene-label" :class="{ active: currentScene === 'tree' }">巨树</span>
      <span class="scene-label" :class="{ active: currentScene === 'home' }">留宿</span>
      <span class="scene-label" :class="{ active: currentScene === 'table' }">食桌</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onUnmounted } from 'vue'
import { getAgentMeta, onAgentImgError } from '../constants/agents.js'

const props = defineProps({
  state: { type: Object, required: true },
  agents: { type: Array, required: true }
})

const actionLabels = {
  chop: '砍树', rest: '休息', move: '移动', noop: '观望',
  eat: '吃饭', sleep: '睡觉', go_home: '回家', cook: '做饭'
}

const sceneTitles = {
  tree: '巨树 · 基拉斯杉',
  home: '留宿 · 小屋',
  table: '食桌 · 午间'
}

const currentScene = computed(() => {
  const hasTable = props.agents.some(a => a.location === 'table')
  const hasHome = props.agents.some(a => a.location === 'home')
  const hasTree = props.agents.some(a => a.location === 'at_tree' || a.location === 'bench')
  if (hasTable) return 'table'
  if (hasHome && !hasTree) return 'home'
  return 'tree'
})

const agentsHere = computed(() => {
  if (currentScene.value === 'tree') {
    return props.agents.filter(a => a.location === 'at_tree' || a.location === 'bench')
  }
  return props.agents.filter(a => a.location === currentScene.value)
})

const shakeActive = ref(false)
let shakeTimer

function triggerShake() {
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return
  }
  shakeActive.value = true
  clearTimeout(shakeTimer)
  shakeTimer = setTimeout(() => {
    shakeActive.value = false
  }, 220)
}

watch(
  () =>
    `${props.state.tick}|${props.state.day}|` +
    props.agents.map(a => `${a.id}:${a.last_action}:${a.last_action_ok}`).join('|'),
  (_, prev) => {
    if (prev === undefined) return
    for (const ag of props.agents) {
      if (ag.last_action === 'chop' && ag.last_action_ok === true) {
        triggerShake()
        break
      }
    }
  }
)

onUnmounted(() => {
  clearTimeout(shakeTimer)
})
</script>

<style scoped>
.scene-wrapper {
  position: relative;
  overflow: hidden;
  min-height: clamp(420px, 52vh, 520px);
  padding-bottom: 5.25rem;
  box-shadow: inset 0 0 80px rgba(0, 0, 0, 0.25);
}

.scene-layers {
  position: absolute;
  inset: 0;
  transition: opacity 0.5s ease;
}

.scene-bg-base {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center bottom;
  transition: opacity 0.55s ease, transform 0.55s ease;
}

.scene-bg-base.tree {
  background: linear-gradient(180deg, #4a7ab0 0%, #6eb8c8 38%, #4a9060 72%, #2d5a3a 100%);
}

.scene-bg-base.home {
  background: linear-gradient(180deg, #1e2838 0%, #3a3228 45%, #4a4035 100%);
}

.scene-bg-base.table {
  background: linear-gradient(180deg, #2a2848 0%, #3d3a5c 50%, #4a4668 100%);
}

.scene-bg-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.55;
  transition: opacity 0.5s ease;
}

.scene-bg-glow.tree {
  background: radial-gradient(ellipse 85% 55% at 50% 12%, rgba(255, 255, 255, 0.45), transparent 58%);
}

.scene-bg-glow.home {
  background: radial-gradient(ellipse 70% 50% at 30% 20%, rgba(201, 162, 39, 0.2), transparent 55%);
}

.scene-bg-glow.table {
  background: radial-gradient(ellipse 60% 45% at 50% 15%, rgba(94, 207, 255, 0.15), transparent 50%);
}

.scene-bg-silhouette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  transition: opacity 0.5s ease, transform 0.55s ease;
}

.scene-bg-silhouette.tree::before {
  content: "";
  position: absolute;
  left: 50%;
  bottom: -8%;
  width: 140%;
  height: 72%;
  transform: translateX(-50%);
  background: radial-gradient(ellipse closest-side at 50% 100%, rgba(15, 40, 25, 0.75), transparent 70%);
  filter: blur(4px);
}

.scene-bg-silhouette.tree::after {
  content: "";
  position: absolute;
  left: 50%;
  bottom: 5%;
  width: 55%;
  height: 78%;
  transform: translateX(-50%);
  background: linear-gradient(180deg, rgba(12, 35, 22, 0.55) 0%, rgba(8, 22, 14, 0.85) 100%);
  border-radius: 50% 50% 8% 8% / 60% 60% 12% 12%;
  filter: blur(2px);
}

.scene-bg-silhouette.home::after {
  content: "";
  position: absolute;
  right: 8%;
  bottom: 12%;
  width: 42%;
  height: 38%;
  background: linear-gradient(180deg, rgba(30, 22, 18, 0.65), rgba(20, 14, 10, 0.9));
  clip-path: polygon(10% 100%, 0 45%, 20% 30%, 50% 8%, 80% 28%, 100% 42%, 92% 100%);
}

.scene-bg-silhouette.table::after {
  content: "";
  position: absolute;
  left: 50%;
  bottom: 18%;
  width: 70%;
  height: 22%;
  transform: translateX(-50%);
  background: rgba(20, 18, 35, 0.55);
  border-radius: 4px;
  box-shadow: 0 0 0 3px rgba(94, 207, 255, 0.12);
}

.scene-overlay {
  position: relative;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 1.75rem 1rem 0;
  min-height: 12rem;
}

.scene-title {
  font-size: clamp(1.15rem, 3.5vw, 1.65rem);
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #f4f8ff;
  text-shadow:
    0 0 20px rgba(94, 207, 255, 0.35),
    0 2px 12px rgba(0, 0, 0, 0.65);
  margin-bottom: 1.25rem;
  animation: titleIn 0.45s ease both;
}

@keyframes titleIn {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.scene-characters {
  display: flex;
  gap: 1.75rem;
  justify-content: center;
  flex-wrap: wrap;
}

.scene-char {
  text-align: center;
  background: rgba(6, 10, 20, 0.55);
  padding: 0.55rem 1rem 0.65rem;
  border-radius: 10px;
  border: 1px solid var(--sao-border-dim);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.scene-char img {
  width: 64px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid rgba(94, 207, 255, 0.35);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

.scene-char-name {
  color: #fff;
  font-size: 0.82rem;
  font-weight: 700;
  margin-top: 0.4rem;
}

.scene-char-action {
  color: var(--ok);
  font-size: 0.74rem;
  margin-top: 0.2rem;
}

.scene-char-action.fail {
  color: var(--bad);
}

.scene-labels {
  position: absolute;
  top: 0.85rem;
  left: 0.85rem;
  z-index: 8;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.scene-label {
  font-size: 0.62rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  padding: 0.2rem 0.45rem;
  border: 1px solid rgba(94, 207, 255, 0.2);
  color: var(--muted);
  background: rgba(6, 10, 20, 0.5);
  border-radius: 2px;
  transition: border-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease;
}

.scene-label.active {
  color: var(--sao-cyan);
  border-color: rgba(94, 207, 255, 0.55);
  box-shadow: 0 0 12px rgba(94, 207, 255, 0.2);
}

.shake {
  animation: sceneShake 0.22s ease;
}

@keyframes sceneShake {
  0%, 100% { transform: translate(0, 0); }
  20% { transform: translate(2px, -1px); }
  40% { transform: translate(-2px, 1px); }
  60% { transform: translate(2px, 1px); }
  80% { transform: translate(-1px, -1px); }
}

@media (prefers-reduced-motion: reduce) {
  .scene-title {
    animation: none;
  }

  .scene-bg-base,
  .scene-bg-glow,
  .scene-bg-silhouette {
    transition: none;
  }

  .shake {
    animation: none;
  }
}
</style>
