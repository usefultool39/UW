<template>
  <div
    v-show="modelValue && event"
    class="probe-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="close"
  >
    <section class="probe-panel" @click.stop>
      <header class="probe-header">
        <div>
          <p class="probe-kicker">边界调查</p>
          <h3>{{ event?.title || '静默线校准' }}</h3>
        </div>
        <button type="button" class="probe-close" aria-label="关闭" @click="close">×</button>
      </header>

      <p class="probe-desc">
        风声被规则压住的一瞬间，先用刻印术短句锁定异常，再决定按谁的方式靠近静默线。
      </p>

      <div class="probe-body">
        <section class="command-board">
          <div class="board-head">
            <strong>刻印术短句</strong>
            <span>{{ selectedIds.length }}/{{ maxPicked }}</span>
          </div>
          <button
            v-for="fragment in fragments"
            :key="fragment.id"
            type="button"
            class="fragment-chip"
            :class="{ selected: selectedIds.includes(fragment.id) }"
            :disabled="busy || (!selectedIds.includes(fragment.id) && selectedIds.length >= maxPicked)"
            @click="toggleFragment(fragment.id)"
          >
            <span>{{ fragment.label }}</span>
            <small>{{ fragment.note }}</small>
          </button>
        </section>

        <section class="signal-board">
          <div class="signal-ring" :class="signalTier.id">
            <span>{{ signalScore }}</span>
            <small>{{ signalTier.label }}</small>
          </div>
          <div class="selected-line">
            <span v-for="slot in selectedSlots" :key="slot.key" :class="{ empty: !slot.label }">
              {{ slot.label || '待校准' }}
            </span>
          </div>
          <p>{{ signalText }}</p>
        </section>
      </div>

      <section class="stance-grid">
        <button
          v-for="stance in availableStances"
          :key="stance.id"
          type="button"
          class="stance-card"
          :class="{ selected: selectedStance === stance.id }"
          :disabled="busy"
          @click="selectedStance = stance.id"
        >
          <strong>{{ stance.label }}</strong>
          <span>{{ stance.hint }}</span>
        </button>
      </section>

      <footer class="probe-actions">
        <button type="button" class="ghost" :disabled="busy || !selectedIds.length" @click="reset">
          重置校准
        </button>
        <button type="button" :disabled="busy || !canFinish" @click="finish">
          确认异常
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
const selectedStance = ref('together')

const fragments = [
  { id: 'generate_light', label: '生成光素', note: '照出风声断开的边缘', value: 30 },
  { id: 'trace_silence', label: '追踪静默', note: '确认鸟声消失的方向', value: 34 },
  { id: 'bind_distance', label: '束定距离', note: '给同伴留下安全界线', value: 28 },
  { id: 'open_boundary', label: '开启边门', note: '更接近源头，但风险升高', value: 20 },
  { id: 'record_vector', label: '记录向量', note: '把异常写成可复查的线索', value: 24 },
  { id: 'listen_roots', label: '听取根音', note: '让古誓树回声参与判断', value: 22 }
]

const stances = [
  {
    id: 'caution',
    choiceIds: ['honor_alice_caution', 'investigate_together'],
    label: '先守住安全距离',
    hint: '更接近艾琳的做法，降低鲁莽越线的风险。'
  },
  {
    id: 'together',
    choiceIds: ['investigate_together'],
    label: '叫上两人一起确认',
    hint: '把调查变成三个人共同承担的判断。'
  },
  {
    id: 'promise',
    requiresChoice: 'follow_eugeo_promise',
    choiceIds: ['follow_eugeo_promise', 'investigate_together'],
    label: '兑现和尤里的约定',
    hint: '更主动推进调查，但艾琳会更紧张。'
  },
  {
    id: 'risk',
    choiceIds: ['press_alone'],
    label: '独自靠近异常',
    hint: '最快接近答案，也最容易留下不安。'
  }
]

const eventChoiceIds = computed(() =>
  new Set((Array.isArray(props.event?.choices) ? props.event.choices : []).map((choice) => choice?.id).filter(Boolean))
)

