<template>
  <aside class="quest-tracker" role="status">
    <div class="quest-rail-title">任务追踪</div>
    <p class="quest-rail-body">{{ safeQuestGuide }}</p>

    <div v-if="actionPreview.length" class="nearby-actions">
      <div class="nearby-actions-head">
        <div class="nearby-actions-label">可执行</div>
        <button
          type="button"
          class="nearby-enter-btn"
          :disabled="busy"
          @click="$emit('open-interact')"
        >
          进入
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
      <span>NPC 在附近</span>
      <strong>可以交谈</strong>
    </div>

    <div v-if="activeNpcIntents.length" class="npc-attention">
      <div class="npc-attention-label">NPC 关注</div>
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
      <div v-if="safeStoryEvents.length" class="event-strip">
        <div class="event-label">当前线索</div>
        <button
          v-for="event in safeStoryEvents"
          :key="event.id"
          type="button"
          :disabled="busy"
          class="event-btn"
          @click="$emit('open-event', event.id)"
        >
          <span class="event-marker" aria-hidden="true"><span></span></span>
          <span class="event-copy">
            <span>{{ canonText(event.title) }}</span>
            <small>{{ eventMeta(event) }}</small>
          </span>
        </button>
      </div>
    </Transition>

    <div class="tracker-meta">
      <span class="meta-chip">
        <span class="chip-icon">附近</span>
        {{ safeNearbyNpcLabel }}
      </span>
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

const props = defineProps({
  simState: { type: Object, default: null },
  storyEvents: { type: Array, default: () => [] },
  questGuide: { type: String, default: '在村中探索，了解周围环境。' },
  nearbyNpcLabel: { type: String, default: '暂无 NPC' },
  nearbyInteractTitle: { type: String, default: '暂无地点' },
  nearbyActionPreview: { type: Array, default: () => [] },
  busy: { type: Boolean, default: false }
})

defineEmits(['open-event', 'open-interact'])

function canonText(value) {
  return String(value || '')
    .replaceAll('艾琳', '爱丽丝')
    .replaceAll('尤里', '悠吉欧')
    .replaceAll('凛斗', 'Kirito')
}

const actionPreview = computed(() =>
  (Array.isArray(props.nearbyActionPreview) ? props.nearbyActionPreview : [])
    .map((action) => ({
      ...action,
      label: canonText(action.label),
      meta: canonText(action.meta)
    }))
)

const safeStoryEvents = computed(() =>
  Array.isArray(props.storyEvents) ? props.storyEvents : []
)

const safeQuestGuide = computed(() => canonText(props.questGuide || '在村中探索，了解周围环境。'))
const safeNearbyNpcLabel = computed(() => canonText(props.nearbyNpcLabel || '暂无 NPC'))
const safeNearbyInteractTitle = computed(() => canonText(props.nearbyInteractTitle || '暂无地点'))
const hasNearbyNpc = computed(() => safeNearbyNpcLabel.value !== '暂无 NPC')
const activeNpcIntents = computed(() =>
  (Array.isArray(props.simState?.npc_intents) ? props.simState.npc_intents : [])
    .slice()
    .sort((a, b) => Number(b?.priority || 0) - Number(a?.priority || 0))
    .slice(0, 2)
)

function intentTitle(intent) {
  return canonText(intent?.title || '同伴正在等你回应')
}

function intentMeta(intent) {
  const agent = canonText(intent?.npc_id ? getAgentLabel(intent.npc_id) : 'NPC')
  const scene = intent?.scene_id ? getSceneLabel(intent.scene_id) : ''
  return canonText([agent, scene, intent?.reason || '主动邀约'].filter(Boolean).join(' · '))
}

function eventMeta(event) {
  const scene = getSceneLabel(event?.location?.scene_id || '')
  const day = event?.day || event?.trigger?.day_min || ''
  return canonText([scene, day ? `Day ${day}` : '靠近金色标记'].filter(Boolean).join(' · '))
}
</script>

<style scoped>
.quest-tracker {
  position: absolute;
  z-index: 35;
  right: 0.8rem;
  top: 11.6rem;
  width: min(252px, calc(100% - 1.5rem));
  max-height: calc(100vh - 17.2rem);
  padding: 0.56rem 0.62rem;
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(5, 10, 18, 0.82), rgba(5, 10, 18, 0.6)),
    rgba(6, 12, 24, 0.56);
  border: 1px solid rgba(125, 211, 252, 0.18);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.22), inset 2px 0 0 rgba(246, 211, 110, 0.48);
  pointer-events: auto;
  overflow: auto;
}

.quest-rail-title {
  font-size: 0.58rem;
  letter-spacing: 0.12em;
  color: var(--sao-gold);
  margin-bottom: 0.26rem;
  font-weight: 700;
}

.quest-rail-body {
  margin: 0;
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  font-size: 0.76rem;
  line-height: 1.45;
  color: #f8fafc;
  opacity: 0.9;
}

.nearby-actions {
  margin-top: 0.48rem;
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
  }
}
</style>

