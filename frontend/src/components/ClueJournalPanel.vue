<template>
  <div v-show="modelValue" class="journal-shell" role="dialog" aria-modal="false">
    <section class="journal-panel" @click.stop>
      <header class="journal-header">
        <div>
          <p class="journal-kicker">线索手册</p>
          <h3>今天留下的痕迹</h3>
        </div>
        <button
          type="button"
          class="journal-close"
          aria-label="关闭"
          @click="emit('update:modelValue', false)"
        >
          ×
        </button>
      </header>

      <div class="journal-grid">
        <section class="journal-column">
          <h4>发现的线索</h4>
          <p v-if="!clueEntries.length" class="journal-empty">还没有写入明确线索。先去书库或巨树旁看看。</p>
          <template v-else>
            <article v-for="entry in clueEntries" :key="entry.key" class="journal-entry">
              <span class="entry-status">{{ entry.status }}</span>
              <strong>{{ entry.title }}</strong>
              <p>{{ entry.body }}</p>
              <small>{{ entry.meta }}</small>
            </article>
          </template>
        </section>

        <section class="journal-column">
          <h4>NPC 记住的事</h4>
          <p v-if="!memoryEntries.length" class="journal-empty">还没有人把你的选择记成关键记忆。</p>
          <template v-else>
            <article v-for="entry in memoryEntries" :key="entry.key" class="journal-entry memory">
              <span class="entry-status">{{ entry.npc }}</span>
              <p>{{ entry.summary }}</p>
              <small>{{ entry.meta }}</small>
            </article>
          </template>
        </section>

        <section class="journal-column">
          <h4>关系暗线</h4>
          <p v-if="!relationshipEntries.length" class="journal-empty">关系还很平稳。一次选择之后，这里会变得更有内容。</p>
          <template v-else>
            <article v-for="entry in relationshipEntries" :key="entry.key" class="journal-entry relation">
              <span class="entry-status">{{ entry.npc }}</span>
              <strong>{{ entry.title }}</strong>
              <p>{{ entry.body }}</p>
            </article>
          </template>
        </section>

        <section class="journal-column">
          <h4>当前承诺 / 紧张点</h4>
          <p v-if="!commitmentEntries.length" class="journal-empty">当前没有需要特别记住的承诺或紧张点。</p>
          <template v-else>
            <article v-for="entry in commitmentEntries" :key="entry.key" class="journal-entry relation">
              <span class="entry-status">{{ entry.npc }}</span>
              <strong>{{ entry.title }}</strong>
              <p>{{ entry.body }}</p>
            </article>
          </template>
        </section>

        <section class="journal-column month-column">
          <h4>{{ monthDisplayTitle(monthPlan) }}</h4>
          <p v-if="!monthWeeks.length" class="journal-empty">月度路线还在同步。完成当前关键事件后，这里会显示后续目标。</p>
          <template v-else>
            <div class="month-current">
              <span>第 {{ monthCurrent.day || 1 }} 天</span>
              <strong>{{ monthCurrent.endingLabel }}</strong>
              <p>{{ monthCurrent.endingNote }}</p>
            </div>
            <article
              v-for="week in monthWeeks"
              :key="week.id"
              class="journal-entry month-plan-entry"
              :class="`status-${week.status || 'upcoming'}`"
            >
              <span class="entry-status">{{ week.status_label || statusLabel(week.status) }}</span>
              <strong>{{ week.title }}</strong>
              <p>{{ week.summary }}</p>
              <div class="month-goals">
                <span v-for="goal in shortGoals(week.goals)" :key="goal">{{ goal }}</span>
              </div>
              <div class="milestone-list">
                <div
                  v-for="milestone in week.milestones || []"
                  :key="milestone.id"
                  class="milestone-row"
                >
                  <span class="status-dot" :class="`dot-${milestone.status || 'upcoming'}`"></span>
                  <span class="milestone-title">{{ milestone.title }}</span>
                  <small>{{ milestone.day_label }} · {{ milestone.status_label || statusLabel(milestone.status) }}</small>
                </div>
              </div>
            </article>
          </template>
        </section>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  getAgentLabel,
  getSceneLabel,
  getStoryEventHint,
  getFlagClueHint
} from '../field/gameContentConfig.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  simState: { type: Object, default: null },
  storyEvents: { type: Array, default: () => [] },
  monthPlan: { type: Object, default: null },
  recentMemories: { type: Array, default: () => [] },
  npcProfiles: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['update:modelValue'])

