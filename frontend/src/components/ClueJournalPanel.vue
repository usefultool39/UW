<template>
  <div v-show="modelValue" class="journal-shell" role="dialog" aria-modal="false">
    <section class="journal-panel" @click.stop>
      <header class="journal-header">
        <div>
          <p class="journal-kicker">线索手册</p>
          <h3>{{ activeTab === 'codex' ? '已经被记住的事' : '今天留下的痕迹' }}</h3>
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

      <nav class="journal-tabs" aria-label="手册分区">
        <button
          type="button"
          class="journal-tab"
          :class="{ active: activeTab === 'journal' }"
          :aria-selected="activeTab === 'journal'"
          @click="activeTab = 'journal'"
        >
          线索手册
        </button>
        <button
          type="button"
          class="journal-tab"
          :class="{ active: activeTab === 'codex' }"
          :aria-selected="activeTab === 'codex'"
          @click="activeTab = 'codex'"
        >
          记忆图鉴
          <span v-if="codexProgress.total" class="tab-count">{{ codexProgress.completed }}/{{ codexProgress.total }}</span>
        </button>
      </nav>

      <div v-if="activeTab === 'journal'" class="journal-grid">
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
          <h4>序章三幕</h4>
          <p v-if="!storyActs.length" class="journal-empty">序章主线还在同步。完成当前关键事件后，这里会显示后续目标。</p>
          <template v-else>
            <article
              v-for="act in storyActs"
              :key="act.id"
              class="journal-entry month-plan-entry"
              :class="`status-${act.status || 'upcoming'}`"
            >
              <span class="entry-status">{{ act.status_label }}</span>
              <strong>{{ act.title }}</strong>
              <p>{{ act.summary }}</p>
              <div class="milestone-list">
                <div
                  v-for="milestone in act.milestones"
                  :key="milestone.id"
                  class="milestone-row"
                >
                  <span class="status-dot" :class="`dot-${milestone.status}`"></span>
                  <span class="milestone-title">{{ milestone.title }}</span>
                  <small>{{ milestone.day_label }} · {{ milestone.status_label }}</small>
                </div>
              </div>
            </article>
          </template>
        </section>
      </div>

      <div v-else class="codex-view">
        <div v-if="!codexData" class="journal-empty codex-loading">记忆图鉴正在从村庄记录同步……</div>
        <template v-else>
          <section class="codex-summary" aria-label="记忆图鉴进度">
            <div>
              <span class="codex-kicker">记忆回廊 · 当前存档</span>
              <strong>你已经留下 {{ codexProgress.completed }} / {{ codexProgress.total }} 条可追溯记录</strong>
            </div>
            <div class="codex-progress" aria-label="图鉴完成度">
              <span :style="{ width: `${codexProgress.percent}%` }"></span>
            </div>
            <small>{{ codexProgress.percent }}% · 完成度来自服务器状态，不会写入浏览器</small>
          </section>

          <div class="codex-grid">
            <section class="codex-column codex-wide">
              <h4>主线节点</h4>
              <p v-if="!codexMainline.length" class="journal-empty">还没有可展示的主线记录。</p>
              <article
                v-for="entry in codexMainline"
                :key="entry.id"
                class="codex-card"
                :class="[`codex-${entry.status}`, { 'is-locked': entry.status === 'locked' }]"
              >
                <span class="entry-status">{{ codexStatusLabel(entry.status) }}</span>
                <strong>{{ entry.status === 'locked' ? '未解锁记忆' : entry.title }}</strong>
                <p v-if="entry.status !== 'locked'">{{ entry.description }}</p>
                <p v-else class="codex-condition">解锁条件：{{ entry.condition }}</p>
                <small v-if="entry.status !== 'locked'">{{ entry.day ? `第 ${entry.day} 天 · ` : '' }}{{ entry.completed ? '已写入主线' : entry.condition }}</small>
              </article>
            </section>

            <section class="codex-column">
              <h4>石碑碎片</h4>
              <div class="fragment-grid">
                <article
                  v-for="entry in codexFragments"
                  :key="entry.id"
                  class="codex-card fragment-card"
                  :class="{ collected: entry.collected, 'is-locked': !entry.collected }"
                >
                  <span class="fragment-silhouette" aria-hidden="true">{{ entry.collected ? '✦' : '？' }}</span>
                  <div>
                    <span class="entry-status">{{ entry.collected ? '已收集' : '未发现' }}</span>
                    <strong>{{ entry.collected ? entry.title : '未知石碑碎片' }}</strong>
                    <p>{{ entry.collected ? entry.description : entry.condition }}</p>
                  </div>
                </article>
              </div>
            </section>

            <section class="codex-column">
              <h4>活动记录</h4>
              <article
                v-for="entry in codexActivities"
                :key="entry.id"
                class="codex-card activity-card"
                :class="{ 'is-locked': entry.status === 'locked' }"
              >
                <span class="entry-status">{{ entry.category }} · {{ codexStatusLabel(entry.status) }}</span>
                <strong>{{ entry.status === 'locked' ? '未解锁活动记录' : entry.title }}</strong>
                <p v-if="entry.completed">完成 {{ entry.count }} 次<span v-if="entry.choices.length"> · {{ entry.choices.join(' / ') }}</span></p>
                <p v-else>解锁条件：{{ entry.condition }}</p>
                <small v-if="entry.last_day">最近记录：第 {{ entry.last_day }} 天</small>
              </article>
            </section>

            <section class="codex-column codex-wide">
              <h4>NPC 记忆与关系里程碑</h4>
              <p v-if="!codexNpcs.length" class="journal-empty">还没有可回看的 NPC 记忆。</p>
              <div class="npc-codex-grid">
                <article v-for="npc in codexNpcs" :key="npc.npc_id" class="codex-card npc-codex-card">
                  <header>
                    <strong>{{ npc.npc }}</strong>
                    <small>好感 {{ npc.relationship.affinity }} · 信任 {{ npc.relationship.trust }} · 紧张 {{ npc.relationship.tension }}</small>
                  </header>
                  <div v-if="npc.memories.length" class="npc-memory-list">
                    <p v-for="memory in npc.memories.slice(0, 3)" :key="`${npc.npc_id}:${memory.recorded_at || memory.summary}`">{{ memory.summary }}</p>
                  </div>
                  <p v-else class="codex-muted">关键记忆尚未形成。</p>
                  <div class="milestone-chip-list">
                    <span
                      v-for="milestone in npc.milestones"
                      :key="milestone.id"
                      class="milestone-chip"
                      :class="{ unlocked: milestone.unlocked }"
                      :title="milestone.unlocked ? milestone.label : `解锁条件：${milestone.condition}`"
                    >
                      {{ milestone.unlocked ? milestone.label : '未解锁里程碑' }}
                    </span>
                  </div>
                </article>
              </div>
            </section>
          </div>
        </template>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  getAgentLabel,
  getSceneLabel,
  getStoryEventHint,
  getFlagClueHint
} from '../field/gameContentConfig.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  simState: { type: Object, default: null },
  codex: { type: Object, default: null },
  storyEvents: { type: Array, default: () => [] },
  recentMemories: { type: Array, default: () => [] },
  npcProfiles: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['update:modelValue'])
