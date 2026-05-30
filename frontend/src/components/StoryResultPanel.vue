<template>
  <div
    v-show="modelValue && result"
    class="result-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="emit('update:modelValue', false)"
  >
    <section class="result-panel" :class="{ 'month-final': isMonthFinal }" @click.stop>
      <header class="result-header">
        <div>
          <p class="result-kicker">{{ resultKicker }}</p>
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

      <section v-if="emotionalSummary" class="result-aftertaste">
        {{ emotionalSummary }}
      </section>

      <section v-if="impactLines.length" class="impact-grid">
        <div v-for="line in impactLines" :key="line.label" class="impact-chip">
          <span>{{ line.label }}</span>
          <strong>{{ line.value }}</strong>
        </div>
      </section>

      <section v-if="agentImpactCards.length" class="memory-board">
        <article v-for="card in agentImpactCards" :key="card.npcId" class="memory-card">
          <div class="memory-avatar">{{ card.initial }}</div>
          <div>
            <h4>{{ card.name }}</h4>
            <p v-if="card.relationship">{{ card.relationship }}</p>
            <p v-if="card.memory">{{ card.memory }}</p>
          </div>
        </article>
      </section>

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

      <section v-if="promiseLines.length || tensionLines.length" class="result-section">
        <h4>留下的暗线</h4>
        <ul>
          <li v-for="line in promiseLines" :key="line">{{ line }}</li>
          <li v-for="line in tensionLines" :key="line">{{ line }}</li>
        </ul>
      </section>

      <section v-if="dailyEventLines.length" class="result-section">
        <h4>这一刻发生了什么</h4>
        <ul>
          <li v-for="line in dailyEventLines" :key="line">{{ line }}</li>
        </ul>
      </section>

      <section v-if="nextEventCards.length" class="next-targets">
        <h4>明天去哪里</h4>
        <article v-for="card in nextEventCards" :key="card.id" class="next-target-card">
          <div>
            <strong>{{ card.title }}</strong>
            <p>{{ card.meta }}</p>
          </div>
          <button type="button" @click="focusNextEvent(card)">查看目标</button>
        </article>
      </section>

      <section v-else-if="nextEventLines.length" class="result-section next-section">
        <h4>接下来可追的线索</h4>
        <ul>
          <li v-for="line in nextEventLines" :key="line">{{ line }}</li>
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
import { getAgentLabel, getSceneLabel, getTimeBandLabel } from '../field/gameContentConfig.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  result: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue', 'focus-event'])

const FIELD_LABELS = {
  affinity: '好感',
  trust: '信任',
  tension: '紧张'
}

const ACTION_LABELS = {
  chop: '砍伐',
  rest: '休息',
  eat: '进食',
  sleep: '睡觉',
  move: '移动',
  cook: '做饭',
  noop: '观察',
  go_home: '回家'
}

const isMonthFinal = computed(() => props.result?.event?.kind === 'month_final')

const resultKicker = computed(() => {
  if (props.result?.kind === 'daily_summary') return '时间流动'
  if (props.result?.kind === 'day_settlement') return '日结算'
  if (props.result?.kind === 'npc_intent_response') return 'NPC 回应'
  if (isMonthFinal.value) return '第一月收束'
  return props.result?.ending_id ? '章节收束' : '选择结果'
})

const resultTitle = computed(() => {
  if (props.result?.kind === 'daily_summary') return '村子继续向前走'
  if (props.result?.kind === 'day_settlement') {
    const day = Number(props.result?.day || 0)
    return day > 0 ? `第 ${day} 天开始` : '新的一天开始'
  }
  const activity = props.result?.activity?.title
  if (activity) return activity
  const choice = props.result?.choice?.label
  const eventTitle = props.result?.event?.title || props.result?.event_title
  if (isMonthFinal.value && choice) return `第二月路线 · ${choice}`
  if (choice && eventTitle) return `${eventTitle} · ${choice}`
  return choice || eventTitle || '这件事留下了痕迹'
})

