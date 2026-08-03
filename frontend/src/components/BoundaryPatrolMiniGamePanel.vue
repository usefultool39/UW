<template>
  <div
    v-show="modelValue && activity"
    class="patrol-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="close"
  >
    <section class="patrol-panel" @click.stop>
      <header class="patrol-header">
        <div>
          <p class="patrol-kicker">可重复短循环 · 北境巡查</p>
          <h3>{{ activity?.title || '北境边门 · 短程巡查' }}</h3>
        </div>
        <button type="button" class="patrol-close" aria-label="关闭" :disabled="busy" @click="close">×</button>
      </header>

      <p class="patrol-desc">
        威胁会先暴露意图。看清动作，再选择克制架势；判断正确就能减少损伤并带回更多边境标记。
      </p>

      <section class="patrol-vitals" aria-label="巡查资源">
        <div class="vital-card hp">
          <span>生命</span><strong>{{ localHp }}/{{ maxHp }}</strong>
          <i><b :style="{ width: hpPercent + '%' }"></b></i>
        </div>
        <div class="vital-card mp">
          <span>神圣力</span><strong>{{ localMp }}/{{ maxMp }}</strong>
          <i><b :style="{ width: mpPercent + '%' }"></b></i>
        </div>
        <div class="vital-card stamina">
          <span>体力</span><strong>{{ localStamina }}/{{ maxStamina }}</strong>
          <i><b :style="{ width: staminaPercent + '%' }"></b></i>
        </div>
        <div class="vital-card marks">
          <span>边境标记</span><strong>+{{ marks }}</strong>
          <small>本次预计带回</small>
        </div>
      </section>

      <section v-if="!finished" class="encounter-board">
        <div class="route-progress">
          <span v-for="(_, index) in encounters" :key="index" :class="{ done: index < roundIndex, active: index === roundIndex }">
            {{ index < roundIndex ? '✓' : index + 1 }}
          </span>
          <strong>{{ roundIndex + 1 }}/{{ encounters.length }}</strong>
        </div>

        <article class="threat-card" :class="currentEncounter.tone">
          <div class="threat-topline">
            <span>{{ currentEncounter.zone }}</span>
            <b>威胁 {{ currentEncounter.danger }}</b>
          </div>
          <h4>{{ currentEncounter.title }}</h4>
          <p>{{ currentEncounter.description }}</p>
          <div class="enemy-intent">
            <span>敌方意图</span>
            <strong>{{ currentEncounter.intent }}</strong>
            <small>{{ currentEncounter.telegraph }}</small>
          </div>
        </article>

        <div class="counter-hint">
          <span>判断提示</span>
          冲撞用格挡，聚能用神圣术，横扫用侧步。选错仍能继续，但代价会立刻显示。
        </div>

        <section class="tactic-grid">
          <button
            v-for="tactic in tactics"
            :key="tactic.id"
            type="button"
            :disabled="busy || !canUse(tactic)"
            @click="chooseTactic(tactic)"
          >
            <span class="tactic-kicker">{{ tactic.counterLabel }}</span>
            <strong>{{ tactic.label }}</strong>
            <small>{{ tactic.costLabel }}</small>
            <p>{{ tactic.hint }}</p>
          </button>
        </section>

        <div class="combat-feedback" :class="lastOutcome?.quality || 'idle'">
          <strong>{{ lastOutcome?.title || '等待判断' }}</strong>
          <span>{{ lastOutcome?.text || '每一轮只选择一次。结果会立即扣除临时资源，并影响最终评价。' }}</span>
        </div>
      </section>

      <section v-else class="patrol-summary" :class="grade.id">
        <div class="summary-seal">{{ grade.badge }}</div>
        <div>
          <p>巡查评价</p>
          <h4>{{ grade.label }}</h4>
          <span>{{ grade.text }}</span>
        </div>
        <dl>
          <div><dt>判断得分</dt><dd>{{ score }}</dd></div>
          <div><dt>正确应对</dt><dd>{{ perfectCount }}/3</dd></div>
          <div><dt>结算损伤</dt><dd>-{{ grade.hpCost }} HP</dd></div>
          <div><dt>行动消耗</dt><dd>-{{ grade.staminaCost }} 体力 · -{{ grade.mpCost }} 神圣力</dd></div>
          <div><dt>带回标记</dt><dd>+{{ grade.marks }}</dd></div>
        </dl>
        <p class="summary-note">服务器会按这项评价执行最终资源与关系结算；夜间休息会恢复生命、神圣力和体力。</p>
      </section>

      <footer class="patrol-actions">
        <button v-if="!finished" type="button" class="ghost" :disabled="busy || roundIndex === 0" @click="reset">
          重新巡查
        </button>
        <button v-else type="button" class="ghost" :disabled="busy" @click="reset">重新判断</button>
        <button v-if="finished" type="button" class="primary" :disabled="busy" @click="completePatrol">
          带着记录返回
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
  player: { type: Object, default: null },
  busy: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'complete'])

