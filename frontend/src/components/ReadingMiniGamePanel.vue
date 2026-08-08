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
          <p class="reading-kicker">书库调查 · 三步推理</p>
          <h3>{{ activity?.title || '整理旧记录' }}</h3>
        </div>
        <button type="button" class="reading-close" aria-label="关闭" @click="close">×</button>
      </header>

      <p class="reading-desc">
        {{ chain.intro }}
      </p>

      <ol class="reading-progress" aria-label="推理进度">
        <li
          v-for="(step, index) in steps"
          :key="step.id"
          :class="{ active: index === stepIndex, done: index < stepIndex }"
        >
          <span class="progress-number">{{ index + 1 }}</span>
          <span>{{ step.label }}</span>
        </li>
      </ol>

      <section class="reading-stage" :aria-labelledby="`reading-step-${currentStep.id}`">
        <div class="stage-heading">
          <div>
            <p class="stage-kicker">第 {{ stepIndex + 1 }} 步 / {{ steps.length }}</p>
            <h4 :id="`reading-step-${currentStep.id}`">{{ currentStep.label }}：{{ currentStep.prompt }}</h4>
          </div>
          <span class="evidence-count">已锁定 {{ selectedIds.length }} / {{ steps.length }}</span>
        </div>
        <p class="stage-helper">{{ currentStep.helper }}</p>

        <div class="keyword-grid">
          <button
            v-for="option in currentStep.options"
            :key="option.id"
            type="button"
            class="keyword-chip"
            :class="{ selected: selectedIds[stepIndex] === option.id }"
            :disabled="busy || feedbackOpen"
            @click="chooseOption(option)"
          >
            <span>{{ option.label }}</span>
            <small>{{ option.note }}</small>
          </button>
        </div>
      </section>

      <div class="reading-thread" aria-label="已组成的推理链">
        <span
          v-for="(step, index) in steps"
          :key="step.id"
          :class="{ empty: !selectedIds[index], current: index === stepIndex }"
        >
          <b>{{ step.label }}</b>
          {{ selectedLabels[index] || '待选择' }}
        </span>
      </div>

      <section
        v-if="feedbackMessage"
        class="reading-feedback"
        :class="feedbackOpen ? 'error' : 'success'"
        role="status"
        aria-live="polite"
      >
        <strong>{{ feedbackOpen ? '这一步需要重看' : '证据已接上' }}</strong>
        <p>{{ feedbackMessage }}</p>
        <button v-if="feedbackOpen" type="button" class="feedback-dismiss" @click="dismissFeedback">
          重新选择
        </button>
      </section>

      <section v-else class="reading-interpretation">
        <strong>{{ currentStep.helper }}</strong>
        <p>错误选择只会停留在当前步骤，不会写入关系、记忆或剧情 flag。</p>
      </section>

      <footer class="reading-actions">
        <button type="button" class="ghost" :disabled="busy || !selectedIds.length" @click="reset">
          从头重看
        </button>
        <button type="button" class="ghost" :disabled="busy || stepIndex === 0" @click="backtrack">
          返回上一步
        </button>
        <button type="button" class="primary-action" :disabled="busy || !completedPath" @click="finish">
          记下这条结论
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

const fallbackChain = {
  intro: '把每一页先放在它能证明的层级：现象、规则、结论。',
  steps: [
    { id: 'phenomenon', label: '现象', prompt: '先辨认直接发生的异常。', helper: '先描述事实，不急着解释。', options: [] },
    { id: 'rule', label: '规则', prompt: '再找出能够约束它的旧规则。', helper: '规则应该能解释前一步。', options: [] },
    { id: 'conclusion', label: '结论', prompt: '最后收束成不超过证据的结论。', helper: '结论要回扣前两步。', options: [] }
  ],
  paths: []
}

const stepIndex = ref(0)
const selectedIds = ref([])
const feedbackMessage = ref('')
const feedbackOpen = ref(false)