const activeTab = ref('journal')

const codexData = computed(() => props.codex || props.simState?.codex || null)
const codexProgress = computed(() => codexData.value?.progress || { completed: 0, total: 0, percent: 0 })
const codexMainline = computed(() => Array.isArray(codexData.value?.mainline) ? codexData.value.mainline : [])
const codexFragments = computed(() => Array.isArray(codexData.value?.fragments) ? codexData.value.fragments : [])
const codexActivities = computed(() => Array.isArray(codexData.value?.activities) ? codexData.value.activities : [])
const codexNpcs = computed(() => Array.isArray(codexData.value?.npcs) ? codexData.value.npcs : [])

function codexStatusLabel(status) {
  return { completed: '已完成', available: '待记录', locked: '待解锁', hidden: '未发现' }[status] || '未记录'
}

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

const ACT_DEFS = [
  {
    id: 'act_0',
    title: '第一幕 · 日常',
    summary: '卢利特村的清晨、巨神树的天职，与禁忌目录的夜晚。',
    day_label: '第 1 天',
    events: ['ch1pc_n01_rulid_daily', 'ch1pc_n02_gigas_calling', 'ch1pc_n03_talk_index_end_mountains']
  },
  {
    id: 'act_1',
    title: '第二幕 · 越界',
    summary: '出发前往尽头山脉，接触受伤者，爱丽丝跨过界线，三人返村。',
    day_label: '第 2 天',
    events: ['ch1pc_n04_travel_to_end_mountains', 'ch1pc_n05_encounter_dark_territory_injured', 'ch1pc_n06_alice_crosses_boundary', 'ch1pc_n07_return_to_rulid']
  },
  {
    id: 'act_2',
    title: '第三幕 · 宣判与告别',
    summary: '整合骑士进村宣判，爱丽丝告别，最终被带走。',
    day_label: '第 3 天',
    events: ['ch1pc_n08_knights_arrive_village', 'ch1pc_n09_alice_farewell', 'ch1pc_n10_alice_captured']
  }
]