const availableStances = computed(() =>
  stances.filter((stance) => {
    if (stance.requiresChoice && !eventChoiceIds.value.has(stance.requiresChoice)) return false
    return stance.choiceIds.some((choiceId) => eventChoiceIds.value.has(choiceId))
  })
)

const selectedSlots = computed(() =>
  Array.from({ length: maxPicked }, (_, index) => {
    const id = selectedIds.value[index]
    const fragment = fragments.find((item) => item.id === id)
    return { key: `${index}:${id || 'empty'}`, label: fragment?.label || '' }
  })
)

const signalScore = computed(() => {
  const picked = selectedIds.value
    .map((id) => fragments.find((item) => item.id === id)?.value || 0)
    .reduce((sum, value) => sum + value, 0)
  const safetyBonus = selectedIds.value.includes('bind_distance') && selectedStance.value !== 'risk' ? 8 : 0
  const riskPenalty = selectedStance.value === 'risk' ? -12 : 0
  return Math.max(0, Math.min(100, picked + safetyBonus + riskPenalty))
})

const signalTier = computed(() => {
  if (signalScore.value >= 82) return { id: 'clear', label: '清晰' }
  if (signalScore.value >= 58) return { id: 'steady', label: '稳定' }
  return { id: 'unstable', label: '不稳' }
})

const signalText = computed(() => {
  if (!selectedIds.value.length) return '先选出三段刻印术短句。顺序会决定你们怎么解释这条静默线。'
  if (signalTier.value.id === 'clear') return '光素、风声和距离被压到同一条线上，异常源头的方向变得明确。'
  if (signalTier.value.id === 'steady') return '读数能用，但仍有噪声。继续靠近前最好让同伴知道你的判断。'
  return '短句还没有稳定成术式。硬靠近也能推进，但会让关系承受更多风险。'
})

const canFinish = computed(() => selectedIds.value.length === maxPicked && !!resolvedChoiceId.value)

const resolvedChoiceId = computed(() => {
  const stance = availableStances.value.find((item) => item.id === selectedStance.value) || availableStances.value[0]
  if (!stance) return ''
  if (selectedStance.value === 'risk' && signalScore.value < 58 && eventChoiceIds.value.has('press_alone')) {
    return 'press_alone'
  }
  return stance.choiceIds.find((choiceId) => eventChoiceIds.value.has(choiceId)) || ''
})

function toggleFragment(id) {
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
  selectedStance.value = availableStances.value[0]?.id || 'together'
}

function close() {
  if (props.busy) return
  emit('update:modelValue', false)
}

