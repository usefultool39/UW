<template>
  <aside class="quest-tracker" :class="{ guided: highlightPrimary }" role="status">
    <section class="quest-focus">
      <div class="quest-heading-row">
        <div>
          <div class="quest-rail-title">主线目标</div>
          <div class="quest-day">第 {{ simState?.day || 1 }} 天 · {{ primaryKindLabel }}</div>
        </div>
        <span class="quest-state">进行中</span>
      </div>
      <p class="quest-rail-body">{{ safeQuestGuide }}</p>
      <div v-if="routeHint" class="route-hint" aria-hidden="true">
        <span class="route-pulse"></span>
        <span>{{ uwCanonText(routeHint) }}</span>
      </div>
      <button
        v-if="primaryEvent"
        type="button"
        class="quest-primary-btn"
        :disabled="busy"
        @click="$emit('open-event', primaryEvent.id)"
      >
        前往：{{ uwCanonText(primaryEvent.title || '当前线索') }}
      </button>
      <button
        v-else-if="actionPreview.length"
        type="button"
        class="quest-primary-btn"
        :disabled="busy"
        @click="$emit('open-interact')"
      >
        打开附近互动
      </button>
    </section>


    <div v-if="actionPreview.length" class="nearby-actions">
      <div class="nearby-actions-head">
        <div class="nearby-actions-label">就在这里</div>
        <button type="button" class="nearby-enter-btn" :disabled="busy" @click="$emit('open-interact')">
          互动
        </button>
      </div>
      <button
        v-for="action in actionPreview"
        :key="action.id"
        type="button"
        class="nearby-action"
        :class="{ blocked: action.blocked }"
        :disabled="busy"
        @click="$emit('open-interact')"
      >
        <span>{{ action.label }}</span>
        <small v-if="action.meta">{{ action.meta }}</small>
      </button>
    </div>

    <div v-if="hasNearbyNpc" class="npc-prompt">
      <span>附近同伴</span>
      <strong>{{ safeNearbyNpcLabel }}</strong>
    </div>

    <div v-if="activeNpcIntents.length" class="npc-attention">
      <div class="npc-attention-label">同伴主动事件</div>
      <button
        v-for="intent in activeNpcIntents"
        :key="intent.id"
        type="button"
        class="npc-attention-btn"
        :disabled="busy"
        @click="$emit('open-interact')"
      >
        <strong>{{ intentTitle(intent) }}</strong>
        <small>{{ intentMeta(intent) }}</small>
      </button>
    </div>

    <Transition name="event-fade">
      <div v-if="secondaryEvents.length" class="event-strip">
        <div class="event-label">之后可追踪</div>
        <button
          v-for="event in secondaryEvents"
          :key="event.id"
          type="button"
          :disabled="busy"
          class="event-btn"
          @click="$emit('open-event', event.id)"
        >
          <span class="event-marker" aria-hidden="true"><span></span></span>
          <span class="event-copy">
            <span>{{ uwCanonText(event.title) }}</span>
            <small>{{ eventMeta(event) }}</small>
          </span>
        </button>
      </div>
    </Transition>

    <div class="tracker-meta">
      <span class="meta-chip place">
        <span class="chip-icon">地点</span>
        {{ safeNearbyInteractTitle }}
      </span>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { getAgentLabel, getSceneLabel } from '../field/gameContentConfig.js'
import { compactPlayerText, uwCanonText } from '../utils/uwCanonText.js'

const props = defineProps({
  simState: { type: Object, default: null },
  storyEvents: { type: Array, default: () => [] },
  questGuide: { type: String, default: '在村中探索，了解周围环境。' },
  nearbyNpcLabel: { type: String, default: '暂无 NPC' },
  nearbyInteractTitle: { type: String, default: '暂无地点' },
  nearbyActionPreview: { type: Array, default: () => [] },
  routeHint: { type: String, default: '' },
  highlightPrimary: { type: Boolean, default: false },
  busy: { type: Boolean, default: false }
})

defineEmits(['open-event', 'open-interact'])

const safeStoryEvents = computed(() => Array.isArray(props.storyEvents) ? props.storyEvents : [])
const primaryEvent = computed(() => safeStoryEvents.value[0] || null)
const secondaryEvents = computed(() => safeStoryEvents.value.slice(1, 2))
const actionPreview = computed(() =>
  (Array.isArray(props.nearbyActionPreview) ? props.nearbyActionPreview : [])
    .slice(0, 2)
    .map((action) => ({
      ...action,
      label: compactPlayerText(action.label, 34),
      meta: compactPlayerText(action.meta, 42)
    }))
)