const resultText = computed(() =>
  props.result?.choice?.result_text || props.result?.result_text || '这段行动已经写入今天的旅程。'
)

const emotionalSummary = computed(() => {
  if (props.result?.kind === 'daily_summary') {
    return 'NPC 不会停在原地等你：他们会工作、休息、消耗体力，也会把今天的气氛带到下一刻。'
  }
  if (props.result?.kind === 'day_settlement') {
    return '今天的行动已经结算。被记住的事会留在关系里，未解决的线索会推着明天继续发生。'
  }
  if (isMonthFinal.value) {
    return '第一个月的记录、撤退线和同伴承诺已经汇成第二月的起点。这个路线选择会改变后续远征的节奏。'
  }
  if (memoryLines.value.length && relationshipLines.value.length) {
    return '这不是一次孤立选择。有人记住了你的做法，你和他们之间的距离也变了。'
  }
  if (memoryLines.value.length) return '这件事被写进了某个人的记忆里，之后的对话会带着它。'
  if (relationshipLines.value.length) return '关系的方向发生了变化，后面的选择会踩在这次判断上。'
  return ''
})

const impactLines = computed(() => {
  const lines = []
  const timeCost = Number(props.result?.time_cost || 0)
  const treeDamage = Number(props.result?.tree_damage || 0)
  const day = Number(props.result?.day || props.result?.state?.day || 0)
  const timeBand = props.result?.time_band || props.result?.state?.time_band
  const training = props.result?.training_result
  const reading = props.result?.reading_result
  const meal = props.result?.meal_result
  const anomaly = props.result?.anomaly_result
  const final = props.result?.final_result
  const activityChoice = props.result?.activity_choice
  if (isMonthFinal.value && props.result?.choice?.label) {
    lines.push({ label: '第一月路线', value: props.result.choice.label })
  }
  if (timeCost > 0) lines.push({ label: '时间推进', value: `${timeCost} 刻` })
  if (treeDamage > 0) lines.push({ label: '巨树损伤', value: `-${treeDamage}` })
  if (training?.label) lines.push({ label: '训练表现', value: `${training.label} · ${training.score || 0}` })
  if (reading?.label) lines.push({ label: '阅读线索', value: reading.label })
  if (meal?.label) lines.push({ label: '餐桌态度', value: meal.label })
  if (anomaly?.label) lines.push({ label: '边界读数', value: `${anomaly.label} · ${anomaly.score || 0}` })
  if (anomaly?.stance) lines.push({ label: '调查态度', value: anomaly.stance })
  if (final?.label) lines.push({ label: '终局选择', value: final.label })
  if (final?.tone) lines.push({ label: '判定倾向', value: `${final.tone} · ${final.pressure || 0}` })
  if (!reading?.label && !meal?.label && activityChoice?.label) {
    lines.push({ label: '行动选择', value: activityChoice.label })
  }
  if (props.result?.kind === 'daily_summary') lines.push({ label: '模拟事件', value: `${dailyEventLines.value.length} 条` })
  if (day > 0) lines.push({ label: '当前日期', value: `Day ${day}` })
  if (timeBand) lines.push({ label: '当前时段', value: getTimeBandLabel(timeBand) })
  return lines
})

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

const promiseLines = computed(() =>
  Object.entries(props.result?.promises || {})
    .map(([npcId, text]) => `${getAgentLabel(npcId)}的承诺：${text}`)
)

const tensionLines = computed(() =>
  Object.entries(props.result?.tensions || {})
    .map(([npcId, text]) => `${getAgentLabel(npcId)}的不安：${text}`)
)

const dailyEventLines = computed(() => {
  const events = Array.isArray(props.result?.events) ? props.result.events : []
  return events.slice(0, 6).map((event) => {
    const name = event.actor_name || getAgentLabel(event.actor)
    const actionName = normalizedActionName(event.action)
    return `${name}：${dailyEventText(actionName, event.detail)}`
  })
})

function normalizedActionName(action) {
  if (action && typeof action === 'object') return action.name
  const text = String(action || '')
  if (text.startsWith('{') && text.endsWith('}')) {
    try {
      const parsed = JSON.parse(text)
      return parsed?.name || text
    } catch {
      return text
    }
  }
  return text
}

