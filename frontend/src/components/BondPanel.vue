<template>
  <div class="card bond-card">
    <div class="bond-heading">
      <div>
        <div class="card-title">关系状态</div>
        <p class="bond-hint">好感、信任与紧张会跟着每次选择留下回响。</p>
      </div>
      <span class="bond-sync" :class="{ local: !hasServerRelationships }">
        {{ hasServerRelationships ? '村庄记录' : '本地记录' }}
      </span>
    </div>

    <div class="chapter-row">
      <div class="chapter-pill">{{ chapterLabel }}</div>
      <div class="flag-row" aria-label="章节抉择进度">
        <span :class="{ ok: narrative.flags?.c1Done }">抉择① {{ narrative.flags?.c1Done ? '已完成' : '未触发' }}</span>
        <span :class="{ ok: narrative.flags?.c2Done }">抉择② {{ narrative.flags?.c2Done ? '已完成' : '未触发' }}</span>
      </div>
    </div>

    <div class="bond-legend" aria-hidden="true">
      <span><i class="legend-dot affinity" />好感</span>
      <span><i class="legend-dot trust" />信任</span>
      <span><i class="legend-dot tension" />紧张</span>
    </div>

    <div class="bond-list">
      <article v-for="row in bondRows" :key="row.id" class="bond-person">
        <div class="bond-person-head">
          <strong :style="{ color: row.color }">{{ row.name }}</strong>
          <span class="bond-note">{{ row.note }}</span>
        </div>
        <div class="bond-person-body">
          <svg class="bond-radar" viewBox="0 0 100 100" role="img" :aria-label="`${row.name}关系雷达：${row.aria}`">
            <polygon class="radar-grid" points="50,6 93,72 7,72" />
            <polygon class="radar-grid inner" points="50,25 68,53 32,53" />
            <line class="radar-axis" x1="50" y1="6" x2="50" y2="82" />
            <line class="radar-axis" x1="7" y1="72" x2="93" y2="72" />
            <polygon class="radar-value" :points="row.radarPoints" :style="{ fill: row.color }" />
          </svg>
          <div class="dimension-list">
            <div v-for="dimension in row.dimensions" :key="dimension.field" class="dimension-row">
              <span>{{ dimension.label }}</span>
              <div class="dimension-track">
                <div class="dimension-fill" :class="dimension.field" :style="{ width: `${dimension.percent}%` }" />
              </div>
              <strong>{{ dimension.valueText }}</strong>
            </div>
          </div>
        </div>
      </article>
    </div>

    <p v-if="!hasServerRelationships" class="bond-footnote">进入地图并完成一次互动后，会同步更细的三维关系记录。</p>
    <p v-if="narrative.lastSyncedRunId" class="run-id">最近同步运行编号: {{ narrative.lastSyncedRunId }}</p>
    <button type="button" class="reset-mini" @click="onResetNarrative">重置本地章节记录</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { AGENT_IDS, AGENT_META } from '../constants/agents.js'
import { relationshipPercent } from '../utils/relationshipFeedback.js'

const props = defineProps({
  narrative: { type: Object, required: true },
  simState: { type: Object, default: null },
  resetNarrative: { type: Function, required: true }
})

const hasServerRelationships = computed(() => Object.keys(props.simState?.relationships || {}).length > 0)
const chapterLabel = computed(() => props.narrative.chapterId === 'ch1' ? '第一章 · 卢利特村' : props.narrative.chapterId)

const bondRows = computed(() => {
  const relationships = props.simState?.relationships || {}
  const localBond = props.narrative?.bond || {}
  const ids = [...new Set([...AGENT_IDS, ...Object.keys(relationships), ...Object.keys(localBond)])]
  return ids.map((id) => {
    const meta = AGENT_META[id] || { display: id, color: '#8be9fd' }
    const rel = relationships[id] || {}
    const fallbackAffinity = Number(localBond[id] ?? 50) * 2 - 100
    const affinity = finite(rel.affinity) ? Number(rel.affinity) : fallbackAffinity
    const trust = finite(rel.trust) ? Number(rel.trust) : 0
    const tension = finite(rel.tension) ? Number(rel.tension) : 0
    const dimensions = [
      { field: 'affinity', label: '好感', value: affinity, percent: relationshipPercent(affinity, 'affinity') },
      { field: 'trust', label: '信任', value: trust, percent: relationshipPercent(trust, 'trust') },
      { field: 'tension', label: '紧张', value: tension, percent: relationshipPercent(tension, 'tension') }
    ]
    return {
      id,
      name: meta.display || id,
      color: meta.color || '#8be9fd',
      note: relationNote({ affinity, trust, tension }),
      dimensions: dimensions.map((dimension) => ({
        ...dimension,
        valueText: `${dimension.value > 0 ? '+' : ''}${dimension.value}`
      })),
      radarPoints: radarPoints(dimensions.map((dimension) => dimension.percent)),
      aria: dimensions.map((dimension) => `${dimension.label}${dimension.value}`).join('、')
    }
  })
})

function finite(value) {
  return Number.isFinite(Number(value))
}