const safeQuestGuide = computed(() => compactPlayerText(props.questGuide || '在村中探索，了解周围环境。', 88))
const safeNearbyNpcLabel = computed(() => uwCanonText(props.nearbyNpcLabel || '暂无 NPC'))
const safeNearbyInteractTitle = computed(() => uwCanonText(props.nearbyInteractTitle || '暂无地点'))
const hasNearbyNpc = computed(() => safeNearbyNpcLabel.value !== '暂无 NPC')

const activeNpcIntents = computed(() => {
  const player = props.simState?.player
  const px = Number(player?.tile_x)
  const py = Number(player?.tile_y)
  const sceneId = String(player?.scene_id || props.simState?.scene_id || '')
  if (!Number.isFinite(px) || !Number.isFinite(py)) return []
  return (Array.isArray(props.simState?.npc_intents) ? props.simState.npc_intents : [])
    .map((intent) => ({
      intent,
      sameScene: String(intent?.scene_id || '') === sceneId,
      distance: Math.max(Math.abs(Number(intent?.tile_x) - px), Math.abs(Number(intent?.tile_y) - py))
    }))
    .filter((item) => item.sameScene && Number.isFinite(item.distance))
    .sort((a, b) => Number(b.intent?.priority || 0) - Number(a.intent?.priority || 0))
    .slice(0, 1)
    .map((item) => item.intent)
})

const primaryKindLabel = computed(() => {
  const kind = String(primaryEvent.value?.kind || '')
  return ({ clue: '调查', training: '训练', anomaly: '异常', conflict: '抉择', final_choice: '关键选择' })[kind] || '村庄生活'
})


function intentTitle(intent) {
  return compactPlayerText(intent?.title || '同伴正在等你回应', 38)
}

function intentMeta(intent) {
  const agent = intent?.npc_id ? getAgentLabel(intent.npc_id) : '同伴'
  const scene = intent?.scene_id ? getSceneLabel(intent.scene_id) : ''
  const playerFacingReason = intent?.description || intent?.stakes?.[0] || '想和你确认一件事'
  return compactPlayerText([agent, scene, playerFacingReason].filter(Boolean).join(' · '), 58)
}

function eventMeta(event) {
  const scene = getSceneLabel(event?.location?.scene_id || '')
  return compactPlayerText(scene || '跟随金色标记', 32)
}
</script>

<style scoped>
.quest-tracker {
  position: absolute;
  z-index: 35;
  right: 0.8rem;
  top: 10.5rem;
  width: min(312px, calc(100% - 1.5rem));
  max-height: calc(100vh - 16.4rem);
  padding: 0.68rem;
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(4, 8, 18, 0.9), rgba(6, 12, 24, 0.76)),
    radial-gradient(circle at 0% 0%, rgba(246, 211, 110, 0.12), transparent 42%);
  border: 1px solid rgba(246, 211, 110, 0.24);
  box-shadow: 0 12px 26px rgba(0, 0, 0, 0.28), inset 3px 0 0 rgba(246, 211, 110, 0.56);
  pointer-events: auto;
  overflow: auto;
}

.quest-tracker.guided {
  border-color: rgba(253, 224, 71, 0.46);
  box-shadow:
    0 16px 34px rgba(0, 0, 0, 0.32),
    0 0 26px rgba(246, 211, 110, 0.12),
    inset 3px 0 0 rgba(246, 211, 110, 0.72);
}

.quest-focus {
  padding-bottom: 0.62rem;
  border-bottom: 1px solid rgba(255, 239, 198, 0.12);
}

.quest-rail-title {
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  color: var(--sao-gold);
  margin-bottom: 0.32rem;
  font-weight: 900;
}

.quest-rail-body {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.55;
  color: #f8fafc;
  opacity: 0.96;
}

.quest-primary-btn {
  width: 100%;
  min-height: 2.35rem;
  margin-top: 0.58rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 247, 214, 0.58);
  color: #2e2113;
  background: linear-gradient(180deg, #fff0b6, #d8913e);
  box-shadow: 0 0 18px rgba(246, 211, 110, 0.18);
  font-size: 0.8rem;
  font-weight: 900;
}

.quest-primary-btn:hover:not(:disabled) {
  box-shadow: 0 0 24px rgba(246, 211, 110, 0.26);
}

.quest-tracker.guided .quest-primary-btn {
  animation: quest-callout 1.75s ease-in-out infinite;
}

.route-hint {
  display: flex;
  align-items: center;
  gap: 0.38rem;
  margin-top: 0.48rem;
  padding: 0.36rem 0.42rem;
  border-radius: 6px;
  color: #dff7ff;
  background: rgba(14, 116, 144, 0.2);
  border: 1px solid rgba(125, 211, 252, 0.22);
  font-size: 0.64rem;
  line-height: 1.25;
  font-weight: 900;
}

.route-pulse {
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 50%;
  background: #fde047;
  box-shadow: 0 0 0 0 rgba(253, 224, 71, 0.45);
  animation: route-pulse 1.5s ease-out infinite;
  flex: 0 0 auto;
}

