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
          <div v-if="choicePreview(choice).length" class="choice-preview">
            <small v-for="item in choicePreview(choice)" :key="item">{{ item }}</small>
          </div>
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

const FIELD_LABELS = {
  affinity: '好感',
  trust: '信任',
  tension: '紧张'
}

function relationshipPreviewText(relationship) {
  const rel = relationship && typeof relationship === 'object' ? relationship : {}
  return Object.entries(rel)
    .map(([path, value]) => {
      const [npcId, fieldId] = String(path).split('.')
      const delta = Number(value || 0)
      if (!npcId || !fieldId || !Number.isFinite(delta) || delta === 0) return ''
      const sign = delta > 0 ? '+' : ''
      return `${getAgentLabel(npcId)} ${FIELD_LABELS[fieldId] || fieldId} ${sign}${delta}`
    })
    .filter(Boolean)
}

function choicePreview(choice) {
  const preview = choice?.preview || {}
  const lines = []
  const remembered = Array.isArray(preview.remembered_by) ? preview.remembered_by : []
  const promises = Array.isArray(preview.promises) ? preview.promises : []
  const tensions = Array.isArray(preview.tensions) ? preview.tensions : []
  const consequences = Array.isArray(preview.consequences) ? preview.consequences : []
  if (remembered.length) lines.push(`${remembered.map(getAgentLabel).join('、')}会记住`)
  lines.push(...relationshipPreviewText(preview.relationship).slice(0, 3))
  if (promises.length) lines.push(`${promises.map(getAgentLabel).join('、')}会留下承诺`)
  if (tensions.length) lines.push(`${tensions.map(getAgentLabel).join('、')}会留下不安`)
  lines.push(...consequences.slice(0, 2))
  if (preview.ending_id) lines.push('可能收束章节')
  if (!lines.length) lines.push('这个选择会影响后续回应')
  return lines.slice(0, 5)
}
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
  animation: modal-backdrop-in 0.18s ease-out both;
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
  animation: modal-rise-in 0.22s ease-out both;
}

@keyframes modal-backdrop-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modal-rise-in {
  from {
    opacity: 0;
    transform: translateY(16px) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
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

.choice-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 0.32rem;
  margin-top: 0.62rem;
}

.choice-preview small {
  padding: 0.2rem 0.42rem;
  border-radius: 999px;
  color: #fff7d6;
  background: rgba(120, 83, 35, 0.34);
  border: 1px solid rgba(246, 211, 110, 0.22);
  font-size: 0.72rem;
  font-weight: 800;
}

.event-choice:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