const encounters = [
  {
    id: 'fang_rush', zone: '门外石道', title: '刃爪兽压低前肢', intent: '正面冲撞',
    telegraph: '肩部下沉，后足正在蓄力。', description: '它没有立刻扑来，而是在等你先失去重心。',
    counter: 'guard', danger: 28, tone: 'amber'
  },
  {
    id: 'hollow_channel', zone: '静默林缘', title: '空壳兽聚拢暗色光素', intent: '聚能咏唱',
    telegraph: '周围风声向它胸口收束。', description: '神圣术成形以前，还有一次打断核心的机会。',
    counter: 'arts', danger: 46, tone: 'violet'
  },
  {
    id: 'vine_sweep', zone: '断裂路标', title: '荆棘根系贴地张开', intent: '范围横扫',
    telegraph: '根须从左右同时抬起，中间出现短暂空隙。', description: '硬接会被缠住，真正安全的位置正在攻击范围之内。',
    counter: 'dash', danger: 64, tone: 'cyan'
  }
]

const tactics = [
  { id: 'guard', label: '架势格挡', counterLabel: '克制：冲撞', stamina: 6, mp: 0, costLabel: '-6 体力', hint: '稳住重心，用剑脊把正面冲击导向地面。' },
  { id: 'arts', label: '神圣术·束光', counterLabel: '克制：聚能', stamina: 2, mp: 10, costLabel: '-2 体力 · -10 神圣力', hint: '在咏唱完成前束定光素核心，安全但消耗神圣力。' },
  { id: 'dash', label: '侧步突进', counterLabel: '克制：横扫', stamina: 10, mp: 0, costLabel: '-10 体力', hint: '从攻击范围内切入空隙，风险和收益都更直接。' }
]

const roundIndex = ref(0)
const score = ref(0)
const marks = ref(0)
const perfectCount = ref(0)
const localHp = ref(100)
const localMp = ref(100)
const localStamina = ref(100)
const finished = ref(false)
const lastOutcome = ref(null)
const combatLog = ref([])

const maxHp = computed(() => Number(props.player?.max_hp || 100))
const maxMp = computed(() => Number(props.player?.max_mp || 100))
const maxStamina = computed(() => Number(props.player?.max_stamina || 100))
const currentEncounter = computed(() => encounters[Math.min(roundIndex.value, encounters.length - 1)])
const hpPercent = computed(() => Math.max(0, Math.round((localHp.value / maxHp.value) * 100)))
const mpPercent = computed(() => Math.max(0, Math.round((localMp.value / maxMp.value) * 100)))
const staminaPercent = computed(() => Math.max(0, Math.round((localStamina.value / maxStamina.value) * 100)))

const grade = computed(() => {
  if (score.value >= 82 && perfectCount.value >= 2) {
    return { id: 'clean_clear', badge: 'S', label: '无伤完成巡查', text: '你读懂了大部分敌意，路线、资源和撤退点都保持完整。', hpCost: 0, staminaCost: 14, mpCost: 8, marks: 3 }
  }
  if (score.value >= 48 && localHp.value > 20) {
    return { id: 'scraped_clear', badge: 'B', label: '带伤完成巡查', text: '判断并不完美，但你们带回了足够让下一次行动更安全的记录。', hpCost: 8, staminaCost: 20, mpCost: 5, marks: 2 }
  }
  return { id: 'forced_retreat', badge: 'R', label: '保住记录并撤退', text: '路线没有走完。你保住唯一确认的标记，把失误变成可复查的警告。', hpCost: 14, staminaCost: 12, mpCost: 0, marks: 1 }
})