const clueEntries = computed(() => {
  const out = []
  const seen = new Set()
  const completed = Array.isArray(props.simState?.completed_event_ids)
    ? props.simState.completed_event_ids
    : []
  for (const eventId of completed) {
    const hint = getStoryEventHint(eventId)
    const key = `event:${eventId}`
    if (seen.has(key)) continue
    seen.add(key)
    out.push({
      key,
      status: '已完成',
      title: hint.title || eventId,
      body: hint.clue || '这条剧情已经被你推进。',
      meta: hint.scene_id ? `${getSceneLabel(hint.scene_id)} · Day ${hint.day || 1}` : `Day ${hint.day || 1}`
    })
  }

  const flags = props.simState?.flags || {}
  for (const [flag, rawValue] of Object.entries(flags)) {
    if (Number(rawValue || 0) <= 0) continue
    const hint = getFlagClueHint(flag)
    if (!hint) continue
    const key = `flag:${flag}`
    if (seen.has(key)) continue
    seen.add(key)
    out.push({
      key,
      status: '已发现',
      title: hint.title,
      body: hint.body,
      meta: hint.meta || '来自行动记录'
    })
  }

  for (const event of Array.isArray(props.storyEvents) ? props.storyEvents : []) {
    const key = `available:${event.id}`
    if (!event?.id || seen.has(`event:${event.id}`) || seen.has(key)) continue
    const loc = event.location || {}
    out.push({
      key,
      status: '待调查',
      title: event.title || '新的线索',
      body: event.description || '地图上有新的金色线索正在等待你靠近。',
      meta: loc.scene_id ? `${getSceneLabel(loc.scene_id)} · 靠近后可触发` : '靠近后可触发'
    })
  }

  return out.slice(0, 8)
})

const memoryEntries = computed(() => {
  const out = []
  const seen = new Set()

  for (const item of Array.isArray(props.recentMemories) ? props.recentMemories : []) {
    const summary = String(item?.summary || '').trim()
    const npcId = String(item?.npc_id || '')
    if (!summary || !npcId) continue
    const key = `${npcId}:${summary}`
    if (seen.has(key)) continue
    seen.add(key)
    out.push({
      key: `recent:${key}`,
      npc: getAgentLabel(npcId),
      summary,
      meta: item?.day ? `Day ${item.day}` : '刚刚写入'
    })
  }

  for (const [npcId, profile] of Object.entries(props.npcProfiles || {})) {
    const memories = Array.isArray(profile?.important_memories) ? profile.important_memories : []
    for (const item of memories.slice(0, 4)) {
      const summary = String(item?.summary || '').trim()
      if (!summary) continue
      const key = `${npcId}:${summary}`
      if (seen.has(key)) continue
      seen.add(key)
      out.push({
        key: `profile:${key}`,
        npc: getAgentLabel(npcId),
        summary,
        meta: item?.day ? `Day ${item.day}` : '重要记忆'
      })
    }
  }

  return out.slice(0, 10)
})

const relationshipEntries = computed(() => {
  const out = []
  const relationships = props.simState?.relationships || {}
  for (const [npcId, rel] of Object.entries(relationships)) {
    const affinity = Number(rel?.affinity || 0)
    const trust = Number(rel?.trust || 0)
    const tension = Number(rel?.tension || 0)
    const dominant = [
      { label: '好感', value: affinity },
      { label: '信任', value: trust },
      { label: '紧张', value: tension }
    ].sort((a, b) => Math.abs(b.value) - Math.abs(a.value))[0]
    const scoreLine = `好感 ${affinity} · 信任 ${trust} · 紧张 ${tension}`
    out.push({
      key: `rel:${npcId}`,
      npc: getAgentLabel(npcId),
      title: rel?.note || rel?.mood_note || `${dominant.label}变化最明显`,
      body: scoreLine
    })
  }

  return out.slice(0, 10)
})

