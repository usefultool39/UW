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
          <p class="training-kicker">巨神树训练</p>
          <h3>{{ event?.title || '节奏训练' }}</h3>
        </div>
        <button type="button" class="training-close" aria-label="关闭" @click="close">×</button>
      </header>

      <p class="training-desc">
        斧柄、呼吸、树干回震要落在同一个节拍上。光点越快，越要先稳住呼吸再出手。
      </p>

      <div class="training-overview" aria-live="polite">
        <div class="stage-card">
          <span class="stat-label">训练阶段</span>
          <strong>第 {{ stageNumber }}/{{ maxAttempts }} 阶段</strong>
          <small>{{ stageMeta.label }} · {{ stageMeta.speedLabel }}</small>
        </div>
        <div class="combo-card" :class="{ active: combo > 0, broken: comboBroken }">
          <span class="stat-label">连击</span>
          <strong>{{ combo }} <small>连</small></strong>
          <small>{{ comboHint }}</small>
        </div>
      </div>

      <div class="stage-progress" aria-hidden="true">
        <span :style="{ width: `${progressPercent}%` }" />
      </div>

      <div
        class="rhythm-strip"
        :class="{ locked: finished }"
        role="button"
        tabindex="0"
        aria-label="节奏条，点按或按空格出手"
        @pointerdown.prevent="recordHit"
        @keydown.enter.prevent="recordHit"
      >
        <div class="sweet-zone" :style="sweetZoneStyle" />
        <div class="rhythm-marker" :style="{ left: markerLeft }" />
        <span class="rhythm-hint">点按 / 空格出手</span>
      </div>

      <div class="training-stats">
        <span>尝试 {{ attempts.length }}/{{ maxAttempts }}</span>
        <span class="feedback-line" :class="feedbackClass">{{ feedbackText }}</span>
      </div>

      <div v-if="lastHit" class="last-hit" :class="lastHit.className" aria-live="polite">
        <strong>{{ lastHit.label }}</strong>
        <span>{{ lastHit.detail }}</span>
        <em v-if="lastHit.combo > 1">{{ lastHit.combo }} 连 · 稳定加成</em>
        <em v-else-if="lastHit.combo === 0 && lastHit.brokeCombo">连击中断 · 重新找回呼吸</em>
      </div>

      <div class="hit-row" aria-label="每阶段判定">
        <span v-for="(hit, index) in hitBadges" :key="index" :class="hit.className">
          <b>{{ hit.label }}</b>
          <small>{{ hit.score ? `${hit.score}分` : '待命' }}</small>
        </span>
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

const maxAttempts = 5
const stages = [
  { cycle: 1800, sweetWidth: 18, label: '找回节拍', speedLabel: '基础速度' },
  { cycle: 1500, sweetWidth: 16, label: '接住回震', speedLabel: '加速 ×1.2' },
  { cycle: 1250, sweetWidth: 14, label: '稳住呼吸', speedLabel: '加速 ×1.4' },
  { cycle: 1050, sweetWidth: 12, label: '听见树心', speedLabel: '加速 ×1.7' },
  { cycle: 900, sweetWidth: 10, label: '与树同拍', speedLabel: '加速 ×2.0' }
]

const attempts = ref([])
const lastFeedback = ref('')
const lastHit = ref(null)
const finished = ref(false)
const combo = ref(0)
const maxCombo = ref(0)
const comboBroken = ref(false)
const markerPosition = ref(0.5)

let animationFrameId = 0
let motionStartedAt = 0
let comboResetTimer = 0

const stageMeta = computed(() => stages[Math.min(attempts.value.length, stages.length - 1)])
const stageNumber = computed(() => Math.min(attempts.value.length + 1, maxAttempts))
const progressPercent = computed(() => Math.round((attempts.value.length / maxAttempts) * 100))
const markerLeft = computed(() => `${Math.max(0, Math.min(100, markerPosition.value * 100))}%`)
const sweetZoneStyle = computed(() => ({
  left: `${50 - stageMeta.value.sweetWidth / 2}%`,
  width: `${stageMeta.value.sweetWidth}%`
}))
const canFinish = computed(() => attempts.value.length >= maxAttempts)

const averageScore = computed(() => {
  if (!attempts.value.length) return 0
  const total = attempts.value.reduce((sum, hit) => sum + hit.score, 0)
  return Math.round(total / attempts.value.length)
})

const tier = computed(() => {
  if (averageScore.value >= 82) {
    return { id: 'excellent', label: '优秀', text: '节拍很准，尤吉欧明显感觉到你稳住了。' }
  }
  if (averageScore.value >= 52) {
    return { id: 'steady', label: '稳定', text: '动作还不完美，但节奏已经接上。' }
  }
  return { id: 'rough', label: '一般', text: '出手有些急，训练仍然算完成，只是回声不太稳。' }
})

const comboHint = computed(() => {
  if (comboBroken.value) return '连击断开'
  if (combo.value >= 3) return '呼吸越来越稳'
  if (combo.value > 0) return '继续保持'
  return '先稳住第一拍'
})

