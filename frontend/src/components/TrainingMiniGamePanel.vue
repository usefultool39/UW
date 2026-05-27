<template>
  <div
    v-show="modelValue && event"
    class="training-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="close"
  >
    <section class="training-panel" @click.stop>
      <header class="training-header">
        <div>
          <p class="training-kicker">古誓树训练</p>
          <h3>{{ event?.title || '节奏训练' }}</h3>
        </div>
        <button type="button" class="training-close" aria-label="关闭" @click="close">×</button>
      </header>

      <p class="training-desc">
        斧柄、呼吸、树干回震要落在同一个节拍上。光点经过金色区域时出手。
      </p>

      <div class="rhythm-strip" :class="{ locked: finished }" @click="recordHit">
        <div class="sweet-zone" />
        <div class="rhythm-marker" />
      </div>

      <div class="training-stats">
        <span>尝试 {{ attempts.length }}/{{ maxAttempts }}</span>
        <span>{{ feedbackText }}</span>
      </div>

      <div class="hit-row">
        <span v-for="(hit, index) in hitBadges" :key="index" :class="hit.className">{{ hit.label }}</span>
      </div>

      <footer class="training-actions">
        <button type="button" :disabled="busy || finished" @click="recordHit">出手</button>
        <button type="button" :disabled="busy || !canFinish" @click="finish('steady_training')">
          按节奏完成
        </button>
        <button type="button" class="ghost" :disabled="busy || attempts.length < 1" @click="finish('ask_boundary')">
          训练时追问边界
        </button>
      </footer>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  event: { type: Object, default: null },
  busy: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'complete'])

const maxAttempts = 3
const attempts = ref([])
const lastFeedback = ref('')
const finished = ref(false)

const canFinish = computed(() => attempts.value.length >= maxAttempts)

const averageScore = computed(() => {
  if (!attempts.value.length) return 0
  const total = attempts.value.reduce((sum, hit) => sum + hit.score, 0)
  return Math.round(total / attempts.value.length)
})

const tier = computed(() => {
  if (averageScore.value >= 82) {
    return { id: 'excellent', label: '优秀', text: '节拍很准，尤里明显感觉到你稳住了。' }
  }
  if (averageScore.value >= 52) {
    return { id: 'steady', label: '稳定', text: '动作还不完美，但节奏已经接上。' }
  }
  return { id: 'rough', label: '一般', text: '出手有些急，训练仍然算完成，只是回声不太稳。' }
})

const feedbackText = computed(() => {
  if (finished.value || canFinish.value) return `${tier.value.label} · ${tier.value.text}`
  return lastFeedback.value || '等待第一次出手'
})

const hitBadges = computed(() =>
  Array.from({ length: maxAttempts }, (_, index) => {
    const hit = attempts.value[index]
    if (!hit) return { label: '待命', className: 'pending' }
    if (hit.score >= 82) return { label: '正中', className: 'great' }
    if (hit.score >= 52) return { label: '接上', className: 'ok' }
    return { label: '偏离', className: 'miss' }
  })
)

function close() {
  if (props.busy) return
  emit('update:modelValue', false)
}

function reset() {
  attempts.value = []
  lastFeedback.value = ''
  finished.value = false
}

function recordHit() {
  if (!props.modelValue || props.busy || finished.value || attempts.value.length >= maxAttempts) return
  const cycle = 1600
  const raw = (Date.now() % cycle) / cycle
  const marker = raw <= 0.5 ? raw * 2 : (1 - raw) * 2
  const sweetCenter = 0.5
  const distance = Math.abs(marker - sweetCenter)
  const score = Math.max(0, Math.round(100 - distance * 210))
  attempts.value = [...attempts.value, { score }]
  if (score >= 82) lastFeedback.value = '正中节拍'
  else if (score >= 52) lastFeedback.value = '节奏接上了'
  else lastFeedback.value = '出手有些偏'
}

function finish(choiceId) {
  if (props.busy || attempts.value.length < 1) return
  finished.value = true
  emit('complete', {
    choice_id: choiceId,
    result: {
      tier: tier.value.id,
      label: tier.value.label,
      score: averageScore.value,
      hits: attempts.value.length,
      text: tier.value.text
    }
  })
}

function handleKeydown(event) {
  if (!props.modelValue) return
  if (event.key !== ' ') return
  event.preventDefault()
  recordHit()
}