function relationNote({ affinity, trust, tension }) {
  if (tension >= 45) return '明显戒备'
  if (trust >= 45) return '愿意相信你'
  if (affinity >= 35) return '对你亲近'
  if (tension >= 18) return '有些担心'
  if (trust <= -25) return '仍在怀疑'
  return '关系平稳'
}

function radarPoints(values) {
  const [affinity, trust, tension] = values.map((value) => Math.max(0, Math.min(100, Number(value) || 0)) / 100)
  const points = [
    [50, 6 + 66 * (1 - affinity)],
    [7 + 43 * (1 - trust), 72 - 66 * trust],
    [93 - 43 * (1 - tension), 72 - 66 * tension]
  ]
  return points.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ')
}

function onResetNarrative() {
  if (confirm('确定清空本地章节记录？（不影响后端游戏状态）')) props.resetNarrative()
}
</script>

<style scoped>
.bond-card { font-size: 0.8rem; }
.bond-heading, .chapter-row, .bond-person-head, .dimension-row { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.bond-heading { align-items: flex-start; }
.bond-hint { color: var(--muted); font-size: 0.72rem; line-height: 1.5; margin: 0.22rem 0 0.55rem; }
.bond-sync { flex: 0 0 auto; padding: 0.2rem 0.42rem; border: 1px solid rgba(103, 232, 249, 0.3); border-radius: 999px; color: var(--sao-cyan); font-size: 0.62rem; white-space: nowrap; }
.bond-sync.local { color: var(--muted); border-color: var(--sao-border-dim); }
.chapter-row { align-items: flex-start; margin-bottom: 0.55rem; }
.chapter-pill { display: inline-block; flex: 0 0 auto; font-size: 0.65rem; letter-spacing: 0.05em; padding: 0.2rem 0.5rem; border: 1px solid var(--sao-border-dim); border-radius: 4px; color: var(--sao-cyan); }
.flag-row { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 0.25rem 0.55rem; font-size: 0.65rem; color: var(--muted); }
.flag-row span.ok { color: var(--ok); }
.bond-legend { display: flex; gap: 0.65rem; padding: 0.42rem 0.5rem; margin-bottom: 0.55rem; border-radius: 7px; background: rgba(0, 0, 0, 0.18); color: var(--muted); font-size: 0.65rem; }
.bond-legend span { display: inline-flex; align-items: center; gap: 0.2rem; }
.legend-dot { width: 0.45rem; height: 0.45rem; border-radius: 50%; display: inline-block; }
.legend-dot.affinity { background: #67e8f9; } .legend-dot.trust { background: #86efac; } .legend-dot.tension { background: #fca5a5; }
.bond-person { padding: 0.55rem 0; border-top: 1px solid rgba(148, 163, 184, 0.12); }
.bond-person:first-child { border-top: 0; padding-top: 0; }
.bond-person-head { margin-bottom: 0.3rem; }
.bond-note { color: var(--muted); font-size: 0.65rem; }
.bond-person-body { display: grid; grid-template-columns: 74px 1fr; align-items: center; gap: 0.55rem; }
.bond-radar { width: 74px; height: 74px; overflow: visible; }
.radar-grid { fill: rgba(103, 232, 249, 0.04); stroke: rgba(148, 163, 184, 0.24); stroke-width: 1; }
.radar-grid.inner { fill: transparent; stroke: rgba(148, 163, 184, 0.14); }
.radar-axis { stroke: rgba(148, 163, 184, 0.16); stroke-width: 0.8; }
.radar-value { fill-opacity: 0.34; stroke: currentColor; stroke-width: 1.6; stroke-linejoin: round; transform-origin: center; animation: radar-in 0.45s ease both; }
.dimension-list { min-width: 0; display: grid; gap: 0.28rem; }
.dimension-row { display: grid; grid-template-columns: 2.1rem 1fr 2rem; gap: 0.32rem; justify-content: initial; font-size: 0.65rem; color: var(--muted); }
.dimension-row strong { text-align: right; color: var(--ink); font-variant-numeric: tabular-nums; font-size: 0.66rem; }
.dimension-track { height: 0.36rem; overflow: hidden; border-radius: 999px; background: rgba(0, 0, 0, 0.32); }
.dimension-fill { height: 100%; border-radius: inherit; transition: width 0.45s ease; }
.dimension-fill.affinity { background: #67e8f9; } .dimension-fill.trust { background: #86efac; } .dimension-fill.tension { background: #fca5a5; }
.bond-footnote { margin: 0.55rem 0 0; color: var(--muted); font-size: 0.65rem; line-height: 1.45; }
.run-id { margin-top: 0.45rem; font-size: 0.62rem; color: var(--muted); word-break: break-all; }
.reset-mini { margin-top: 0.65rem; width: 100%; font-size: 0.68rem; padding: 0.35rem; opacity: 0.85; }
@keyframes radar-in { from { opacity: 0; transform: scale(0.78); } to { opacity: 1; transform: scale(1); } }
@media (max-width: 900px) { .bond-person-body { grid-template-columns: 68px 1fr; } .bond-radar { width: 68px; height: 68px; } }
</style>