function actStatusFor(act, doneIds) {
  const done = act.events.filter((id) => doneIds.has(id)).length
  const total = act.events.length
  if (done >= total) return { status: 'completed', label: '已完成' }
  if (done > 0) return { status: 'active', label: '推进中' }
  return { status: 'upcoming', label: '未开始' }
}

const storyActs = computed(() => {
  const doneIds = new Set(
    Array.isArray(props.simState?.completed_event_ids)
      ? props.simState.completed_event_ids
      : []
  )
  return ACT_DEFS.map((act) => {
    const { status, label } = actStatusFor(act, doneIds)
    return {
      ...act,
      status,
      status_label: label,
      milestones: act.events.map((eventId) => {
        const isDone = doneIds.has(eventId)
        return {
          id: eventId,
          title: eventId.replace('ch1pc_', ''),
          day_label: act.day_label,
          status: isDone ? 'completed' : 'upcoming',
          status_label: isDone ? '已完成' : '未开始'
        }
      })
    }
  })
})

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


.journal-tabs {
  display: flex;
  gap: 0.45rem;
  margin-top: 0.7rem;
  padding: 0.22rem;
  border-radius: 10px;
  background: rgba(8, 16, 28, 0.68);
  border: 1px solid rgba(148, 163, 184, 0.15);
}

.journal-tab {
  min-height: 2rem;
  padding: 0.28rem 0.68rem;
  border: 1px solid transparent;
  border-radius: 8px;
  color: #a9bdd0;
  background: transparent;
  font-size: 0.78rem;
  font-weight: 900;
  cursor: pointer;
}

.journal-tab.active {
  color: #332414;
  background: linear-gradient(180deg, #ffe6a6, #d99545);
  border-color: rgba(255, 247, 214, 0.72);
}

.tab-count {
  margin-left: 0.25rem;
  opacity: 0.78;
  font-size: 0.68rem;
}

.codex-view {
  margin-top: 0.78rem;
}

.codex-summary {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(170px, 280px);
  gap: 0.28rem 0.85rem;
  align-items: center;
  padding: 0.72rem 0.78rem;
  border-radius: 11px;
  background: linear-gradient(135deg, rgba(62, 49, 28, 0.72), rgba(12, 28, 38, 0.72));
  border: 1px solid rgba(246, 211, 110, 0.24);
}

.codex-kicker {
  display: block;
  color: #f6d36e;
  font-size: 0.66rem;
  font-weight: 900;
  letter-spacing: 0.1em;
}

.codex-summary strong {
  display: block;
  margin-top: 0.16rem;
  color: #fff7d6;
  font-size: 0.9rem;
}

.codex-summary small {
  grid-column: 1 / -1;
  color: #a9bdd0;
  font-size: 0.68rem;
}

.codex-progress {
  height: 0.48rem;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.codex-progress span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #67e8f9, #f6d36e);
  transition: width 220ms ease;
}

.codex-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.72rem;
  margin-top: 0.72rem;
}