function dailyEventText(actionName, rawDetail) {
  const detail = String(rawDetail || '')
  const action = ACTION_LABELS[actionName] || actionName || '行动'
  const damage = detail.match(/dmg=(\d+)/)
  if (damage) return `${action}，巨树进度推进 ${damage[1]} 点`
  if (detail === 'cooking') return '准备饭菜，维持家里的日常'
  if (detail === 'ate') return '吃过饭，体力和情绪稍微安定下来'
  if (detail === 'sleeping') return '休息入睡，把今天留到明天继续'
  if (detail === 'resting') return '短暂休息，恢复一点余裕'
  if (detail === 'moving') return '前往下一个地点'
  if (!detail || detail === 'ok') return `${action}完成`
  return `${action}：${detail}`
}

const nextEventLines = computed(() => {
  const events = Array.isArray(props.result?.next_events) ? props.result.next_events : []
  return events.slice(0, 4).map((event) => event.title || event.id).filter(Boolean)
})

const nextEventCards = computed(() => {
  if (props.result?.kind !== 'day_settlement') return []
  const events = Array.isArray(props.result?.next_events) ? props.result.next_events : []
  return events.slice(0, 3).map((event) => {
    const loc = event?.location || {}
    const participants = Array.isArray(event?.participants) ? event.participants.map(getAgentLabel).join('、') : ''
    const scene = loc.scene_id ? getSceneLabel(loc.scene_id) : '未知地点'
    return {
      id: event.id,
      title: event.title || event.id || '新的线索',
      location: loc,
      meta: participants ? `${scene} · ${participants}` : scene
    }
  })
})

function focusNextEvent(card) {
  emit('focus-event', { event_id: card.id, location: card.location })
}

const agentImpactCards = computed(() => {
  const cards = new Map()
  const ensure = (npcId) => {
    const id = String(npcId || '')
    if (!id) return null
    if (!cards.has(id)) {
      const name = getAgentLabel(id)
      cards.set(id, {
        npcId: id,
        name,
        initial: name.slice(0, 1),
        relationship: '',
        memory: ''
      })
    }
    return cards.get(id)
  }

  for (const item of Array.isArray(props.result?.relationship_changes) ? props.result.relationship_changes : []) {
    const card = ensure(item?.npc_id)
    if (!card || Number(item?.delta || 0) === 0) continue
    const field = FIELD_LABELS[item.field] || item.field
    const delta = Number(item.delta || 0)
    const sign = delta > 0 ? '+' : ''
    card.relationship = `${field} ${sign}${delta}，现在 ${item.after}`
  }

  for (const item of Array.isArray(props.result?.memory_written) ? props.result.memory_written : []) {
    const card = ensure(item?.npc_id)
    if (!card || !item?.summary) continue
    card.memory = `记住：${item.summary}`
  }

  return [...cards.values()].filter((card) => card.relationship || card.memory)
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
  width: min(94vw, 820px);
  max-height: min(88vh, 740px);
  overflow: auto;
  padding: 1.25rem;
  border-radius: 16px;
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
  font-size: 1.45rem;
  color: #fff7d6;
  line-height: 1.35;
}

.result-close {
  flex: 0 0 auto;
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

.result-text {
  margin: 0.85rem 0;
  color: #f8fafc;
  line-height: 1.68;
  font-size: 1.05rem;
}

.result-panel.month-final {
  border-color: rgba(125, 211, 252, 0.46);
  background:
    linear-gradient(160deg, rgba(21, 37, 59, 0.98), rgba(6, 14, 26, 0.99)),
    radial-gradient(circle at 18% 0%, rgba(125, 211, 252, 0.12), transparent 36%);
  box-shadow: 0 30px 78px rgba(0, 0, 0, 0.62), 0 0 32px rgba(125, 211, 252, 0.12);
}

.result-aftertaste {
  margin: 0.75rem 0 0;
  padding: 0.62rem 0.72rem;
  border-radius: 10px;
  color: #fff7d6;
  line-height: 1.55;
  background: rgba(120, 83, 35, 0.22);
  border: 1px solid rgba(246, 211, 110, 0.24);
}

.impact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.45rem;
  margin: 0.75rem 0 0;
}

.impact-chip {
  min-height: 3rem;
  padding: 0.5rem 0.6rem;
  border-radius: 9px;
  background: rgba(6, 12, 24, 0.58);
  border: 1px solid rgba(246, 211, 110, 0.18);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.12rem;
}

.impact-chip span {
  color: #bfdbfe;
  font-size: 0.82rem;
  font-weight: 700;
}

.impact-chip strong {
  color: #fff7d6;
  font-size: 1.14rem;
}

.memory-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 0.55rem;
  margin-top: 0.78rem;
}

