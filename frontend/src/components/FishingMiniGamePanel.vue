<template>
  <div
    v-show="modelValue && activity"
    class="fishing-backdrop"
    role="dialog"
    aria-modal="true"
    aria-labelledby="fishing-title"
    @click.self="close"
  >
    <section class="fishing-panel" @click.stop>
      <header class="fishing-header">
        <div>
          <p class="fishing-kicker">南湖旧渡 · 每日垂钓</p>
          <h3 id="fishing-title">{{ activity?.title || '雾中垂钓' }}</h3>
        </div>
        <button type="button" class="fishing-close" aria-label="关闭" @click="close">×</button>
      </header>

      <p class="fishing-desc">
        {{ activity?.description || '鱼线落入雾里。听见咬钩后，抓住最短的一瞬提竿。' }}
      </p>

      <section class="fishing-water" :class="phaseClass" aria-live="polite">
        <div class="water-lines" aria-hidden="true">
          <span v-for="line in 5" :key="line" :style="{ '--line-delay': `${line * 0.18}s` }" />
        </div>
        <div class="float" :class="{ biting: phase === 'bite', caught: phase === 'result' }" aria-hidden="true">
          <span class="float-tip" />
        </div>
        <div class="water-copy">
          <strong>{{ phaseLabel }}</strong>
          <span>{{ phaseHint }}</span>
        </div>
      </section>

      <section class="fishing-meter" aria-label="咬钩窗口">
        <div class="meter-heading">
          <span>咬钩窗口</span>
          <strong v-if="phase === 'bite'">{{ biteRemainingLabel }}</strong>
          <strong v-else>{{ attempts }} / {{ maxAttempts }} 次</strong>
        </div>
        <div class="meter-track">
          <div class="meter-fill" :class="meterClass" :style="{ width: `${meterPercent}%` }" />
        </div>
        <div class="meter-scale">
          <span>抛竿</span>
          <span>清脆提竿 · 稀有鱼</span>
          <span>错过</span>
        </div>
      </section>

      <section v-if="lastOutcome" class="fishing-outcome" :class="lastOutcome.kind">
        <div class="outcome-badge">{{ lastOutcome.badge }}</div>
        <div>
          <strong>{{ lastOutcome.label }}</strong>
          <p>{{ lastOutcome.text }}</p>
        </div>
      </section>

      <footer class="fishing-actions">
        <button
          v-if="phase === 'ready' || phase === 'missed'"
          type="button"
          class="fishing-primary"
          :disabled="busy"
          @click="cast"
        >
          {{ phase === 'missed' ? '再抛一竿' : '抛竿' }}
        </button>
        <button
          v-else-if="phase === 'waiting'"
          type="button"
          class="fishing-primary fishing-wait"
          :disabled="busy"
          @click="earlyLift"
        >
          等待咬钩…
        </button>
        <button
          v-else-if="phase === 'bite'"
          type="button"
          class="fishing-primary fishing-strike"
          :disabled="busy"
          @click="strike"
        >
          现在提竿！
        </button>
        <button
          v-else
          type="button"
          class="fishing-primary"
          :disabled="busy"
          @click="finish"
        >
          收线并结算
        </button>
        <button
          type="button"
          class="fishing-ghost"
          :disabled="busy || phase === 'waiting' || phase === 'bite'"
          @click="close"
        >
          先不钓了
        </button>
      </footer>

      <p class="fishing-note">本次结果会沿用场景活动结算，鱼获将直接写入库存。</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  activity: { type: Object, default: null },
  busy: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'complete'])

const maxAttempts = 3
const biteWindowMs = 900
const rareWindowMs = 240
const phase = ref('ready')
const attempts = ref(0)
const meterPercent = ref(0)
const biteRemainingMs = ref(biteWindowMs)
const lastOutcome = ref(null)
const caughtOutcome = ref(null)

let biteTimer = null
let meterTimer = null
let biteStartedAt = 0

const fallbackChoices = [
  {
    id: 'catch_common_fish',
    label: '湖鳞鱼（普通）',
    hint: '稳定提竿，获得 1 条南湖湖鳞鱼。'
  },
  {
    id: 'catch_rare_fish',
    label: '雾银鱼（稀有）',
    hint: '抓住最清脆的一瞬，获得 1 条南湖雾银鱼。'
  }
]

const choices = computed(() => {
  const authored = Array.isArray(props.activity?.choices) ? props.activity.choices : []
  return fallbackChoices.map((fallback) => authored.find((choice) => choice?.id === fallback.id) || fallback)
})