const feedbackText = computed(() => {
  if (finished.value || canFinish.value) return `${tier.value.label} · ${tier.value.text}`
  return lastFeedback.value || '等待第一次出手'
})

const feedbackClass = computed(() => lastHit.value?.className || 'neutral')

const hitBadges = computed(() =>
  Array.from({ length: maxAttempts }, (_, index) => {
    const hit = attempts.value[index]
    if (!hit) return { label: '待命', score: 0, className: 'pending' }
    return { label: hit.label, score: hit.score, className: hit.className }
  })
)

function close() {
  if (props.busy) return
  stopMotion()
  emit('update:modelValue', false)
}

function reset() {
  attempts.value = []
  lastFeedback.value = ''
  lastHit.value = null
  finished.value = false
  combo.value = 0
  maxCombo.value = 0
  comboBroken.value = false
  markerPosition.value = 0.5
  startMotion()
}

function getJudgement(score) {
  if (score >= 86) {
    return { label: '正中', className: 'great', detail: '完美命中 · 树干回震清澈' }
  }
  if (score >= 58) {
    return { label: '接上', className: 'ok', detail: '稳定命中 · 节奏没有散开' }
  }
  return { label: '偏离', className: 'miss', detail: '失误 · 回震偏了一拍' }
}

function recordHit() {
  if (!props.modelValue || props.busy || finished.value || attempts.value.length >= maxAttempts) return

  const previousCombo = combo.value
  const distance = Math.abs(markerPosition.value - 0.5)
  const baseScore = Math.max(0, Math.round(100 - distance * 200))
  const judgement = getJudgement(baseScore)
  const nextCombo = judgement.className === 'miss' ? 0 : previousCombo + 1
  const comboBonus = nextCombo > 1 ? Math.min((nextCombo - 1) * 3, 9) : 0
  const score = Math.min(100, baseScore + comboBonus)
  const brokeCombo = previousCombo > 0 && nextCombo === 0
  const hit = {
    score,
    baseScore,
    label: judgement.label,
    className: judgement.className,
    detail: judgement.detail,
    combo: nextCombo,
    brokeCombo
  }

  attempts.value = [...attempts.value, hit]
  combo.value = nextCombo
  maxCombo.value = Math.max(maxCombo.value, nextCombo)
  comboBroken.value = brokeCombo
  lastHit.value = hit
  lastFeedback.value = brokeCombo
    ? '连击中断，重新找回呼吸'
    : nextCombo > 1
      ? `${judgement.label} · ${nextCombo} 连，节拍更稳`
      : judgement.detail

  clearTimeout(comboResetTimer)
  if (brokeCombo) {
    comboResetTimer = window.setTimeout(() => {
      comboBroken.value = false
    }, 900)
  }
  restartMotion()
}

function finish(choiceId) {
  if (props.busy || attempts.value.length < 1) return
  finished.value = true
  stopMotion()
  emit('complete', {
    choice_id: choiceId,
    result: {
      tier: tier.value.id,
      label: tier.value.label,
      score: averageScore.value,
      hits: attempts.value.length,
      text: tier.value.text,
      combo: maxCombo.value,
      stages_cleared: attempts.value.length
    }
  })
}

function animate(now) {
  if (!props.modelValue || finished.value) return
  if (!motionStartedAt) motionStartedAt = now
  const elapsed = now - motionStartedAt
  const raw = (elapsed % stageMeta.value.cycle) / stageMeta.value.cycle
  markerPosition.value = raw <= 0.5 ? raw * 2 : (1 - raw) * 2
  animationFrameId = window.requestAnimationFrame(animate)
}

function startMotion() {
  stopMotion()
  if (!props.modelValue || finished.value) return
  motionStartedAt = window.performance?.now?.() || Date.now()
  animationFrameId = window.requestAnimationFrame(animate)
}

function restartMotion() {
  startMotion()
}

function stopMotion() {
  if (animationFrameId) window.cancelAnimationFrame(animationFrameId)
  animationFrameId = 0
  motionStartedAt = 0
}

function handleKeydown(event) {
  if (!props.modelValue) return
  if (event.key !== ' ') return
  event.preventDefault()
  recordHit()
}

watch(() => props.modelValue, (open) => {
  if (open) reset()
  else stopMotion()
})

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  if (props.modelValue) startMotion()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  clearTimeout(comboResetTimer)
  stopMotion()
})
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
  background: rgba(4, 8, 18, 0.68);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
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
  flex: 0 0 auto;
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

.training-overview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.55rem;
  margin-bottom: 0.62rem;
}

.stage-card,
.combo-card {
  min-width: 0;
  padding: 0.62rem 0.72rem;
  border: 1px solid rgba(125, 211, 252, 0.18);
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.58);
}

.combo-card {
  border-color: rgba(246, 211, 110, 0.2);
}

.combo-card.active {
  border-color: rgba(134, 239, 172, 0.54);
  background: linear-gradient(135deg, rgba(22, 101, 52, 0.34), rgba(15, 23, 42, 0.62));
}

.combo-card.broken {
  border-color: rgba(248, 113, 113, 0.72);
  animation: combo-break 0.45s ease-out;
}

