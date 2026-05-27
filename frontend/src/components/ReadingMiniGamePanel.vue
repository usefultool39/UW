<template>
  <div
    v-show="modelValue"
    class="reading-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="close"
  >
    <section class="reading-panel" @click.stop>
      <header class="reading-header">
        <div>
          <p class="reading-kicker">书库调查</p>
          <h3>{{ activity?.title || '拼接旧记录' }}</h3>
        </div>
        <button type="button" class="reading-close" aria-label="关闭" @click="close">×</button>
      </header>

      <p class="reading-desc">
        从旧书页里挑出 3 个关键词，拼成你愿意带出书库的线索。
      </p>

      <div class="keyword-grid">
        <button
          v-for="keyword in keywords"
          :key="keyword.id"
          type="button"
          class="keyword-chip"
          :class="{ selected: selectedIds.includes(keyword.id) }"
          :disabled="busy || (!selectedIds.includes(keyword.id) && selectedIds.length >= maxPicked)"
          @click="toggleKeyword(keyword.id)"
        >
          <span>{{ keyword.label }}</span>
          <small>{{ keyword.note }}</small>
        </button>
      </div>

      <div class="reading-thread">
        <span v-for="slot in selectedSlots" :key="slot.key" :class="{ empty: !slot.label }">
          {{ slot.label || '待选择' }}
        </span>
      </div>

      <section class="reading-interpretation">
        <strong>{{ interpretation.label }}</strong>
        <p>{{ interpretation.text }}</p>
      </section>

      <footer class="reading-actions">
        <button type="button" class="ghost" :disabled="busy || !selectedIds.length" @click="reset">
          重选
        </button>
        <button type="button" :disabled="busy || !canFinish" @click="finish">
          记下这条线索
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

const maxPicked = 3
const selectedIds = ref([])

const keywords = [
  { id: 'bird_silence', label: '鸟声消失', note: '边界附近最反常的感官线索' },
  { id: 'silent_line', label: '静默线', note: '旧记录里被反复涂改的词' },
  { id: 'north_law', label: '北境律令', note: '村民不愿多谈的规则名' },
  { id: 'ancient_tree', label: '古誓树', note: '清场日常和边界传闻的交点' },
  { id: 'village_record', label: '村史断页', note: '年份缺了一段的旧纸' },
  { id: 'blank_margin', label: '空白注记', note: '像被人故意留下的空处' }
]

const canFinish = computed(() => selectedIds.value.length === maxPicked)

const selectedSlots = computed(() =>
  Array.from({ length: maxPicked }, (_, index) => {
    const id = selectedIds.value[index]
    const keyword = keywords.find((item) => item.id === id)
    return { key: `${index}:${id || 'empty'}`, label: keyword?.label || '' }
  })
)

const interpretation = computed(() => {
  const set = new Set(selectedIds.value)
  if (set.has('bird_silence') && set.has('silent_line') && set.has('north_law')) {
    return {
      id: 'trace_silence',
      label: '异常线索完整',
      text: '你把鸟声、静默线和北境律令拼成同一个问题。'
    }
  }
  if (set.has('ancient_tree') && set.has('north_law') && set.has('village_record')) {
    return {
      id: 'map_boundary',
      label: '边界规则偏重',
      text: '你更倾向先确认村史和清场日常之间的关系。'
    }
  }
  return {
    id: 'quiet_observe',
    label: selectedIds.value.length ? '保留疑问' : '等待关键词',
    text: selectedIds.value.length
      ? '这组词还没有变成答案，但足够让你继续观察艾琳和村子的反应。'
      : '先从纸页里挑出 3 个最刺眼的词。'
  }
})

function toggleKeyword(id) {
  if (props.busy) return
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter((item) => item !== id)
    return
  }
  if (selectedIds.value.length >= maxPicked) return
  selectedIds.value = [...selectedIds.value, id]
}

function reset() {
  selectedIds.value = []
}

function close() {
  if (props.busy) return
  emit('update:modelValue', false)
}

function finish() {
  if (props.busy || !canFinish.value) return
  emit('complete', {
    choice_id: interpretation.value.id,
    result: {
      label: interpretation.value.label,
      keywords: selectedSlots.value.map((slot) => slot.label).filter(Boolean),
      text: interpretation.value.text
    }
  })
}