const commitmentEntries = computed(() => {
  const out = []
  for (const [npcId, profile] of Object.entries(props.npcProfiles || {})) {
    for (const promise of Array.isArray(profile?.promises) ? profile.promises : []) {
      out.push({
        key: `promise:${npcId}:${promise}`,
        npc: getAgentLabel(npcId),
        title: '承诺',
        body: promise
      })
    }
    for (const tension of Array.isArray(profile?.tensions) ? profile.tensions : []) {
      out.push({
        key: `tension:${npcId}:${tension}`,
        npc: getAgentLabel(npcId),
        title: '紧张点',
        body: tension
      })
    }
  }
  return out.slice(0, 8)
})

function monthDisplayTitle(plan) {
  const title = String(plan?.title || '').trim()
  if (!title) return '月度路线'
  // Preserve the familiar first-month label used by existing players while
  // allowing later months to show their authored titles verbatim.
  return title.startsWith('第一月') ? `第一月路线 · ${title}` : title
}

const monthWeeks = computed(() =>
  Array.isArray(props.monthPlan?.weeks) ? props.monthPlan.weeks : []
)

const monthCurrent = computed(() => {
  const current = props.monthPlan?.current || {}
  const labels = {
    unresolved: '路线尚未收束',
    order: '稳守路线',
    expedition: '远征路线',
    quiet: '静默路线',
    formal_hearing: '正式边界听证',
    guarded_warning: '分层警告',
    source_pursuit: '三人源头追查',
    accountable_probe: '密封副本托管',
    public_network: '公开协作族',
    frontier_probe: '源头追查族',
    accountable_intel: '责任情报族',
    cross: '越界路线',
    hide: '隐秘路线'
  }
  const ending = String(current.ending_path || 'unresolved')
  return {
    day: current.day || props.simState?.day || 1,
    endingLabel: labels[ending] || ending,
    endingNote: current.ending_note || props.monthPlan?.summary || '继续推进当天事件，月度目标会随状态更新。'
  }
})

function statusLabel(status) {
  return {
    completed: '已完成',
    active: '可推进',
    upcoming: '未到日期',
    locked: '待解锁',
    overdue: '可补做'
  }[status] || status || '未到日期'
}

function shortGoals(goals) {
  return Array.isArray(goals) ? goals.slice(0, 2) : []
}
</script>

<style scoped>
.journal-shell {
  position: fixed;
  inset: 0;
  z-index: 74;
  pointer-events: none;
}

.journal-panel {
  position: absolute;
  top: 4.75rem;
  right: 0.85rem;
  bottom: 5.6rem;
  width: min(1180px, calc(100vw - 1.7rem));
  padding: 0.92rem;
  border-radius: 12px;
  color: #f8fafc;
  background: linear-gradient(165deg, rgba(20, 30, 44, 0.94), rgba(5, 10, 18, 0.92));
  border: 1px solid rgba(246, 211, 110, 0.32);
  box-shadow: 0 24px 58px rgba(0, 0, 0, 0.5), 0 0 24px rgba(94, 207, 255, 0.08);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  pointer-events: auto;
  overflow: auto;
}

.journal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  padding-bottom: 0.72rem;
  border-bottom: 1px solid rgba(246, 211, 110, 0.18);
}

.journal-kicker {
  margin: 0 0 0.16rem;
  color: var(--sao-gold);
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.12em;
}

.journal-header h3 {
  margin: 0;
  color: #fff7d6;
  font-size: 1.18rem;
  line-height: 1.25;
}

.journal-close {
  flex: 0 0 auto;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(51, 65, 85, 0.64);
  color: #e2e8f0;
  font-size: 1.18rem;
  line-height: 1;
  cursor: pointer;
}

.journal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.72rem;
  margin-top: 0.78rem;
}

.journal-column {
  min-width: 0;
}

.journal-column h4 {
  margin: 0 0 0.45rem;
  color: #bae6fd;
  font-size: 0.9rem;
}

.journal-empty {
  margin: 0;
  padding: 0.72rem;
  border-radius: 10px;
  color: #94a3b8;
  background: rgba(15, 23, 42, 0.52);
  border: 1px solid rgba(148, 163, 184, 0.14);
  font-size: 0.86rem;
  line-height: 1.55;
}

.journal-entry {
  min-height: 6rem;
  padding: 0.62rem 0.66rem;
  margin-bottom: 0.52rem;
  border-radius: 10px;
  background: rgba(8, 16, 28, 0.62);
  border: 1px solid rgba(246, 211, 110, 0.16);
}