const chain = computed(() => {
  const authored = props.activity?.reading_chain
  return authored?.steps?.length === 3 && Array.isArray(authored.paths) ? authored : fallbackChain
})
const steps = computed(() => chain.value.steps)
const currentStep = computed(() => steps.value[stepIndex.value] || steps.value[0] || fallbackChain.steps[0])
const selectedLabels = computed(() => selectedIds.value.map((id, index) => {
  const option = steps.value[index]?.options?.find((item) => item.id === id)
  return option?.label || ''
}))
const selectedSlots = computed(() => steps.value.map((step, index) => ({
  key: `${step.id}:${selectedIds.value[index] || 'empty'}`,
  label: selectedLabels.value[index] || ''
})))
const candidatePaths = computed(() => {
  const paths = Array.isArray(chain.value.paths) ? chain.value.paths : []
  return paths.filter((path) => selectedIds.value.every((id, index) => path.steps?.[index] === id))
})
const completedPath = computed(() => {
  if (selectedIds.value.length !== steps.value.length) return null
  return candidatePaths.value.find((path) => path.steps?.length === steps.value.length) || null
})

function chooseOption(option) {
  if (props.busy || feedbackOpen.value || !option?.id) return
  const expected = candidatePaths.value.some((path) => path.steps?.[stepIndex.value] === option.id)
  if (!expected) {
    feedbackMessage.value = option.feedback || '这条记录不能接在当前步骤后面。回到当前证据，再换一个选项。'
    feedbackOpen.value = true
    return
  }

  selectedIds.value = [...selectedIds.value.slice(0, stepIndex.value), option.id]
  feedbackMessage.value = option.feedback || '这一步和当前证据接上了。'
  feedbackOpen.value = false
  if (stepIndex.value < steps.value.length - 1) stepIndex.value += 1
}

function dismissFeedback() {
  feedbackMessage.value = ''
  feedbackOpen.value = false
}

function backtrack() {
  if (props.busy || stepIndex.value <= 0) return
  selectedIds.value = selectedIds.value.slice(0, stepIndex.value)
  stepIndex.value -= 1
  dismissFeedback()
}

function reset() {
  stepIndex.value = 0
  selectedIds.value = []
  dismissFeedback()
}

function close() {
  if (props.busy) return
  emit('update:modelValue', false)
}