const commonChoice = computed(() => choices.value.find((choice) => choice.id === 'catch_common_fish') || fallbackChoices[0])
const rareChoice = computed(() => choices.value.find((choice) => choice.id === 'catch_rare_fish') || fallbackChoices[1])
const phaseClass = computed(() => `is-${phase.value}`)
const meterClass = computed(() => {
  if (phase.value === 'bite') return biteRemainingMs.value <= rareWindowMs ? 'rare-window' : 'bite-window'
  if (phase.value === 'result') return caughtOutcome.value?.rarity === 'rare' ? 'rare-window' : 'caught-window'
  return phase.value === 'missed' ? 'missed-window' : ''
})
const biteRemainingLabel = computed(() => `${(Math.max(0, biteRemainingMs.value) / 1000).toFixed(1)}s`)
const phaseLabel = computed(() => ({
  ready: '安静的水面',
  waiting: '浮漂正在下沉',
  bite: '咬钩！',
  missed: '鱼线重新安静下来',
  result: caughtOutcome.value?.rarity === 'rare' ? '稀有鱼获' : '鱼获到手'
}[phase.value] || '南湖旧渡'))
const phaseHint = computed(() => ({
  ready: '先抛竿，再等湖面给出回应。',
  waiting: '不要急，太早提竿只会惊走鱼。',
  bite: '在窗口内提竿；越接近清脆的一瞬，越可能钓到稀有鱼。',
  missed: attempts.value >= maxAttempts ? '今天的水面没有再给机会，先收竿吧。' : '还可以再试一次，听清下一次水声。',
  result: caughtOutcome.value?.rarity === 'rare' ? '雾银鱼的鳞光只停留了一瞬。' : '普通鱼也能成为今天的一份鲜味。'
}[phase.value] || ''))

function clearTimers() {
  if (biteTimer) window.clearTimeout(biteTimer)
  if (meterTimer) window.clearInterval(meterTimer)
  biteTimer = null
  meterTimer = null
}

function reset() {
  clearTimers()
  phase.value = 'ready'
  attempts.value = 0
  meterPercent.value = 0
  biteRemainingMs.value = biteWindowMs
  lastOutcome.value = null
  caughtOutcome.value = null
  biteStartedAt = 0
}

function cast() {
  if (props.busy || (phase.value === 'missed' && attempts.value >= maxAttempts)) return
  clearTimers()
  phase.value = 'waiting'
  meterPercent.value = 12
  biteRemainingMs.value = biteWindowMs
  const delay = 760 + Math.floor(Math.random() * 760)
  biteTimer = window.setTimeout(beginBite, delay)
}

function beginBite() {
  biteTimer = null
  phase.value = 'bite'
  biteStartedAt = performance.now()
  biteRemainingMs.value = biteWindowMs
  meterPercent.value = 100
  meterTimer = window.setInterval(() => {
    const elapsed = performance.now() - biteStartedAt
    biteRemainingMs.value = Math.max(0, biteWindowMs - elapsed)
    meterPercent.value = Math.max(0, (biteRemainingMs.value / biteWindowMs) * 100)
    if (elapsed >= biteWindowMs) miss()
  }, 40)
}

function earlyLift() {
  if (props.busy || phase.value !== 'waiting') return
  attempts.value += 1
  clearTimers()
  lastOutcome.value = {
    kind: 'miss',
    badge: '太早',
    label: '浮漂还没有咬住',
    text: '先等水面真正下沉，再把力道送进鱼线。'
  }
  phase.value = attempts.value >= maxAttempts ? 'missed' : 'missed'
  meterPercent.value = 0
}

function miss() {
  if (phase.value !== 'bite') return
  attempts.value += 1
  clearTimers()
  biteRemainingMs.value = 0
  meterPercent.value = 0
  lastOutcome.value = {
    kind: 'miss',
    badge: '脱钩',
    label: '鱼游回雾里了',
    text: attempts.value >= maxAttempts ? '今天的水面没有再给机会。' : '下一次把注意力放在浮漂最轻的一沉。'
  }
  phase.value = 'missed'
}

