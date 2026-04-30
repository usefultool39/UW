<template>
  <div
    v-show="modelValue && event"
    class="event-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="emit('update:modelValue', false)"
  >
    <section class="event-panel" @click.stop>
      <header class="event-header">
        <div>
          <p class="event-kicker">章节事件</p>
          <h3>{{ event?.title }}</h3>
        </div>
        <button
          type="button"
          class="event-close"
          aria-label="关闭"
          @click="emit('update:modelValue', false)"
        >
          ×
        </button>
      </header>

      <p class="event-desc">{{ event?.description }}</p>

      <div class="event-meta">
        <span v-if="event?.location?.scene_id">{{ sceneLabel }}</span>
        <span v-if="participantLabel">参与：{{ participantLabel }}</span>
      </div>

      <div class="event-choices">
        <button
          v-for="choice in event?.choices || []"
          :key="choice.id"
          type="button"
          :disabled="busy"
          class="event-choice"
          @click="emit('choose', choice)"
        >
          <strong>{{ choice.label }}</strong>
          <span v-if="choice.hint">{{ choice.hint }}</span>
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getAgentLabel, getSceneLabel } from '../field/gameContentConfig.js'

const props = defineProps({
  event: { type: Object, default: null },
  modelValue: { type: Boolean, default: false },
  busy: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'choose'])

const sceneLabel = computed(() => getSceneLabel(props.event?.location?.scene_id))
const participantLabel = computed(() => {
  const participants = Array.isArray(props.event?.participants) ? props.event.participants : []
  return participants.map((id) => getAgentLabel(id)).join('、')
})
</script>

<style scoped>
.event-backdrop {
  position: fixed;
  inset: 0;
  z-index: 86;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(4, 8, 18, 0.78);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.event-panel {
  width: min(94vw, 800px);
  max-height: min(88vh, 720px);
  overflow: auto;
  padding: 1.25rem;
  border-radius: 16px;
  background: linear-gradient(165deg, rgba(27, 38, 58, 0.97), rgba(8, 12, 22, 0.98));
  border: 1px solid rgba(246, 211, 110, 0.34);
  box-shadow: 0 26px 68px rgba(0, 0, 0, 0.56), 0 0 26px rgba(246, 211, 110, 0.1);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(246, 211, 110, 0.18);
}

.event-kicker {
  margin: 0 0 0.16rem;
  font-size: 0.62rem;
  color: var(--sao-gold);
  letter-spacing: 0.14em;
  font-weight: 800;
}

.event-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #fff7d6;
}

.event-close {
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(51, 65, 85, 0.6);
  color: #e2e8f0;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}

.event-desc {
  margin: 0.85rem 0;
  color: #e2e8f0;
  line-height: 1.65;
  font-size: 1.04rem;
}

.event-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-bottom: 0.8rem;
}

.event-meta span {
  padding: 0.22rem 0.45rem;
  border-radius: 999px;
  background: rgba(30, 64, 175, 0.24);
  border: 1px solid rgba(147, 197, 253, 0.18);
  color: #dbeafe;
  font-size: 0.82rem;
}

.event-choices {
  display: grid;
  gap: 0.55rem;
}

.event-choice {
  text-align: left;
  padding: 0.9rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(246, 211, 110, 0.26);
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  cursor: pointer;
}

.event-choice:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.72);
  box-shadow: 0 0 18px rgba(212, 175, 55, 0.2);
}

.event-choice strong,
.event-choice span {
  display: block;
}

.event-choice strong {
  font-size: 1.02rem;
}

.event-choice span {
  margin-top: 0.28rem;
  color: #cbd5e1;
  font-size: 0.9rem;
  line-height: 1.55;
}

.event-choice:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