function finish() {
  if (props.busy || !completedPath.value) return
  const path = completedPath.value
  emit('complete', {
    choice_id: path.choice_id,
    result: {
      label: path.label,
      text: path.success_text,
      steps: selectedSlots.value.map((slot) => slot.label),
      inference_chain: selectedIds.value.slice(),
      path_id: path.choice_id,
      explanation: '三步推理在书页证据范围内完成；只有现在才会向后端提交活动选择。'
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

.reading-kicker,
.stage-kicker {
  margin: 0 0 0.16rem;
  color: #bae6fd;
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.reading-header h3,
.stage-heading h4 {
  margin: 0;
  color: #fff7d6;
}

.reading-header h3 { font-size: 1.34rem; }
.stage-heading h4 { font-size: 1rem; line-height: 1.48; }

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
  margin: 0.82rem 0 0.75rem;
  color: #dbeafe;
  font-size: 0.98rem;
  line-height: 1.6;
}

.reading-progress {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.4rem;
  padding: 0;
  margin: 0 0 0.8rem;
  list-style: none;
}

.reading-progress li {
  display: flex;
  align-items: center;
  gap: 0.38rem;
  min-height: 2.15rem;
  padding: 0.35rem 0.48rem;
  border-radius: 8px;
  color: #94a3b8;
  background: rgba(15, 23, 42, 0.62);
  border: 1px solid rgba(148, 163, 184, 0.16);
  font-size: 0.78rem;
  font-weight: 800;
}

.reading-progress li.active { color: #fff7d6; border-color: rgba(246, 211, 110, 0.7); }
.reading-progress li.done { color: #bae6fd; border-color: rgba(125, 211, 252, 0.42); }
.progress-number {
  display: grid;
  place-items: center;
  width: 1.32rem;
  height: 1.32rem;
  border-radius: 50%;
  color: #0f172a;
  background: #94a3b8;
  font-size: 0.72rem;
}
.reading-progress li.active .progress-number { background: #f6d36e; }
.reading-progress li.done .progress-number { background: #7dd3fc; }

.reading-stage {
  padding: 0.78rem;
  border-radius: 10px;
  background: rgba(6, 12, 24, 0.42);
  border: 1px solid rgba(125, 211, 252, 0.18);
}
.stage-heading { display: flex; justify-content: space-between; gap: 0.75rem; }
.stage-helper { margin: 0.35rem 0 0.72rem; color: #bae6fd; font-size: 0.82rem; line-height: 1.45; }
.evidence-count { color: #94a3b8; font-size: 0.7rem; white-space: nowrap; }

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
  touch-action: manipulation;
}
.keyword-chip:hover:not(:disabled) { border-color: rgba(246, 211, 110, 0.54); background: rgba(28, 38, 56, 0.88); }
.keyword-chip.selected { border-color: rgba(246, 211, 110, 0.76); background: rgba(120, 83, 35, 0.44); box-shadow: 0 0 16px rgba(246, 211, 110, 0.12); }
.keyword-chip:disabled { opacity: 0.58; cursor: not-allowed; }
.keyword-chip span { color: #fff7d6; font-size: 0.94rem; font-weight: 900; }
.keyword-chip small { color: #bae6fd; font-size: 0.76rem; line-height: 1.35; }

.reading-thread {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.45rem;
  margin-top: 0.78rem;
}
.reading-thread span {
  min-height: 3rem;
  display: grid;
  place-items: center;
  gap: 0.12rem;
  border-radius: 8px;
  color: #fff7d6;
  font-size: 0.86rem;
  font-weight: 900;
  background: rgba(120, 83, 35, 0.28);
  border: 1px solid rgba(246, 211, 110, 0.28);
}
.reading-thread span b { color: #bae6fd; font-size: 0.62rem; letter-spacing: 0.08em; }
.reading-thread .empty { color: #94a3b8; background: rgba(15, 23, 42, 0.62); border-color: rgba(148, 163, 184, 0.16); }
.reading-thread .current { box-shadow: inset 0 0 0 1px rgba(125, 211, 252, 0.24); }

.reading-feedback,
.reading-interpretation {
  margin-top: 0.78rem;
  padding: 0.66rem 0.72rem;
  border-radius: 9px;
  background: rgba(6, 12, 24, 0.58);
}
.reading-feedback { border: 1px solid rgba(248, 113, 113, 0.55); }
.reading-feedback.success { border-color: rgba(125, 211, 252, 0.32); }
.reading-feedback strong,
.reading-interpretation strong { color: #fff7d6; font-size: 0.96rem; }
.reading-feedback p,
.reading-interpretation p { margin: 0.25rem 0 0; color: #dbeafe; font-size: 0.9rem; line-height: 1.48; }
.feedback-dismiss { margin-top: 0.45rem; padding: 0.32rem 0.5rem; border-radius: 6px; color: #fff7d6; background: rgba(120, 83, 35, 0.46); border: 1px solid rgba(246, 211, 110, 0.34); cursor: pointer; }

.reading-actions {
  display: grid;
  grid-template-columns: 0.8fr 0.8fr 1.4fr;
  gap: 0.55rem;
  margin-top: 0.9rem;
}
.reading-actions button { min-height: 2.7rem; border-radius: 9px; border: 1px solid rgba(246, 211, 110, 0.36); color: #fff7d6; background: linear-gradient(180deg, rgba(120, 83, 35, 0.96), rgba(48, 37, 24, 0.98)); font-weight: 900; cursor: pointer; touch-action: manipulation; }
.reading-actions .ghost { color: #dbeafe; background: rgba(15, 23, 42, 0.72); border-color: rgba(125, 211, 252, 0.26); }
.reading-actions button:disabled { opacity: 0.48; cursor: not-allowed; }

@media (max-width: 640px) {
  .reading-backdrop { align-items: flex-end; padding: 0; }
  .reading-panel { width: 100%; max-height: min(82dvh, 720px); padding: 0.9rem 0.82rem max(0.9rem, env(safe-area-inset-bottom)); border-radius: 16px 16px 0 0; }
  .stage-heading { display: block; }
  .evidence-count { display: block; margin-top: 0.28rem; }
  .keyword-grid, .reading-thread { grid-template-columns: 1fr; }
  .reading-actions { grid-template-columns: 1fr 1fr; }
  .reading-actions .primary-action { grid-column: 1 / -1; }
}
</style>