.stat-label,
.stage-card small,
.combo-card small {
  display: block;
  color: #94a3b8;
  font-size: 0.72rem;
  font-weight: 800;
}

.stage-card strong,
.combo-card strong {
  display: block;
  margin: 0.12rem 0;
  color: #fff7d6;
  font-size: 1rem;
}

.combo-card strong {
  color: #bbf7d0;
  font-size: 1.28rem;
}

.combo-card strong small {
  display: inline;
  color: inherit;
  font-size: 0.72rem;
}

.stage-progress {
  height: 0.28rem;
  margin-bottom: 0.72rem;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.8);
}

.stage-progress span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #38bdf8, #f6d36e, #86efac);
  transition: width 0.25s ease;
}

.rhythm-strip {
  position: relative;
  height: 4.5rem;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  touch-action: manipulation;
  background:
    linear-gradient(90deg, rgba(15, 23, 42, 0.94), rgba(30, 64, 175, 0.38), rgba(15, 23, 42, 0.94)),
    rgba(8, 13, 24, 0.86);
  border: 1px solid rgba(125, 211, 252, 0.28);
  outline: none;
}

.rhythm-strip:focus-visible {
  box-shadow: 0 0 0 3px rgba(125, 211, 252, 0.3);
}

.rhythm-strip.locked {
  cursor: default;
  opacity: 0.78;
}

.sweet-zone {
  position: absolute;
  top: 0.45rem;
  bottom: 0.45rem;
  border-radius: 10px;
  background: rgba(246, 211, 110, 0.2);
  border: 1px solid rgba(253, 224, 71, 0.58);
  box-shadow: 0 0 22px rgba(246, 211, 110, 0.16);
  transition: left 0.2s ease, width 0.2s ease;
}

.rhythm-marker {
  position: absolute;
  top: 0.35rem;
  bottom: 0.35rem;
  width: 0.55rem;
  transform: translateX(-50%);
  border-radius: 999px;
  background: #fff7d6;
  box-shadow: 0 0 18px rgba(255, 247, 214, 0.65);
  will-change: left;
}

.rhythm-hint {
  position: absolute;
  right: 0.62rem;
  bottom: 0.38rem;
  color: rgba(219, 234, 254, 0.68);
  font-size: 0.68rem;
  font-weight: 800;
  pointer-events: none;
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

.feedback-line {
  text-align: right;
}

.feedback-line.great { color: #fde68a; }
.feedback-line.ok { color: #bbf7d0; }
.feedback-line.miss { color: #fecaca; }
.feedback-line.neutral { color: #bae6fd; }

.last-hit {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem 0.6rem;
  margin-top: 0.55rem;
  padding: 0.48rem 0.65rem;
  border-radius: 9px;
  background: rgba(15, 23, 42, 0.62);
  border-left: 3px solid #94a3b8;
  animation: hit-in 0.2s ease-out;
}

.last-hit strong { font-size: 0.9rem; }
.last-hit span { color: #cbd5e1; font-size: 0.78rem; }
.last-hit em { margin-left: auto; color: #bbf7d0; font-size: 0.72rem; font-style: normal; font-weight: 900; }
.last-hit.great { border-left-color: #facc15; }
.last-hit.ok { border-left-color: #86efac; }
.last-hit.miss { border-left-color: #f87171; }
.last-hit.miss em { color: #fecaca; }

.hit-row {
  display: flex;
  gap: 0.45rem;
  margin-top: 0.72rem;
}

.hit-row span {
  flex: 1;
  min-width: 0;
  min-height: 2.3rem;
  display: grid;
  place-items: center;
  gap: 0.08rem;
  padding: 0.25rem 0.18rem;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 900;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(15, 23, 42, 0.68);
  color: #94a3b8;
}

.hit-row small {
  color: inherit;
  font-size: 0.62rem;
  font-weight: 800;
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
  touch-action: manipulation;
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

@keyframes hit-in {
  from { opacity: 0.25; transform: translateY(-2px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes combo-break {
  0%, 100% { transform: translateX(0); }
  35% { transform: translateX(-3px); }
  70% { transform: translateX(3px); }
}

@media (max-width: 640px) {
  .training-backdrop {
    align-items: flex-end;
    padding: 0.5rem;
    padding-bottom: max(0.5rem, env(safe-area-inset-bottom));
  }

  .training-panel {
    width: 100%;
    max-height: min(78dvh, 560px);
    padding: 0.9rem;
    border-radius: 18px 18px 10px 10px;
  }

  .training-header h3 { font-size: 1.18rem; }
  .training-desc { margin: 0.65rem 0 0.75rem; font-size: 0.88rem; line-height: 1.45; }
  .rhythm-strip { height: 4rem; }
  .rhythm-hint { font-size: 0.62rem; }

  .training-stats {
    flex-direction: column;
    gap: 0.28rem;
    font-size: 0.8rem;
  }

  .feedback-line { text-align: left; }
  .last-hit em { margin-left: 0; }

  .training-actions {
    grid-template-columns: 1fr;
    gap: 0.42rem;
    margin-top: 0.72rem;
  }

  .training-actions button { min-height: 2.55rem; }
}
</style>
