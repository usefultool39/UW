<template>
  <div
    v-show="modelValue && event"
    class="verdict-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="close"
  >
    <section class="verdict-panel" @click.stop>
      <header class="verdict-header">
        <div>
          <p class="verdict-kicker">边界判定</p>
          <h3>{{ event?.title || '边界线前' }}</h3>
        </div>
        <button type="button" class="verdict-close" aria-label="关闭" @click="close">×</button>
      </header>

      <p class="verdict-desc">
        禁忌目录、静默线和同伴的视线同时压过来。先确认你愿意承认的事实，再给出最终行动。
      </p>

      <div class="verdict-layout">
        <section class="evidence-board">
          <div class="board-head">
            <strong>边界事实</strong>
            <span>{{ selectedIds.length }}/{{ maxPicked }}</span>
          </div>
          <button
            v-for="item in evidence"
            :key="item.id"
            type="button"
            class="evidence-card"
            :class="{ selected: selectedIds.includes(item.id) }"
            :disabled="busy || (!selectedIds.includes(item.id) && selectedIds.length >= maxPicked)"
            @click="toggleEvidence(item.id)"
          >
            <span>{{ item.label }}</span>
            <small>{{ item.note }}</small>
          </button>
        </section>

        <section class="verdict-meter">
          <div class="meter-ring" :class="dominantTone.id">
            <span>{{ pressureScore }}</span>
            <small>{{ dominantTone.label }}</small>
          </div>
          <div class="meter-line">
            <span v-for="slot in selectedSlots" :key="slot.key" :class="{ empty: !slot.label }">
              {{ slot.label || '未确认' }}
            </span>
          </div>
          <p>{{ verdictPreview }}</p>
        </section>
      </div>

      <section class="ending-grid">
        <button
          v-for="ending in endings"
          :key="ending.id"
          type="button"
          class="ending-card"
          :class="{ selected: selectedEnding === ending.id }"
          :disabled="busy"
          @click="selectedEnding = ending.id"
        >
          <strong>{{ ending.label }}</strong>
          <span>{{ ending.hint }}</span>
        </button>
      </section>

      <footer class="verdict-actions">
        <button type="button" class="ghost" :disabled="busy || !selectedIds.length" @click="reset">
          重新判断
        </button>
        <button type="button" :disabled="busy || !canFinish" @click="finish">
          执行选择
        </button>
      </footer>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  event: { type: Object, default: null },
  busy: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'complete'])

const maxPicked = 3
const selectedIds = ref([])
const selectedEnding = ref('obey_order')

const evidence = [
  { id: 'law_pressure', label: '禁忌目录仍在', note: '规则没有声音，但每个人都知道它在', order: 34, truth: 4, secrecy: 6 },
  { id: 'silent_line', label: '静默线真实存在', note: '鸟声和风声都在同一处断开', order: 4, truth: 34, secrecy: 8 },
  { id: 'alice_hand', label: '爱丽丝按住记录本', note: '她担心的不是答案，而是你会不会回来', order: 24, truth: 8, secrecy: 18 },
  { id: 'eugeo_step', label: '尤吉欧往前半步', note: '他已经把这当成共同冒险的入口', order: 4, truth: 28, secrecy: 4 },
  { id: 'village_smoke', label: '村里的炊烟还在', note: '回去报告也能保护今天以前的日常', order: 26, truth: 2, secrecy: 18 },
  { id: 'wind_returns', label: '风声在边界后回流', note: '源头似乎只差一步就会承认你', order: 0, truth: 32, secrecy: 0 }
]

const endings = [
  { id: 'obey_order', label: '遵守规则，回村报告', hint: '保住安全和秩序，把异常交给村子处理。' },
  { id: 'cross_boundary', label: '越过边界，确认源头', hint: '触碰规则，但最接近静默线背后的真相。' },
  { id: 'hide_anomaly', label: '隐瞒异常，保护同伴', hint: '把风险留在自己心里，关系会留下阴影。' }
]

const selectedItems = computed(() =>
  selectedIds.value.map((id) => evidence.find((item) => item.id === id)).filter(Boolean)
)

const selectedSlots = computed(() =>
  Array.from({ length: maxPicked }, (_, index) => {
    const item = selectedItems.value[index]
    return { key: `${index}:${item?.id || 'empty'}`, label: item?.label || '' }
  })
)