.memory-card {
  display: flex;
  align-items: flex-start;
  gap: 0.62rem;
  min-height: 5rem;
  padding: 0.68rem 0.72rem;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.72), rgba(51, 65, 85, 0.42));
  border: 1px solid rgba(94, 207, 255, 0.18);
}

.memory-avatar {
  flex: 0 0 auto;
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 50%;
  display: grid;
  place-items: center;
  color: #fff7d6;
  font-size: 1rem;
  font-weight: 900;
  background: radial-gradient(circle at 35% 25%, rgba(255, 255, 255, 0.28), transparent 30%), rgba(120, 83, 35, 0.9);
  border: 1px solid rgba(246, 211, 110, 0.48);
  box-shadow: 0 0 14px rgba(246, 211, 110, 0.12);
}

.memory-card h4 {
  margin: 0 0 0.26rem;
  color: #fff7d6;
  font-size: 0.95rem;
}

.memory-card p {
  margin: 0.12rem 0;
  color: #dbeafe;
  font-size: 0.86rem;
  line-height: 1.48;
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
  font-size: 0.92rem;
  color: var(--sao-cyan);
}

.next-section {
  border-color: rgba(246, 211, 110, 0.24);
  background: rgba(120, 83, 35, 0.16);
}

.next-targets {
  margin-top: 0.78rem;
  padding: 0.68rem 0.72rem;
  border-radius: 10px;
  border: 1px solid rgba(246, 211, 110, 0.28);
  background: rgba(120, 83, 35, 0.16);
}

.next-targets h4 {
  margin: 0 0 0.48rem;
  color: var(--sao-gold);
  font-size: 0.92rem;
}

.next-target-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.62rem 0;
  border-top: 1px solid rgba(246, 211, 110, 0.14);
}

.next-target-card:first-of-type {
  border-top: 0;
  padding-top: 0;
}

.next-target-card:last-of-type {
  padding-bottom: 0;
}

.next-target-card strong {
  display: block;
  color: #fff7d6;
  font-size: 0.96rem;
  line-height: 1.35;
}

.next-target-card p {
  margin: 0.18rem 0 0;
  color: #bae6fd;
  font-size: 0.84rem;
  line-height: 1.45;
}

.next-target-card button {
  flex: 0 0 auto;
  min-height: 2.25rem;
  padding: 0 0.72rem;
  border-radius: 8px;
  border: 1px solid rgba(246, 211, 110, 0.42);
  color: #fff7d6;
  background: rgba(120, 83, 35, 0.82);
  font-weight: 800;
  cursor: pointer;
}

.next-target-card button:hover {
  border-color: rgba(253, 224, 71, 0.78);
  box-shadow: 0 0 14px rgba(212, 175, 55, 0.18);
}

.result-section ul {
  margin: 0;
  padding-left: 1rem;
  color: #e2e8f0;
  font-size: 0.96rem;
  line-height: 1.6;
}

.result-primary {
  width: 100%;
  margin-top: 0.9rem;
  min-height: 3rem;
  font-size: 1rem;
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

@media (max-width: 640px) {
  .next-target-card {
    align-items: stretch;
    flex-direction: column;
  }

  .next-target-card button {
    width: 100%;
  }
}
</style>