function strike() {
  if (props.busy || phase.value !== 'bite') return
  const timingMs = Math.max(0, performance.now() - biteStartedAt)
  attempts.value += 1
  clearTimers()
  const rare = timingMs <= rareWindowMs
  const choice = rare ? rareChoice.value : commonChoice.value
  caughtOutcome.value = {
    choiceId: choice.id,
    rarity: rare ? 'rare' : 'common',
    label: choice.label || (rare ? '雾银鱼（稀有）' : '湖鳞鱼（普通）'),
    score: rare ? 100 : Math.max(62, Math.round(100 - (timingMs / biteWindowMs) * 35)),
    timingMs: Math.round(timingMs),
    text: rare
      ? '提竿几乎和咬钩重合，雾银鱼的鳞光从水面一闪而过。'
      : '你稳稳收线，一条湖鳞鱼在雾边翻了个身。'
  }
  lastOutcome.value = {
    kind: rare ? 'rare' : 'common',
    badge: rare ? '稀有' : '普通',
    label: caughtOutcome.value.label,
    text: caughtOutcome.value.text
  }
  phase.value = 'result'
  meterPercent.value = rare ? 100 : Math.max(38, caughtOutcome.value.score)
}

function finish() {
  if (props.busy || phase.value !== 'result' || !caughtOutcome.value) return
  emit('complete', {
    choice_id: caughtOutcome.value.choiceId,
    result: {
      fish_id: caughtOutcome.value.rarity === 'rare' ? 'south_lake_rare_fish' : 'south_lake_common_fish',
      fish_rarity: caughtOutcome.value.rarity,
      label: caughtOutcome.value.label,
      score: caughtOutcome.value.score,
      timing_ms: caughtOutcome.value.timingMs,
      attempts: attempts.value,
      text: caughtOutcome.value.text
    }
  })
}

function close() {
  if (props.busy) return
  clearTimers()
  emit('update:modelValue', false)
}

watch(() => props.modelValue, (open) => {
  if (open) reset()
  else clearTimers()
})

onUnmounted(clearTimers)
</script>

<style scoped>
.fishing-backdrop {
  position: fixed;
  inset: 0;
  z-index: 89;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(2, 11, 20, .84);
  backdrop-filter: blur(7px);
  -webkit-backdrop-filter: blur(7px);
}

.fishing-panel {
  width: min(94vw, 760px);
  max-height: min(90vh, 760px);
  overflow: auto;
  padding: 1.16rem;
  border-radius: 18px;
  color: #e0f2fe;
  background: linear-gradient(160deg, rgba(10, 39, 57, .98), rgba(4, 14, 27, .99));
  border: 1px solid rgba(103, 232, 249, .34);
  box-shadow: 0 28px 76px rgba(0, 0, 0, .62), 0 0 34px rgba(34, 211, 238, .1);
}