const scores = computed(() => {
  const sum = { order: 0, truth: 0, secrecy: 0 }
  for (const item of selectedItems.value) {
    sum.order += Number(item.order || 0)
    sum.truth += Number(item.truth || 0)
    sum.secrecy += Number(item.secrecy || 0)
  }
  if (selectedEnding.value === 'obey_order') sum.order += 16
  if (selectedEnding.value === 'cross_boundary') sum.truth += 16
  if (selectedEnding.value === 'hide_anomaly') sum.secrecy += 16
  return sum
})

const dominantTone = computed(() => {
  const list = [
    { id: 'order', label: '秩序', value: scores.value.order },
    { id: 'truth', label: '真相', value: scores.value.truth },
    { id: 'secrecy', label: '隐瞒', value: scores.value.secrecy }
  ].sort((a, b) => b.value - a.value)
  return list[0]
})

const pressureScore = computed(() => Math.max(0, Math.min(100, dominantTone.value.value)))

const canFinish = computed(() => selectedIds.value.length === maxPicked && choiceAvailable.value)

const choiceAvailable = computed(() => {
  const ids = new Set((Array.isArray(props.event?.choices) ? props.event.choices : []).map((choice) => choice?.id))
  return ids.has(selectedEnding.value)
})

const verdictPreview = computed(() => {
  if (!selectedIds.value.length) return '先确认三条事实。你选择承认什么，结局就会偏向什么。'
  if (selectedEnding.value === 'cross_boundary') return '你把静默线看成必须亲手确认的真相。跨出去以后，关系会被改写。'
  if (selectedEnding.value === 'hide_anomaly') return '你准备把答案压在心里。这样能保护当下，也会让沉默继续长大。'
  return '你把规则和同伴安全放在前面。异常不会消失，但今天可以收束。'
})

function toggleEvidence(id) {
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
  selectedEnding.value = 'obey_order'
}

function close() {
  if (props.busy) return
  emit('update:modelValue', false)
}

function finish() {
  if (props.busy || !canFinish.value) return
  const ending = endings.find((item) => item.id === selectedEnding.value)
  emit('complete', {
    choice_id: selectedEnding.value,
    result: {
      label: ending?.label || '',
      tone: dominantTone.value.label,
      pressure: pressureScore.value,
      facts: selectedSlots.value.map((slot) => slot.label).filter(Boolean),
      text: verdictPreview.value
    }
  })
}

watch(
  () => [props.modelValue, props.event?.id],
  ([open]) => {
    if (open) reset()
  }
)
</script>

<style scoped>
.verdict-backdrop {
  position: fixed;
  inset: 0;
  z-index: 88;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(4, 8, 18, 0.8);
  backdrop-filter: blur(7px);
  -webkit-backdrop-filter: blur(7px);
}

.verdict-panel {
  width: min(94vw, 880px);
  max-height: min(88vh, 760px);
  overflow: auto;
  padding: 1.18rem;
  border-radius: 14px;
  color: #f8fafc;
  background: linear-gradient(165deg, rgba(28, 32, 48, 0.98), rgba(7, 10, 18, 0.98));
  border: 1px solid rgba(246, 211, 110, 0.34);
  box-shadow: 0 28px 72px rgba(0, 0, 0, 0.58), 0 0 30px rgba(246, 211, 110, 0.1);
}

.verdict-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding-bottom: 0.72rem;
  border-bottom: 1px solid rgba(246, 211, 110, 0.18);
}

.verdict-kicker {
  margin: 0 0 0.16rem;
  color: var(--sao-gold);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.verdict-header h3 {
  margin: 0;
  color: #fff7d6;
  font-size: 1.36rem;
}

.verdict-close {
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

.verdict-desc {
  margin: 0.82rem 0 0.9rem;
  color: #dbeafe;
  font-size: 0.98rem;
  line-height: 1.6;
}

.verdict-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(240px, 0.75fr);
  gap: 0.75rem;
}

.evidence-board,
.verdict-meter,
.ending-card {
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(246, 211, 110, 0.18);
}

.evidence-board {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
  padding: 0.65rem;
}

.board-head {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  color: #fde68a;
  font-size: 0.84rem;
  font-weight: 900;
}

.evidence-card {
  min-height: 4.9rem;
  padding: 0.58rem;
  border-radius: 9px;
  border: 1px solid rgba(246, 211, 110, 0.18);
  background: rgba(6, 12, 24, 0.58);
  color: #e2e8f0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 0.22rem;
  text-align: left;
}

.evidence-card:hover:not(:disabled),
.ending-card:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.58);
  background: rgba(28, 38, 56, 0.88);
}

