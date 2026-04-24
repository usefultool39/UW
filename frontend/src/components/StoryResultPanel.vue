<template>
  <div
    v-show="modelValue && result"
    class="result-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="emit('update:modelValue', false)"
  >
    <section class="result-panel" @click.stop>
      <header class="result-header">
        <div>
          <p class="result-kicker">{{ result?.ending_id ? '章节收束' : '选择结果' }}</p>
          <h3>{{ resultTitle }}</h3>
        </div>
        <button
          type="button"
          class="result-close"
          aria-label="关闭"
          @click="emit('update:modelValue', false)"
        >
          ×
        </button>
      </header>

      <p class="result-text">{{ resultText }}</p>

      <section v-if="relationshipLines.length" class="result-section">
        <h4>关系变化</h4>
        <ul>
          <li v-for="line in relationshipLines" :key="line">{{ line }}</li>
        </ul>
      </section>

      <section v-if="memoryLines.length" class="result-section">
        <h4>被记住的事</h4>
        <ul>
          <li v-for="line in memoryLines" :key="line">{{ line }}</li>
        </ul>
      </section>

      <button type="button" class="result-primary" @click="emit('update:modelValue', false)">
        继续行动
      </button>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getAgentLabel } from '../field/gameContentConfig.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  result: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue'])

const FIELD_LABELS = {
  affinity: '好感',
  trust: '信任',
  tension: '紧张'
}

const resultTitle = computed(() => {
  const choice = props.result?.choice?.label
  const eventTitle = props.result?.event?.title || props.result?.event_title
  if (choice && eventTitle) return `${eventTitle} · ${choice}`
  return choice || eventTitle || '这件事留下了痕迹'
})

const resultText = computed(() =>
  props.result?.choice?.result_text || props.result?.result_text || '选择已经写入今天的旅程。'
)

const relationshipLines = computed(() => {
  const changes = Array.isArray(props.result?.relationship_changes)
    ? props.result.relationship_changes
    : []
  return changes
    .filter((item) => Number(item?.delta || 0) !== 0)
    .map((item) => {
      const name = getAgentLabel(item.npc_id)
      const field = FIELD_LABELS[item.field] || item.field
      const delta = Number(item.delta || 0)
      const sign = delta > 0 ? '+' : ''
      return `${name}的${field} ${sign}${delta}，现在是 ${item.after}`
    })
})

const memoryLines = computed(() => {
  const memories = Array.isArray(props.result?.memory_written) ? props.result.memory_written : []
  return memories
    .filter((item) => item?.summary)
    .map((item) => `${getAgentLabel(item.npc_id)}记住了：${item.summary}`)
})
</script>

<style scoped>
.result-backdrop {
  position: fixed;
  inset: 0;
  z-index: 89;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(4, 8, 18, 0.78);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.result-panel {
  width: min(94vw, 620px);
  max-height: min(88vh, 640px);
  overflow: auto;
  padding: 1rem;
  border-radius: 12px;
  background: linear-gradient(165deg, rgba(30, 43, 62, 0.98), rgba(8, 12, 22, 0.98));
  border: 1px solid rgba(246, 211, 110, 0.36);
  box-shadow: 0 26px 68px rgba(0, 0, 0, 0.56), 0 0 28px rgba(246, 211, 110, 0.12);
}

.result-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(246, 211, 110, 0.18);
}

.result-kicker {
  margin: 0 0 0.16rem;
  font-size: 0.62rem;
  color: var(--sao-gold);
  letter-spacing: 0.14em;
  font-weight: 800;
}

.result-header h3 {
  margin: 0;
  font-size: 1.14rem;
  color: #fff7d6;
  line-height: 1.35;
}

.result-close {
  flex: 0 0 auto;
  width: 2rem;
  height: 2rem;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(51, 65, 85, 0.6);
  color: #e2e8f0;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}

.result-text {
  margin: 0.85rem 0;
  color: #f8fafc;
  line-height: 1.68;
  font-size: 0.92rem;
}

.result-section {
  margin-top: 0.78rem;
  padding: 0.65rem 0.7rem;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.result-section h4 {
  margin: 0 0 0.35rem;
  font-size: 0.76rem;
  color: var(--sao-cyan);
}

.result-section ul {
  margin: 0;
  padding-left: 1rem;
  color: #e2e8f0;
  font-size: 0.8rem;
  line-height: 1.6;
}

.result-primary {
  width: 100%;
  margin-top: 0.9rem;
  min-height: 2.45rem;
  border-radius: 10px;
  color: #fff7d6;
  font-weight: 800;
  border: 1px solid rgba(246, 211, 110, 0.42);
  background: linear-gradient(180deg, rgba(120, 83, 35, 0.96), rgba(48, 37, 24, 0.98));
  cursor: pointer;
}

.result-primary:hover {
  border-color: rgba(253, 224, 71, 0.78);
  box-shadow: 0 0 18px rgba(212, 175, 55, 0.22);
}
</style>