function canUse(tactic) {
  return localStamina.value >= tactic.stamina && localMp.value >= tactic.mp && localHp.value > 1
}

function matchup(encounter, tactic) {
  if (encounter.counter === tactic.id) {
    return { quality: 'perfect', title: '判断正确', text: '敌意被完整克制，没有受到伤害。', score: 34, damage: 0, marks: 2 }
  }
  const neutral = (
    (encounter.counter === 'guard' && tactic.id === 'dash') ||
    (encounter.counter === 'arts' && tactic.id === 'dash') ||
    (encounter.counter === 'dash' && tactic.id === 'arts')
  )
  if (neutral) {
    return { quality: 'steady', title: '勉强接住', text: '行动有效，但没有完全读懂敌方意图。', score: 18, damage: 4, marks: 1 }
  }
  return { quality: 'danger', title: '判断失误', text: '你的动作被敌意反制，损伤和噪声同时上升。', score: 8, damage: 9, marks: 0 }
}

function chooseTactic(tactic) {
  if (props.busy || finished.value || !canUse(tactic)) return
  const encounter = currentEncounter.value
  const outcome = matchup(encounter, tactic)
  localStamina.value = Math.max(0, localStamina.value - tactic.stamina)
  localMp.value = Math.max(0, localMp.value - tactic.mp)
  localHp.value = Math.max(1, localHp.value - outcome.damage)
  score.value += outcome.score
  marks.value += outcome.marks
  if (outcome.quality === 'perfect') perfectCount.value += 1
  lastOutcome.value = outcome
  combatLog.value = [...combatLog.value, { encounter: encounter.id, tactic: tactic.id, ...outcome }]
  if (roundIndex.value >= encounters.length - 1 || localHp.value <= 1) {
    finished.value = true
    const finalGrade = grade.value
    // Round-by-round values explain the immediate tactics. Once the route ends,
    // switch to the authoritative grade preview so the displayed totals exactly
    // match the backend settlement the player is about to confirm.
    localHp.value = Math.max(1, Number(props.player?.hp || 100) - finalGrade.hpCost)
    localMp.value = Math.max(0, Number(props.player?.mp || 100) - finalGrade.mpCost)
    localStamina.value = Math.max(0, Number(props.player?.stamina || 100) - finalGrade.staminaCost)
    marks.value = finalGrade.marks
    return
  }
  roundIndex.value += 1
}

function reset() {
  roundIndex.value = 0
  score.value = 0
  marks.value = 0
  perfectCount.value = 0
  localHp.value = Number(props.player?.hp || 100)
  localMp.value = Number(props.player?.mp || 100)
  localStamina.value = Number(props.player?.stamina || 100)
  finished.value = false
  lastOutcome.value = null
  combatLog.value = []
}

function completePatrol() {
  if (props.busy || !finished.value) return
  emit('complete', {
    choice_id: grade.value.id,
    result: {
      id: grade.value.id,
      label: grade.value.label,
      score: score.value,
      perfect_count: perfectCount.value,
      marks: grade.value.marks,
      hp_cost: grade.value.hpCost,
      stamina_cost: grade.value.staminaCost,
      mp_cost: grade.value.mpCost,
      combat_log: combatLog.value
    }
  })
}

function close() {
  if (props.busy) return
  emit('update:modelValue', false)
}

watch(() => props.modelValue, (open) => {
  if (open) reset()
})
</script>

