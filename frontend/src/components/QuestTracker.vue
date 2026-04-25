<template>
  <aside class="quest-tracker" role="status">
    <div class="quest-rail-title">当前目标</div>
    <p class="quest-rail-body">{{ questGuide }}</p>

    <div v-if="actionPreview.length" class="nearby-actions">
      <div class="nearby-actions-label">附近行动</div>
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

    <Transition name="event-fade">
      <div v-if="storyEvents.length" class="event-strip">
        <div class="event-label">章节事件</div>
        <button
          v-for="event in storyEvents"
          :key="event.id"
          type="button"
          :disabled="busy"
          class="event-btn"
          @click="$emit('open-event', event.id)"
        >
          <span class="event-marker">!</span>
          <span>{{ event.title }}</span>
        </button>
      </div>
    </Transition>

    <div class="tracker-meta">
      <span class="meta-chip">
        <span class="chip-icon">📍</span>
        {{ nearbyNpcLabel }}
      </span>
      <span class="meta-chip place">
        <span class="chip-icon">◎</span>
        {{ nearbyInteractTitle }}
      </span>
      <span class="meta-chip node">{{ simState?.story_node_id || 'mq00_tutorial' }}</span>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'

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

const actionPreview = computed(() =>
  Array.isArray(props.nearbyActionPreview) ? props.nearbyActionPreview : []
)
</script>

<style scoped>
.quest-tracker {
  position: absolute;
  z-index: 3;
  right: 0.75rem;
  top: 13.25rem;
  width: min(300px, calc(100% - 1.5rem));
  padding: 0.68rem 0.75rem;
  border-radius: 10px;
  background: rgba(6, 12, 24, 0.8);
  border: 1px solid rgba(94, 207, 255, 0.22);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.32);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  pointer-events: auto;
}

.quest-rail-title {
  font-size: 0.62rem;
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

.nearby-actions {
  margin-top: 0.65rem;
  display: grid;
  gap: 0.35rem;
}

.nearby-actions-label {
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  color: var(--sao-gold);
  font-weight: 800;
}

.nearby-action {
  width: 100%;
  padding: 0.38rem 0.5rem;
  border-radius: 8px;
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
  font-size: 0.72rem;
  font-weight: 800;
  line-height: 1.35;
}

.nearby-action small {
  color: #bae6fd;
  font-size: 0.62rem;
  line-height: 1.35;
}

.event-strip {
  margin-top: 0.6rem;
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
  min-height: 1.85rem;
  padding: 0.34rem 0.5rem;
  border-radius: 8px;
  border: 1px solid rgba(246, 211, 110, 0.28);
  background: rgba(78, 56, 25, 0.72);
  color: #fff7d6;
  font-size: 0.72rem;
  font-weight: 800;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin-bottom: 0.32rem;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.12s ease;
  will-change: transform;
}

.event-btn:last-child {
  margin-bottom: 0;
}

.event-btn:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.78);
  box-shadow: 0 0 14px rgba(212, 175, 55, 0.2);
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
  background: rgba(253, 224, 71, 0.85);
  color: #1f2937;
  font-size: 0.72rem;
  font-weight: 900;
  display: grid;
  place-items: center;
  animation: pulse-marker 1.6s ease-in-out infinite;
}

@keyframes pulse-marker {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.12); opacity: 0.8; }
}

.tracker-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.55rem;
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.4rem;
  border-radius: 999px;
  color: #dbeafe;
  background: rgba(30, 64, 175, 0.28);
  border: 1px solid rgba(147, 197, 253, 0.18);
  font-size: 0.66rem;
  font-weight: 600;
}

.meta-chip.node {
  font-family: monospace;
  font-size: 0.62rem;
  color: var(--muted);
  background: rgba(15, 23, 42, 0.6);
  border-color: rgba(94, 207, 255, 0.15);
}

.chip-icon {
  font-size: 0.7rem;
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
    position: relative;
    top: auto;
    right: auto;
    width: auto;
    margin: 0.45rem 0.55rem 4.75rem;
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