.fishing-header { display: flex; justify-content: space-between; gap: .8rem; padding-bottom: .72rem; border-bottom: 1px solid rgba(103, 232, 249, .2); }
.fishing-kicker { margin: 0 0 .16rem; color: #67e8f9; font-size: .63rem; font-weight: 900; letter-spacing: .14em; }
.fishing-header h3 { margin: 0; color: #ecfeff; font-size: 1.4rem; }
.fishing-close { width: 2.35rem; height: 2.35rem; border-radius: 9px; border: 1px solid rgba(148, 163, 184, .24); background: rgba(15, 23, 42, .68); color: #e2e8f0; font-size: 1.25rem; cursor: pointer; }
.fishing-desc { margin: .82rem 0 .92rem; color: #c7e8f4; line-height: 1.58; }

.fishing-water { position: relative; min-height: 11rem; display: grid; place-items: center; overflow: hidden; border-radius: 14px; background: radial-gradient(circle at 50% 32%, rgba(125, 211, 252, .36), transparent 28%), linear-gradient(180deg, #164e63 0%, #082f49 48%, #071827 100%); border: 1px solid rgba(125, 211, 252, .25); }
.fishing-water::after { content: ''; position: absolute; inset: auto 0 0; height: 35%; background: linear-gradient(180deg, transparent, rgba(2, 6, 23, .46)); }
.water-lines { position: absolute; inset: 34% 8% 16%; display: grid; gap: .78rem; }
.water-lines span { display: block; height: 1px; border-radius: 99px; background: rgba(186, 230, 253, .28); transform: scaleX(.76); animation: water-shift 2.8s ease-in-out infinite alternate; animation-delay: var(--line-delay); }
.float { position: absolute; z-index: 2; top: 43%; width: .7rem; height: 3.8rem; transform: rotate(5deg); transition: transform .16s ease, top .16s ease; }
.float::before { content: ''; position: absolute; top: 0; left: 50%; width: 2px; height: 2.7rem; background: rgba(224, 242, 254, .72); }
.float-tip { position: absolute; left: 50%; bottom: 0; width: .7rem; height: 1rem; border-radius: 50% 50% 55% 55%; background: #fcd34d; box-shadow: 0 0 14px rgba(253, 224, 71, .4); }
.float.biting { top: 48%; transform: rotate(17deg) scale(1.1); }
.float.caught { top: 34%; transform: rotate(-8deg) translateY(-8px); }
.water-copy { position: relative; z-index: 3; display: grid; gap: .28rem; margin-top: 3.4rem; text-align: center; text-shadow: 0 2px 10px rgba(0, 0, 0, .55); }
.water-copy strong { color: #f0fdff; font-size: 1.35rem; }
.water-copy span { color: #bae6fd; font-size: .88rem; }

.fishing-meter { margin-top: .9rem; padding: .75rem .8rem; border-radius: 12px; background: rgba(2, 12, 27, .66); border: 1px solid rgba(125, 211, 252, .18); }
.meter-heading, .meter-scale { display: flex; justify-content: space-between; gap: .7rem; color: #bae6fd; font-size: .78rem; }
.meter-heading strong { color: #fef08a; }
.meter-track { height: .78rem; margin: .48rem 0 .4rem; overflow: hidden; border-radius: 99px; background: rgba(15, 23, 42, .94); border: 1px solid rgba(125, 211, 252, .22); }
.meter-fill { height: 100%; border-radius: inherit; background: linear-gradient(90deg, #38bdf8, #67e8f9); transition: width .08s linear, background .15s ease; }
.meter-fill.rare-window { background: linear-gradient(90deg, #facc15, #fb7185); box-shadow: 0 0 14px rgba(250, 204, 21, .38); }
.meter-fill.caught-window { background: linear-gradient(90deg, #22d3ee, #a7f3d0); }
.meter-fill.missed-window { background: #64748b; }
.meter-scale { color: #7dd3fc; font-size: .68rem; }

.fishing-outcome { display: flex; gap: .75rem; align-items: center; margin-top: .8rem; padding: .72rem .78rem; border-radius: 12px; border: 1px solid rgba(125, 211, 252, .24); background: rgba(8, 47, 73, .48); }
.fishing-outcome.rare { border-color: rgba(250, 204, 21, .54); background: rgba(113, 63, 18, .3); }
.outcome-badge { display: grid; place-items: center; min-width: 3.2rem; min-height: 2rem; padding: .2rem .45rem; border-radius: 8px; color: #082f49; background: #bae6fd; font-size: .74rem; font-weight: 950; }
.fishing-outcome.rare .outcome-badge { color: #451a03; background: #fde68a; }
.fishing-outcome strong { color: #ecfeff; }
.fishing-outcome p { margin: .18rem 0 0; color: #c7e8f4; font-size: .85rem; line-height: 1.45; }

.fishing-actions { display: grid; grid-template-columns: 1.25fr .75fr; gap: .55rem; margin-top: .9rem; }
.fishing-actions button { min-height: 2.75rem; border-radius: 10px; border: 1px solid rgba(103, 232, 249, .38); font-weight: 900; cursor: pointer; transition: transform .15s ease, border-color .15s ease, opacity .15s ease; }
.fishing-actions button:hover:not(:disabled) { transform: translateY(-1px); border-color: rgba(186, 230, 253, .82); }
.fishing-primary { color: #082f49; background: linear-gradient(180deg, #a5f3fc, #38bdf8); }
.fishing-strike { color: #451a03; background: linear-gradient(180deg, #fde68a, #fb7185); animation: strike-pulse .85s ease-in-out infinite alternate; }
.fishing-wait { color: #bae6fd; background: rgba(15, 23, 42, .78); }
.fishing-ghost { color: #c7e8f4; background: rgba(15, 23, 42, .72); }
.fishing-actions button:disabled { opacity: .48; cursor: not-allowed; transform: none; }
.fishing-note { margin: .72rem 0 0; color: #7dd3fc; font-size: .73rem; text-align: center; }

@keyframes water-shift { from { transform: scaleX(.62) translateX(-3%); opacity: .4; } to { transform: scaleX(1) translateX(4%); opacity: .82; } }
@keyframes strike-pulse { from { box-shadow: 0 0 0 rgba(253, 224, 71, 0); } to { box-shadow: 0 0 22px rgba(253, 224, 71, .34); } }

@media (max-width: 640px) {
  .fishing-backdrop { align-items: flex-end; padding: 0; }
  .fishing-panel { width: 100%; max-height: min(80dvh, 650px); padding: .95rem .9rem max(.9rem, env(safe-area-inset-bottom)); border-radius: 18px 18px 0 0; }
  .fishing-water { min-height: 8.8rem; }
  .fishing-actions { grid-template-columns: 1fr; }
  .fishing-actions button { min-height: 3rem; touch-action: manipulation; }
  .meter-scale span:nth-child(2) { text-align: center; }
}
</style>