.guide-steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.28rem;
  margin-top: 0.56rem;
}

.guide-steps span {
  min-height: 1.62rem;
  display: grid;
  place-items: center;
  padding: 0.15rem 0.22rem;
  border-radius: 6px;
  color: #dbeafe;
  background: rgba(14, 116, 144, 0.22);
  border: 1px solid rgba(125, 211, 252, 0.18);
  font-size: 0.58rem;
  font-weight: 900;
  text-align: center;
}

.nearby-actions {
  margin-top: 0.6rem;
  display: grid;
  gap: 0.26rem;
}

.nearby-actions-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.nearby-actions-label {
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  color: var(--sao-gold);
  font-weight: 800;
}

.nearby-enter-btn {
  flex: 0 0 auto;
  min-height: 1.45rem;
  padding: 0.18rem 0.5rem;
  border-radius: 6px;
  border: 1px solid rgba(125, 211, 252, 0.32);
  background: rgba(14, 116, 144, 0.42);
  color: #dff7ff;
  font-size: 0.62rem;
  font-weight: 800;
  cursor: pointer;
}

.nearby-enter-btn:hover:not(:disabled) {
  border-color: rgba(246, 211, 110, 0.58);
  color: #fff7d6;
}

.nearby-enter-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nearby-action {
  width: 100%;
  padding: 0.32rem 0.42rem;
  border-radius: 6px;
  border: 1px solid rgba(125, 211, 252, 0.24);
  background: rgba(8, 21, 38, 0.78);
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.12rem;
  text-align: left;
  cursor: pointer;
}

.nearby-action:hover:not(:disabled) {
  border-color: rgba(246, 211, 110, 0.52);
  background: rgba(28, 38, 56, 0.86);
}

.nearby-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nearby-action.blocked {
  border-color: rgba(148, 163, 184, 0.15);
  background: rgba(15, 23, 42, 0.68);
}

.nearby-action span {
  font-size: 0.7rem;
  font-weight: 800;
  line-height: 1.25;
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.nearby-action small {
  color: #bae6fd;
  font-size: 0.6rem;
  line-height: 1.25;
}

.npc-prompt {
  margin-top: 0.44rem;
  padding: 0.36rem 0.44rem;
  border-radius: 6px;
  border: 1px solid rgba(246, 211, 110, 0.24);
  background: rgba(120, 83, 35, 0.18);
  display: grid;
  gap: 0.12rem;
}

.npc-prompt span {
  color: #fde68a;
  font-size: 0.58rem;
  font-weight: 900;
  letter-spacing: 0.1em;
}

.npc-prompt strong {
  color: #fff7d6;
  font-size: 0.72rem;
  line-height: 1.3;
}

.npc-attention {
  margin-top: 0.46rem;
  display: grid;
  gap: 0.3rem;
}

.npc-attention-label {
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  color: var(--sao-gold);
  font-weight: 800;
}

.npc-attention-btn {
  width: 100%;
  padding: 0.36rem 0.44rem;
  border-radius: 6px;
  border: 1px solid rgba(246, 211, 110, 0.22);
  background: rgba(35, 28, 18, 0.42);
  color: #fff7d6;
  cursor: pointer;
  text-align: left;
  display: grid;
  gap: 0.12rem;
}

.npc-attention-btn:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.58);
  background: rgba(56, 43, 24, 0.58);
}

.npc-attention-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.npc-attention-btn strong {
  font-size: 0.7rem;
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.npc-attention-btn small {
  color: #bae6fd;
  font-size: 0.6rem;
  line-height: 1.25;
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.event-strip {
  margin-top: 0.48rem;
}

.event-label {
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--sao-gold);
  margin-bottom: 0.35rem;
  font-weight: 700;
}

.event-btn {
  width: 100%;
  min-height: 1.78rem;
  padding: 0.32rem 0.44rem;
  border-radius: 6px;
  border: 1px solid rgba(246, 211, 110, 0.18);
  background:
    radial-gradient(circle at 8% 50%, rgba(253, 224, 71, 0.1), transparent 32%),
    rgba(26, 34, 48, 0.62);
  color: #fff7d6;
  font-size: 0.7rem;
  font-weight: 800;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
  margin-bottom: 0.32rem;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.12s ease;
  will-change: transform;
}

.event-btn:last-child {
  margin-bottom: 0;
}

.event-btn:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.58);
  box-shadow: 0 0 12px rgba(212, 175, 55, 0.14);
  transform: translateX(2px);
}

.event-btn:active:not(:disabled) {
  transform: translateX(0);
}