.journal-entry.memory {
  border-color: rgba(94, 207, 255, 0.18);
}

.journal-entry.relation {
  border-color: rgba(167, 139, 250, 0.2);
}

.journal-entry.month-plan-entry {
  min-height: 0;
  border-color: rgba(56, 189, 248, 0.2);
}

.month-plan-entry.status-active,
.month-plan-entry.status-overdue {
  border-color: rgba(253, 224, 71, 0.36);
  box-shadow: inset 0 1px 0 rgba(253, 224, 71, 0.08);
}

.month-plan-entry.status-completed {
  border-color: rgba(74, 222, 128, 0.28);
}

.month-current {
  margin-bottom: 0.52rem;
  padding: 0.62rem 0.66rem;
  border-radius: 10px;
  color: #dbeafe;
  background: rgba(8, 16, 28, 0.72);
  border: 1px solid rgba(94, 207, 255, 0.2);
}

.month-current span {
  display: block;
  color: #93c5fd;
  font-size: 0.7rem;
  font-weight: 900;
}

.month-current strong {
  display: block;
  margin-top: 0.1rem;
  color: #fff7d6;
  font-size: 0.92rem;
}

.month-current p {
  margin: 0.28rem 0 0;
  color: #cbd5e1;
  font-size: 0.78rem;
  line-height: 1.45;
}

.month-goals {
  display: flex;
  flex-wrap: wrap;
  gap: 0.32rem;
  margin-top: 0.48rem;
}

.month-goals span {
  padding: 0.18rem 0.42rem;
  border-radius: 6px;
  color: #dbeafe;
  background: rgba(30, 41, 59, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.16);
  font-size: 0.68rem;
  font-weight: 800;
}

.milestone-list {
  display: grid;
  gap: 0.34rem;
  margin-top: 0.58rem;
}

.milestone-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 0.1rem 0.42rem;
  align-items: center;
  min-width: 0;
}

.status-dot {
  width: 0.55rem;
  height: 0.55rem;
  border-radius: 50%;
  background: #64748b;
  box-shadow: 0 0 0 2px rgba(100, 116, 139, 0.14);
}

.dot-active,
.dot-overdue {
  background: #facc15;
  box-shadow: 0 0 0 2px rgba(250, 204, 21, 0.18);
}

.dot-completed {
  background: #4ade80;
  box-shadow: 0 0 0 2px rgba(74, 222, 128, 0.18);
}

.dot-locked {
  background: #f87171;
  box-shadow: 0 0 0 2px rgba(248, 113, 113, 0.16);
}

.milestone-title {
  min-width: 0;
  overflow-wrap: anywhere;
  color: #e0f2fe;
  font-size: 0.78rem;
  font-weight: 800;
  line-height: 1.3;
}

.milestone-row small {
  grid-column: 2;
  margin: 0;
  color: #93c5fd;
  font-size: 0.68rem;
}

.entry-status {
  display: inline-flex;
  margin-bottom: 0.32rem;
  padding: 0.13rem 0.38rem;
  border-radius: 999px;
  color: #fff7d6;
  background: rgba(120, 83, 35, 0.52);
  border: 1px solid rgba(246, 211, 110, 0.24);
  font-size: 0.66rem;
  font-weight: 900;
}

.journal-entry strong {
  display: block;
  color: #fff7d6;
  font-size: 0.92rem;
  line-height: 1.35;
}

.journal-entry p {
  margin: 0.3rem 0 0;
  color: #dbeafe;
  font-size: 0.84rem;
  line-height: 1.52;
}

.journal-entry small {
  display: block;
  margin-top: 0.36rem;
  color: #93c5fd;
  font-size: 0.72rem;
  line-height: 1.35;
}

.journal-entry .milestone-row small {
  grid-column: 2;
  margin: 0;
  font-size: 0.68rem;
}

@media (max-width: 900px) {
  .journal-panel {
    top: 3.2rem;
    left: 0.55rem;
    right: 0.55rem;
    bottom: 4.75rem;
    width: auto;
    padding: 0.76rem;
  }

  .journal-grid {
    grid-template-columns: 1fr;
    gap: 0.6rem;
  }

  .journal-entry {
    min-height: auto;
  }
}
</style>