.evidence-card.selected,
.ending-card.selected {
  border-color: rgba(253, 224, 71, 0.78);
  background: rgba(120, 83, 35, 0.44);
  box-shadow: 0 0 16px rgba(246, 211, 110, 0.12);
}

.evidence-card:disabled {
  opacity: 0.52;
  cursor: not-allowed;
}

.evidence-card span {
  color: #fff7d6;
  font-size: 0.92rem;
  font-weight: 900;
}

.evidence-card small {
  color: #bae6fd;
  font-size: 0.74rem;
  line-height: 1.35;
}

.verdict-meter {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.68rem;
}

.meter-ring {
  width: 8rem;
  height: 8rem;
  margin: 0 auto;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff7d6;
  background: radial-gradient(circle, rgba(255, 247, 214, 0.18), transparent 52%), rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(246, 211, 110, 0.32);
  box-shadow: inset 0 0 28px rgba(246, 211, 110, 0.12);
}

.meter-ring span {
  font-size: 2.1rem;
  font-weight: 900;
  line-height: 1;
}

.meter-ring small {
  color: #fde68a;
  font-size: 0.78rem;
  font-weight: 900;
}

.meter-ring.order { border-color: rgba(125, 211, 252, 0.6); }
.meter-ring.truth { border-color: rgba(253, 224, 71, 0.7); box-shadow: 0 0 22px rgba(246, 211, 110, 0.14); }
.meter-ring.secrecy { border-color: rgba(167, 139, 250, 0.62); }

.meter-line {
  display: grid;
  gap: 0.38rem;
}

.meter-line span {
  min-height: 2rem;
  display: grid;
  place-items: center;
  border-radius: 8px;
  color: #fff7d6;
  font-size: 0.82rem;
  font-weight: 900;
  background: rgba(120, 83, 35, 0.28);
  border: 1px solid rgba(246, 211, 110, 0.28);
}

.meter-line .empty {
  color: #94a3b8;
  background: rgba(6, 12, 24, 0.48);
  border-color: rgba(148, 163, 184, 0.16);
}

.verdict-meter p {
  margin: 0;
  color: #dbeafe;
  font-size: 0.9rem;
  line-height: 1.52;
}

.ending-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.ending-card {
  min-height: 5.3rem;
  padding: 0.62rem;
  color: #e2e8f0;
  cursor: pointer;
  text-align: left;
}

.ending-card strong,
.ending-card span {
  display: block;
}

.ending-card strong {
  color: #fff7d6;
  font-size: 0.9rem;
  line-height: 1.3;
}

.ending-card span {
  margin-top: 0.24rem;
  color: #bae6fd;
  font-size: 0.76rem;
  line-height: 1.35;
}

.verdict-actions {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 0.55rem;
  margin-top: 0.9rem;
}

.verdict-actions button {
  min-height: 2.7rem;
  border-radius: 9px;
  border: 1px solid rgba(246, 211, 110, 0.36);
  color: #fff7d6;
  background: linear-gradient(180deg, rgba(120, 83, 35, 0.96), rgba(48, 37, 24, 0.98));
  font-weight: 900;
  cursor: pointer;
}

.verdict-actions .ghost {
  color: #dbeafe;
  background: rgba(15, 23, 42, 0.72);
  border-color: rgba(125, 211, 252, 0.26);
}

.verdict-actions button:disabled {
  opacity: 0.48;
  cursor: not-allowed;
}

@media (max-width: 760px) {
  .verdict-layout,
  .ending-grid,
  .verdict-actions {
    grid-template-columns: 1fr;
  }

  .evidence-board {
    grid-template-columns: 1fr;
  }

  .meter-ring {
    width: 6.6rem;
    height: 6.6rem;
  }
}
</style>