.event-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.event-marker {
  flex: 0 0 auto;
  width: 1.1rem;
  height: 1.1rem;
  border-radius: 50%;
  position: relative;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle, rgba(255, 247, 214, 0.58) 0 18%, rgba(251, 191, 36, 0.2) 19% 44%, transparent 45%),
    rgba(253, 224, 71, 0.1);
  border: 1px solid rgba(253, 224, 71, 0.76);
  box-shadow: 0 0 13px rgba(251, 191, 36, 0.32);
  animation: pulse-marker 1.6s ease-in-out infinite;
}

.event-copy {
  display: grid;
  gap: 0.12rem;
  min-width: 0;
}

.event-copy span {
  overflow-wrap: anywhere;
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.event-copy small {
  color: #bae6fd;
  font-size: 0.62rem;
  line-height: 1.25;
}

.event-marker span {
  width: 0.34rem;
  height: 0.34rem;
  border-radius: 50%;
  background: #fff7d6;
  box-shadow: 0 0 8px rgba(255, 247, 214, 0.7);
}

@keyframes pulse-marker {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.12); opacity: 0.8; }
}

@keyframes quest-callout {
  0%, 100% {
    box-shadow: 0 0 18px rgba(246, 211, 110, 0.18);
  }
  50% {
    box-shadow: 0 0 28px rgba(253, 224, 71, 0.36);
  }
}

@keyframes route-pulse {
  0% { box-shadow: 0 0 0 0 rgba(253, 224, 71, 0.45); }
  70% { box-shadow: 0 0 0 8px rgba(253, 224, 71, 0); }
  100% { box-shadow: 0 0 0 0 rgba(253, 224, 71, 0); }
}

.tracker-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.28rem;
  margin-top: 0.44rem;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.4rem;
  border-radius: 6px;
  color: #dbeafe;
  background: rgba(30, 64, 175, 0.28);
  border: 1px solid rgba(147, 197, 253, 0.18);
  font-size: 0.62rem;
  font-weight: 600;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chip-icon {
  font-size: 0.58rem;
  color: #93c5fd;
  letter-spacing: 0.04em;
}

/* Fade transition for event strip */
.event-fade-enter-active,
.event-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.event-fade-enter-from,
.event-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 900px) {
  .quest-tracker {
    position: absolute;
    left: 0.55rem;
    right: 0.55rem;
    top: auto;
    bottom: 8.65rem;
    width: auto;
    max-height: min(10.8rem, calc(100vh - 19rem));
    margin: 0;
    padding: 0.52rem 0.6rem;
  }

  .quest-rail-body {
    display: -webkit-box;
    overflow: hidden;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    font-size: 0.78rem;
  }

  .guide-steps {
    display: none;
  }

  .quest-primary-btn {
    min-height: 2rem;
    margin-top: 0.42rem;
  }
}
.quest-heading-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.6rem;
}
.quest-day {
  margin-top: 0.16rem;
  color: #bae6fd;
  font-size: 0.72rem;
  font-weight: 800;
}
.quest-state {
  padding: 0.18rem 0.42rem;
  border-radius: 999px;
  color: #d9f99d;
  background: rgba(101, 163, 13, 0.16);
  border: 1px solid rgba(163, 230, 53, 0.28);
  font-size: 0.68rem;
  font-weight: 900;
}
.reward-preview {
  display: grid;
  gap: 0.12rem;
  margin: 0.58rem 0;
  padding: 0.48rem 0.58rem;
  border-radius: 7px;
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(125, 211, 252, 0.16);
}
.reward-preview span { color: #7dd3fc; font-size: 0.66rem; font-weight: 900; }
.reward-preview strong { color: #e0f2fe; font-size: 0.78rem; line-height: 1.4; }

.daily-loop {
  margin: 0.55rem 0 0.62rem;
  padding: 0.5rem 0.58rem;
  border-radius: 7px;
  background: rgba(15, 23, 42, 0.48);
  border: 1px solid rgba(148, 163, 184, 0.14);
}
.daily-loop-head { display: flex; justify-content: space-between; color: #cbd5e1; font-size: 0.7rem; font-weight: 900; }
.daily-loop-head strong { color: #fde68a; }
.daily-loop-bar { height: 4px; margin: 0.38rem 0 0.42rem; border-radius: 99px; overflow: hidden; background: rgba(148, 163, 184, 0.16); }
.daily-loop-bar span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #38bdf8, #fde047); transition: width 0.3s ease; }
.daily-loop-items { display: grid; gap: 0.2rem; }
.daily-loop-items span { color: #94a3b8; font-size: 0.68rem; line-height: 1.3; }
.daily-loop-items span b { display: inline-block; width: 1rem; color: #64748b; }
.daily-loop-items span.done { color: #bbf7d0; text-decoration: line-through; text-decoration-color: rgba(187, 247, 208, 0.4); }
.daily-loop-items span.done b { color: #86efac; }

</style>