watch(() => props.modelValue, (open) => {
  if (open) reset()
})

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<style scoped>
.training-backdrop {
  position: fixed;
  inset: 0;
  z-index: 87;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(4, 8, 18, 0.78);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.training-panel {
  width: min(94vw, 760px);
  max-height: min(88vh, 700px);
  overflow: auto;
  padding: 1.22rem;
  border-radius: 16px;
  color: #f8fafc;
  background: linear-gradient(165deg, rgba(27, 38, 58, 0.98), rgba(8, 12, 22, 0.98));
  border: 1px solid rgba(246, 211, 110, 0.34);
  box-shadow: 0 26px 68px rgba(0, 0, 0, 0.56), 0 0 26px rgba(246, 211, 110, 0.1);
}

.training-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(246, 211, 110, 0.18);
}

.training-kicker {
  margin: 0 0 0.16rem;
  color: var(--sao-gold);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.training-header h3 {
  margin: 0;
  color: #fff7d6;
  font-size: 1.42rem;
}

.training-close {
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

.training-desc {
  margin: 0.9rem 0 1rem;
  color: #dbeafe;
  font-size: 1rem;
  line-height: 1.62;
}

.rhythm-strip {
  position: relative;
  height: 4.5rem;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  background:
    linear-gradient(90deg, rgba(15, 23, 42, 0.94), rgba(30, 64, 175, 0.38), rgba(15, 23, 42, 0.94)),
    rgba(8, 13, 24, 0.86);
  border: 1px solid rgba(125, 211, 252, 0.28);
}

.rhythm-strip.locked {
  cursor: default;
  opacity: 0.78;
}

.sweet-zone {
  position: absolute;
  top: 0.45rem;
  bottom: 0.45rem;
  left: 42%;
  width: 16%;
  border-radius: 10px;
  background: rgba(246, 211, 110, 0.2);
  border: 1px solid rgba(253, 224, 71, 0.58);
  box-shadow: 0 0 22px rgba(246, 211, 110, 0.16);
}

.rhythm-marker {
  position: absolute;
  top: 0.35rem;
  bottom: 0.35rem;
  left: 0;
  width: 0.55rem;
  border-radius: 999px;
  background: #fff7d6;
  box-shadow: 0 0 18px rgba(255, 247, 214, 0.65);
  animation: rhythm-sweep 1.6s ease-in-out infinite alternate;
}

@keyframes rhythm-sweep {
  from { transform: translateX(0.6rem); }
  to { transform: translateX(calc(min(94vw, 760px) - 3.2rem)); }
}

.training-stats {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 0.72rem;
  color: #bae6fd;
  font-size: 0.9rem;
  font-weight: 800;
}

.hit-row {
  display: flex;
  gap: 0.45rem;
  margin-top: 0.72rem;
}

.hit-row span {
  flex: 1;
  min-height: 2rem;
  display: grid;
  place-items: center;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 900;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(15, 23, 42, 0.68);
  color: #94a3b8;
}

.hit-row .great {
  color: #fff7d6;
  background: rgba(120, 83, 35, 0.72);
  border-color: rgba(253, 224, 71, 0.48);
}

.hit-row .ok {
  color: #dcfce7;
  background: rgba(22, 101, 52, 0.38);
  border-color: rgba(134, 239, 172, 0.34);
}

.hit-row .miss {
  color: #fee2e2;
  background: rgba(127, 29, 29, 0.34);
  border-color: rgba(248, 113, 113, 0.28);
}

.training-actions {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1.2fr;
  gap: 0.55rem;
  margin-top: 0.95rem;
}

.training-actions button {
  min-height: 2.75rem;
  border-radius: 10px;
  border: 1px solid rgba(246, 211, 110, 0.36);
  color: #fff7d6;
  background: linear-gradient(180deg, rgba(120, 83, 35, 0.96), rgba(48, 37, 24, 0.98));
  font-weight: 900;
  cursor: pointer;
}

.training-actions button:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.78);
  box-shadow: 0 0 16px rgba(212, 175, 55, 0.18);
}

.training-actions .ghost {
  color: #dbeafe;
  background: rgba(15, 23, 42, 0.72);
  border-color: rgba(125, 211, 252, 0.26);
}

.training-actions button:disabled {
  opacity: 0.48;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .training-actions {
    grid-template-columns: 1fr;
  }

  .training-stats {
    flex-direction: column;
    gap: 0.28rem;
  }
}
</style>