.codex-column { min-width: 0; }
.codex-column h4 { margin: 0 0 0.45rem; color: #bae6fd; font-size: 0.9rem; }
.codex-wide { grid-column: span 2; }

.codex-card {
  min-width: 0;
  margin-bottom: 0.48rem;
  padding: 0.6rem 0.66rem;
  border-radius: 10px;
  background: rgba(8, 16, 28, 0.62);
  border: 1px solid rgba(94, 207, 255, 0.18);
}

.codex-card.codex-completed { border-color: rgba(74, 222, 128, 0.28); }
.codex-card.codex-available { border-color: rgba(253, 224, 71, 0.28); }
.codex-card.is-locked { border-color: rgba(148, 163, 184, 0.14); background: rgba(15, 23, 42, 0.42); }
.codex-card.is-locked strong { color: #64748b; letter-spacing: 0.08em; }
.codex-card p { margin: 0.28rem 0 0; color: #dbeafe; font-size: 0.78rem; line-height: 1.48; }
.codex-card small { display: block; margin-top: 0.34rem; color: #93c5fd; font-size: 0.68rem; line-height: 1.35; }
.codex-condition { color: #a8b6c8 !important; }
.codex-muted { color: #8ca0b5 !important; }

.fragment-grid { display: grid; gap: 0.45rem; }
.fragment-card { display: grid; grid-template-columns: 2.1rem minmax(0, 1fr); gap: 0.55rem; align-items: center; }
.fragment-silhouette { display: grid; place-items: center; width: 1.85rem; height: 2.2rem; border-radius: 7px; color: #f6d36e; background: rgba(71, 85, 105, 0.48); font-size: 1.1rem; }
.fragment-card.is-locked .fragment-silhouette { color: #64748b; filter: grayscale(1); }
.fragment-card strong { font-size: 0.82rem; }

.activity-card { min-height: 4.55rem; }
.npc-codex-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.5rem; }
.npc-codex-card header { display: flex; justify-content: space-between; gap: 0.55rem; align-items: baseline; }
.npc-codex-card header strong { font-size: 0.92rem; }
.npc-codex-card header small { margin: 0; white-space: nowrap; }
.npc-memory-list { display: grid; gap: 0.24rem; margin-top: 0.42rem; }
.npc-memory-list p { margin: 0; padding-left: 0.5rem; border-left: 2px solid rgba(94, 207, 255, 0.35); }
.milestone-chip-list { display: flex; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.52rem; }
.milestone-chip { padding: 0.18rem 0.38rem; border-radius: 999px; color: #718096; background: rgba(51, 65, 85, 0.48); border: 1px solid rgba(148, 163, 184, 0.14); font-size: 0.65rem; }
.milestone-chip.unlocked { color: #d9f99d; background: rgba(74, 116, 68, 0.3); border-color: rgba(134, 239, 172, 0.25); }

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


@media (max-width: 620px) {
  .codex-summary { grid-template-columns: 1fr; }
  .codex-summary small { grid-column: auto; }
  .codex-grid { grid-template-columns: 1fr; }
  .codex-wide { grid-column: auto; }
  .npc-codex-grid { grid-template-columns: 1fr; }
  .npc-codex-card header { display: block; }
  .npc-codex-card header small { margin-top: 0.18rem; }
}