function finish() {
  if (props.busy || !canFinish.value) return
  const stance = availableStances.value.find((item) => item.id === selectedStance.value)
  emit('complete', {
    choice_id: resolvedChoiceId.value,
    result: {
      label: signalTier.value.label,
      score: signalScore.value,
      stance: stance?.label || '',
      fragments: selectedSlots.value.map((slot) => slot.label).filter(Boolean),
      text: signalText.value
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
.probe-backdrop {
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

.probe-panel {
  width: min(94vw, 840px);
  max-height: min(88vh, 740px);
  overflow: auto;
  padding: 1.18rem;
  border-radius: 14px;
  color: #f8fafc;
  background: linear-gradient(165deg, rgba(21, 34, 49, 0.98), rgba(8, 12, 22, 0.98));
  border: 1px solid rgba(125, 211, 252, 0.34);
  box-shadow: 0 26px 68px rgba(0, 0, 0, 0.56), 0 0 26px rgba(125, 211, 252, 0.1);
}

.probe-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding-bottom: 0.72rem;
  border-bottom: 1px solid rgba(125, 211, 252, 0.18);
}

.probe-kicker {
  margin: 0 0 0.16rem;
  color: #bae6fd;
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.probe-header h3 {
  margin: 0;
  color: #fff7d6;
  font-size: 1.36rem;
}

.probe-close {
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

.probe-desc {
  margin: 0.82rem 0 0.9rem;
  color: #dbeafe;
  font-size: 0.98rem;
  line-height: 1.6;
}

.probe-body {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(240px, 0.8fr);
  gap: 0.75rem;
}

.command-board,
.signal-board,
.stance-card {
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(125, 211, 252, 0.18);
}

.command-board {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem;
  padding: 0.65rem;
}

.board-head {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  color: #bae6fd;
  font-size: 0.84rem;
  font-weight: 900;
}

.fragment-chip {
  min-height: 4.7rem;
  padding: 0.58rem;
  border-radius: 9px;
  border: 1px solid rgba(125, 211, 252, 0.2);
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

.fragment-chip:hover:not(:disabled),
.stance-card:hover:not(:disabled) {
  border-color: rgba(246, 211, 110, 0.56);
  background: rgba(28, 38, 56, 0.88);
}

.fragment-chip.selected,
.stance-card.selected {
  border-color: rgba(246, 211, 110, 0.76);
  background: rgba(120, 83, 35, 0.44);
  box-shadow: 0 0 16px rgba(246, 211, 110, 0.12);
}

.fragment-chip:disabled {
  opacity: 0.52;
  cursor: not-allowed;
}

.fragment-chip span {
  color: #fff7d6;
  font-size: 0.92rem;
  font-weight: 900;
}

.fragment-chip small {
  color: #bae6fd;
  font-size: 0.74rem;
  line-height: 1.35;
}

.signal-board {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.68rem;
}

.signal-ring {
  width: 8rem;
  height: 8rem;
  margin: 0 auto;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff7d6;
  background:
    radial-gradient(circle, rgba(255, 247, 214, 0.18), transparent 52%),
    rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(125, 211, 252, 0.3);
  box-shadow: inset 0 0 28px rgba(94, 207, 255, 0.12);
}

.signal-ring span {
  font-size: 2.1rem;
  font-weight: 900;
  line-height: 1;
}

.signal-ring small {
  color: #bae6fd;
  font-size: 0.78rem;
  font-weight: 900;
}

.signal-ring.clear { border-color: rgba(253, 224, 71, 0.68); box-shadow: 0 0 24px rgba(246, 211, 110, 0.16); }
.signal-ring.steady { border-color: rgba(94, 207, 255, 0.64); }
.signal-ring.unstable { border-color: rgba(248, 113, 113, 0.42); }

.selected-line {
  display: grid;
  gap: 0.38rem;
}

.selected-line span {
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

.selected-line .empty {
  color: #94a3b8;
  background: rgba(6, 12, 24, 0.48);
  border-color: rgba(148, 163, 184, 0.16);
}

.signal-board p {
  margin: 0;
  color: #dbeafe;
  font-size: 0.9rem;
  line-height: 1.52;
}

.stance-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.stance-card {
  min-height: 5rem;
  padding: 0.62rem;
  color: #e2e8f0;
  cursor: pointer;
  text-align: left;
}

.stance-card strong,
.stance-card span {
  display: block;
}

.stance-card strong {
  color: #fff7d6;
  font-size: 0.88rem;
  line-height: 1.3;
}

.stance-card span {
  margin-top: 0.24rem;
  color: #bae6fd;
  font-size: 0.74rem;
  line-height: 1.35;
}

.probe-actions {
  display: grid;
  grid-template-columns: 0.8fr 1.2fr;
  gap: 0.55rem;
  margin-top: 0.9rem;
}

.probe-actions button {
  min-height: 2.7rem;
  border-radius: 9px;
  border: 1px solid rgba(246, 211, 110, 0.36);
  color: #fff7d6;
  background: linear-gradient(180deg, rgba(120, 83, 35, 0.96), rgba(48, 37, 24, 0.98));
  font-weight: 900;
  cursor: pointer;
}

.probe-actions .ghost {
  color: #dbeafe;
  background: rgba(15, 23, 42, 0.72);
  border-color: rgba(125, 211, 252, 0.26);
}

.probe-actions button:disabled {
  opacity: 0.48;
  cursor: not-allowed;
}

@media (max-width: 760px) {
  .probe-body,
  .stance-grid,
  .probe-actions {
    grid-template-columns: 1fr;
  }

  .command-board {
    grid-template-columns: 1fr;
  }

  .signal-ring {
    width: 6.6rem;
    height: 6.6rem;
  }
}
</style>
