<template>
  <div
    v-show="modelValue"
    class="meal-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="close"
  >
    <section class="meal-panel" @click.stop>
      <header class="meal-header">
        <div>
          <p class="meal-kicker">关系选择</p>
          <h3>{{ activity?.title || '餐桌分歧' }}</h3>
        </div>
        <button type="button" class="meal-close" aria-label="关闭" @click="close">×</button>
      </header>

      <p class="meal-desc">
        这不是正确答案选择。你偏向谁、保留什么沉默，都会进入今天的关系和记忆。
      </p>

      <div class="meal-options">
        <button
          v-for="choice in options"
          :key="choice.id"
          type="button"
          class="meal-option"
          :class="{ selected: selectedId === choice.id }"
          :disabled="busy"
          @click="selectedId = choice.id"
        >
          <span>{{ choice.label }}</span>
          <small>{{ choice.hint }}</small>
        </button>
      </div>

      <section class="meal-preview">
        <strong>{{ selectedChoice?.label || '选择一个态度' }}</strong>
        <p>{{ selectedChoice?.hint || '偏向、沉默和缓和，都会被 NPC 以不同方式记住。' }}</p>
      </section>

      <footer class="meal-actions">
        <button type="button" class="ghost" :disabled="busy" @click="close">稍后再说</button>
        <button type="button" :disabled="busy || !selectedChoice" @click="finish">
          确认态度
        </button>
      </footer>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  activity: { type: Object, default: null },
  busy: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'complete'])

const selectedId = ref('')

const fallbackOptions = computed(() => {
  const id = props.activity?.id || props.activity?.activity_id || ''
  if (id === 'home_evening_meal') {
    return [
      { id: 'side_alice', label: '偏向爱丽丝：先守住禁忌目录', hint: '降低当晚风险，但尤吉欧会觉得调查被放慢。' },
      { id: 'side_eugeo', label: '偏向尤吉欧：明天再确认静默线', hint: '推进调查，但爱丽丝会更担心。' },
      { id: 'keep_table_calm', label: '保持沉默，把话题拉回日常', hint: '缓和当下气氛，同时保留观察空间。' }
    ]
  }
  return [
    { id: 'support_alice', label: '帮爱丽丝把篮子重新扎紧', hint: '让她知道你愿意照看这些细节。' },
    { id: 'support_eugeo', label: '给尤吉欧多留一份干粮', hint: '把巨神树伐木场的消耗放在前面。' },
    { id: 'quiet_observe', label: '保持沉默，观察两人的习惯', hint: '少表态，多记住他们的日常分工。' }
  ]
})

const options = computed(() => {
  const raw = Array.isArray(props.activity?.choices) ? props.activity.choices : []
  const cleaned = raw
    .map((choice) => ({
      id: choice?.id || '',
      label: choice?.label || '',
      hint: choice?.hint || ''
    }))
    .filter((choice) => choice.id && choice.label)
  return cleaned.length ? cleaned : fallbackOptions.value
})

const selectedChoice = computed(() =>
  options.value.find((choice) => choice.id === selectedId.value) || null
)

function close() {
  if (props.busy) return
  emit('update:modelValue', false)
}

function finish() {
  if (props.busy || !selectedChoice.value) return
  emit('complete', {
    choice_id: selectedChoice.value.id,
    result: {
      label: selectedChoice.value.label,
      text: selectedChoice.value.hint
    }
  })
}

watch(() => props.modelValue, (open) => {
  if (open) selectedId.value = options.value[0]?.id || ''
})
</script>

<style scoped>
.meal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 88;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(4, 8, 18, 0.78);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.meal-panel {
  width: min(94vw, 760px);
  max-height: min(88vh, 700px);
  overflow: auto;
  padding: 1.18rem;
  border-radius: 14px;
  color: #f8fafc;
  background: linear-gradient(165deg, rgba(32, 37, 48, 0.98), rgba(8, 12, 22, 0.98));
  border: 1px solid rgba(246, 211, 110, 0.34);
  box-shadow: 0 26px 68px rgba(0, 0, 0, 0.56), 0 0 26px rgba(246, 211, 110, 0.1);
}

.meal-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding-bottom: 0.72rem;
  border-bottom: 1px solid rgba(246, 211, 110, 0.18);
}

.meal-kicker {
  margin: 0 0 0.16rem;
  color: var(--sao-gold);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.meal-header h3 {
  margin: 0;
  color: #fff7d6;
  font-size: 1.34rem;
}

.meal-close {
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(51, 65, 85, 0.6);
  color: #e2e8f0;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}

.meal-desc {
  margin: 0.82rem 0 0.9rem;
  color: #dbeafe;
  font-size: 0.98rem;
  line-height: 1.6;
}

.meal-options {
  display: grid;
  gap: 0.52rem;
}

.meal-option {
  min-height: 4.6rem;
  padding: 0.68rem 0.72rem;
  border-radius: 9px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.66);
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 0.24rem;
  text-align: left;
  cursor: pointer;
}

.meal-option:hover:not(:disabled) {
  border-color: rgba(246, 211, 110, 0.56);
  background: rgba(28, 38, 56, 0.88);
}

.meal-option.selected {
  border-color: rgba(246, 211, 110, 0.76);
  background: rgba(120, 83, 35, 0.44);
  box-shadow: 0 0 16px rgba(246, 211, 110, 0.12);
}

.meal-option span {
  color: #fff7d6;
  font-size: 0.95rem;
  font-weight: 900;
}

.meal-option small {
  color: #bae6fd;
  font-size: 0.78rem;
  line-height: 1.38;
}

.meal-preview {
  margin-top: 0.78rem;
  padding: 0.66rem 0.72rem;
  border-radius: 9px;
  border: 1px solid rgba(246, 211, 110, 0.22);
  background: rgba(6, 12, 24, 0.58);
}

.meal-preview strong {
  color: #fff7d6;
  font-size: 0.96rem;
}

.meal-preview p {
  margin: 0.25rem 0 0;
  color: #dbeafe;
  font-size: 0.9rem;
  line-height: 1.48;
}

.meal-actions {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 0.55rem;
  margin-top: 0.9rem;
}

.meal-actions button {
  min-height: 2.7rem;
  border-radius: 9px;
  border: 1px solid rgba(246, 211, 110, 0.36);
  color: #fff7d6;
  background: linear-gradient(180deg, rgba(120, 83, 35, 0.96), rgba(48, 37, 24, 0.98));
  font-weight: 900;
  cursor: pointer;
}

.meal-actions .ghost {
  color: #dbeafe;
  background: rgba(15, 23, 42, 0.72);
  border-color: rgba(125, 211, 252, 0.26);
}

.meal-actions button:disabled {
  opacity: 0.48;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .meal-actions {
    grid-template-columns: 1fr;
  }
}
</style>