<style scoped>
.patrol-backdrop { position: fixed; inset: 0; z-index: 89; display: flex; align-items: center; justify-content: center; padding: 1rem; background: rgba(2, 7, 16, .84); backdrop-filter: blur(7px); }
.patrol-panel { width: min(96vw, 880px); max-height: min(92vh, 820px); overflow: auto; padding: 1.2rem; border-radius: 18px; color: #f8fafc; background: linear-gradient(155deg, rgba(24, 36, 45, .99), rgba(6, 12, 22, .99)); border: 1px solid rgba(103, 232, 249, .28); box-shadow: 0 28px 74px rgba(0,0,0,.64), 0 0 30px rgba(34,211,238,.08); }
.patrol-header { display: flex; justify-content: space-between; gap: .8rem; padding-bottom: .72rem; border-bottom: 1px solid rgba(148,163,184,.16); }
.patrol-kicker { margin: 0 0 .18rem; color: #67e8f9; font-size: .64rem; font-weight: 900; letter-spacing: .14em; }
.patrol-header h3 { margin: 0; color: #ecfeff; font-size: 1.42rem; }
.patrol-close { width: 2.4rem; height: 2.4rem; border-radius: 9px; border: 1px solid rgba(148,163,184,.24); background: rgba(30,41,59,.72); color: #e2e8f0; font-size: 1.3rem; cursor: pointer; }
.patrol-desc { margin: .8rem 0; color: #cbd5e1; line-height: 1.6; }
.patrol-vitals { display: grid; grid-template-columns: repeat(4, 1fr); gap: .55rem; }
.vital-card { display: grid; grid-template-columns: 1fr auto; gap: .28rem .5rem; padding: .62rem .7rem; border-radius: 11px; background: rgba(15,23,42,.72); border: 1px solid rgba(148,163,184,.15); }
.vital-card span { color: #94a3b8; font-size: .72rem; font-weight: 800; }
.vital-card strong { font-size: .84rem; }
.vital-card i { grid-column: 1 / -1; height: .28rem; overflow: hidden; border-radius: 999px; background: rgba(2,6,23,.8); }
.vital-card i b { display: block; height: 100%; border-radius: inherit; background: #22c55e; transition: width .25s ease; }
.vital-card.mp i b { background: #38bdf8; }.vital-card.stamina i b { background: #fbbf24; }
.vital-card.marks { align-content: center; border-color: rgba(103,232,249,.24); }.vital-card.marks strong { color: #67e8f9; font-size: 1.1rem; }.vital-card.marks small { grid-column: 1 / -1; color: #64748b; }
.encounter-board { margin-top: .8rem; }
.route-progress { display: flex; align-items: center; gap: .4rem; margin-bottom: .55rem; }.route-progress span { width: 1.8rem; height: 1.8rem; display: grid; place-items: center; border-radius: 50%; color: #64748b; background: rgba(15,23,42,.8); border: 1px solid rgba(148,163,184,.18); font-weight: 900; }.route-progress span.active { color: #07111d; background: #67e8f9; box-shadow: 0 0 16px rgba(103,232,249,.28); }.route-progress span.done { color: #d9f99d; border-color: rgba(163,230,53,.4); }.route-progress strong { margin-left: auto; color: #a5f3fc; }
.threat-card { padding: .9rem 1rem; border-radius: 13px; background: linear-gradient(145deg, rgba(30,41,59,.92), rgba(15,23,42,.92)); border: 1px solid rgba(251,191,36,.25); }.threat-card.violet { border-color: rgba(192,132,252,.32); }.threat-card.cyan { border-color: rgba(34,211,238,.34); }
.threat-topline { display: flex; justify-content: space-between; color: #94a3b8; font-size: .72rem; font-weight: 800; }.threat-topline b { color: #fbbf24; }.threat-card h4 { margin: .42rem 0 .25rem; font-size: 1.2rem; color: #f8fafc; }.threat-card > p { margin: 0; color: #cbd5e1; }
.enemy-intent { display: grid; grid-template-columns: auto 1fr; gap: .16rem .65rem; margin-top: .72rem; padding: .58rem .7rem; border-left: 3px solid #fb7185; background: rgba(127,29,29,.15); }.enemy-intent span { color: #fda4af; font-size: .68rem; font-weight: 900; letter-spacing: .08em; }.enemy-intent strong { color: #fff1f2; }.enemy-intent small { grid-column: 2; color: #fecdd3; }
.counter-hint { margin: .55rem 0; color: #cbd5e1; font-size: .78rem; }.counter-hint span { margin-right: .45rem; color: #67e8f9; font-weight: 900; }
.tactic-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: .55rem; }.tactic-grid button { min-height: 8rem; padding: .72rem; text-align: left; border-radius: 12px; color: #e2e8f0; background: rgba(15,23,42,.78); border: 1px solid rgba(148,163,184,.18); cursor: pointer; transition: transform .15s ease, border-color .15s ease; }.tactic-grid button:hover:not(:disabled) { transform: translateY(-2px); border-color: rgba(103,232,249,.55); }.tactic-grid button:disabled { opacity: .38; cursor: not-allowed; }.tactic-grid strong,.tactic-grid small,.tactic-grid p { display: block; }.tactic-kicker { color: #67e8f9; font-size: .66rem; font-weight: 900; }.tactic-grid strong { margin-top: .28rem; color: #f8fafc; }.tactic-grid small { margin-top: .2rem; color: #fbbf24; }.tactic-grid p { margin: .42rem 0 0; color: #94a3b8; font-size: .76rem; line-height: 1.45; }
.combat-feedback { display: flex; gap: .6rem; margin-top: .6rem; padding: .58rem .7rem; border-radius: 10px; background: rgba(15,23,42,.72); color: #94a3b8; }.combat-feedback strong { flex: 0 0 auto; color: #e2e8f0; }.combat-feedback.perfect strong { color: #bef264; }.combat-feedback.steady strong { color: #fde68a; }.combat-feedback.danger strong { color: #fda4af; }
.patrol-summary { display: grid; grid-template-columns: auto 1fr; gap: .8rem 1rem; margin-top: .9rem; padding: 1rem; border-radius: 14px; background: rgba(15,23,42,.78); border: 1px solid rgba(103,232,249,.28); }.summary-seal { width: 4rem; height: 4rem; display: grid; place-items: center; border-radius: 13px; background: linear-gradient(145deg,#164e63,#0891b2); color: #ecfeff; font-size: 2rem; font-weight: 950; box-shadow: 0 0 22px rgba(34,211,238,.18); }.patrol-summary.scraped_clear .summary-seal { background: linear-gradient(145deg,#713f12,#d97706); }.patrol-summary.forced_retreat .summary-seal { background: linear-gradient(145deg,#7f1d1d,#be123c); }.patrol-summary p { margin: 0; color: #67e8f9; font-size: .7rem; font-weight: 900; }.patrol-summary h4 { margin: .15rem 0 .28rem; font-size: 1.3rem; }.patrol-summary span { color: #cbd5e1; }.patrol-summary dl { grid-column: 1 / -1; display: grid; grid-template-columns: repeat(5, 1fr); gap: .45rem; margin: 0; }.patrol-summary dl div { padding: .5rem; border-radius: 9px; background: rgba(2,6,23,.42); }.patrol-summary dt { color: #64748b; font-size: .66rem; }.patrol-summary dd { margin: .18rem 0 0; color: #f8fafc; font-weight: 900; font-size: .78rem; }.summary-note { grid-column: 1 / -1; color: #94a3b8 !important; font-weight: 500 !important; line-height: 1.5; }
.patrol-actions { display: flex; justify-content: flex-end; gap: .55rem; margin-top: .8rem; }.patrol-actions button { min-height: 2.7rem; padding: .55rem 1rem; border-radius: 9px; cursor: pointer; }.patrol-actions .ghost { color: #cbd5e1; background: rgba(30,41,59,.62); border: 1px solid rgba(148,163,184,.2); }.patrol-actions .primary { color: #06202a; font-weight: 950; background: linear-gradient(180deg,#a5f3fc,#22d3ee); border: 0; box-shadow: 0 0 18px rgba(34,211,238,.2); }
@media (max-width: 720px) { .patrol-panel { padding: .9rem; }.patrol-vitals { grid-template-columns: repeat(2, 1fr); }.tactic-grid { grid-template-columns: 1fr; }.tactic-grid button { min-height: auto; }.patrol-summary dl { grid-template-columns: repeat(2, 1fr); }.patrol-header h3 { font-size: 1.15rem; } }
</style>