watch(() => props.modelValue, (open) => {
  if (open) reset()
})
</script>

<style scoped>
.reading-backdrop {
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

.reading-panel {
  width: min(94vw, 780px);
  max-height: min(88vh, 720px);
  overflow: auto;
  padding: 1.18rem;
  border-radius: 14px;
  color: #f8fafc;
  background: linear-gradient(165deg, rgba(25, 39, 54, 0.98), rgba(8, 12, 22, 0.98));
  border: 1px solid rgba(125, 211, 252, 0.34);
  box-shadow: 0 26px 68px rgba(0, 0, 0, 0.56), 0 0 26px rgba(125, 211, 252, 0.1);
}

.reading-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding-bottom: 0.72rem;
  border-bottom: 1px solid rgba(125, 211, 252, 0.18);
}

.reading-kicker {
  margin: 0 0 0.16rem;
  color: #bae6fd;
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.reading-header h3 {
  margin: 0;
  color: #fff7d6;
  font-size: 1.34rem;
}

.reading-close {
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

.reading-desc {
  margin: 0.82rem 0 0.9rem;
  color: #dbeafe;
  font-size: 0.98rem;
  line-height: 1.6;
}

.keyword-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.52rem;
}

.keyword-chip {
  min-height: 5.2rem;
  padding: 0.62rem;
  border-radius: 9px;
  border: 1px solid rgba(125, 211, 252, 0.2);
  background: rgba(15, 23, 42, 0.66);
  color: #e2e8f0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 0.24rem;
  text-align: left;
}

.keyword-chip:hover:not(:disabled) {
  border-color: rgba(246, 211, 110, 0.54);
  background: rgba(28, 38, 56, 0.88);
}

.keyword-chip.selected {
  border-color: rgba(246, 211, 110, 0.76);
  background: rgba(120, 83, 35, 0.44);
  box-shadow: 0 0 16px rgba(246, 211, 110, 0.12);
}

.keyword-chip:disabled {
  opacity: 0.52;
  cursor: not-allowed;
}

.keyword-chip span {
  color: #fff7d6;
  font-size: 0.94rem;
  font-weight: 900;
}

.keyword-chip small {
  color: #bae6fd;
  font-size: 0.76rem;
  line-height: 1.35;
}

.reading-thread {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.45rem;
  margin-top: 0.78rem;
}

.reading-thread span {
  min-height: 2.35rem;
  display: grid;
  place-items: center;
  border-radius: 8px;
  color: #fff7d6;
  font-size: 0.86rem;
  font-weight: 900;
  background: rgba(120, 83, 35, 0.28);
  border: 1px solid rgba(246, 211, 110, 0.28);
}

.reading-thread .empty {
  color: #94a3b8;
  background: rgba(15, 23, 42, 0.62);
  border-color: rgba(148, 163, 184, 0.16);
}

.reading-interpretation {
  margin-top: 0.78rem;
  padding: 0.66rem 0.72rem;
  border-radius: 9px;
  border: 1px solid rgba(125, 211, 252, 0.22);
  background: rgba(6, 12, 24, 0.58);
}

.reading-interpretation strong {
  color: #fff7d6;
  font-size: 0.96rem;
}

.reading-interpretation p {
  margin: 0.25rem 0 0;
  color: #dbeafe;
  font-size: 0.9rem;
  line-height: 1.48;
}

.reading-actions {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 0.55rem;
  margin-top: 0.9rem;
}

.reading-actions button {
  min-height: 2.7rem;
  border-radius: 9px;
  border: 1px solid rgba(246, 211, 110, 0.36);
  color: #fff7d6;
  background: linear-gradient(180deg, rgba(120, 83, 35, 0.96), rgba(48, 37, 24, 0.98));
  font-weight: 900;
  cursor: pointer;
}

.reading-actions .ghost {
  color: #dbeafe;
  background: rgba(15, 23, 42, 0.72);
  border-color: rgba(125, 211, 252, 0.26);
}

.reading-actions button:disabled {
  opacity: 0.48;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .keyword-grid,
  .reading-thread,
  .reading-actions {
    grid-template-columns: 1fr;
  }
}
</style>

