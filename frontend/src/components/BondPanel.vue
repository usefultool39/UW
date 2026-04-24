<template>
  <div class="card bond-card">
    <div class="card-title">第一章 · 羁绊（本地）</div>
    <p class="bond-hint">
      关键抉择会在 <strong>回合 10+</strong> 与 <strong>回合 30 食桌</strong> 自动弹出；数值写入本地存档。
    </p>
    <div class="chapter-pill">章节 {{ narrative.chapterId === 'ch1' ? '第一章' : narrative.chapterId }}</div>
    <div class="flag-row">
      <span :class="{ ok: narrative.flags?.c1Done }">抉择① {{ narrative.flags?.c1Done ? '已完成' : '未触发' }}</span>
      <span :class="{ ok: narrative.flags?.c2Done }">抉择② {{ narrative.flags?.c2Done ? '已完成' : '未触发' }}</span>
    </div>
    <div v-for="id in AGENT_IDS" :key="id" class="bond-row">
      <span class="bond-name" :style="{ color: AGENT_META[id].color }">{{ AGENT_META[id].display }}</span>
      <div class="bond-track">
        <div
          class="bond-fill"
          :style="{ width: narrative.bond[id] + '%', background: AGENT_META[id].color }"
        />
      </div>
      <span class="bond-num">{{ narrative.bond[id] }}</span>
    </div>
    <p v-if="narrative.lastSyncedRunId" class="run-id">最近同步运行编号: {{ narrative.lastSyncedRunId }}</p>
    <button type="button" class="reset-mini" @click="onResetNarrative">重置剧情进度（仅本地）</button>
  </div>
</template>

<script setup>
import { AGENT_IDS, AGENT_META } from '../constants/agents.js'

const props = defineProps({
  narrative: { type: Object, required: true },
  resetNarrative: { type: Function, required: true }
})

function onResetNarrative() {
  if (confirm('确定清空本地羁绊、抉择记录与章节标记？（不影响后端游戏状态）')) {
    props.resetNarrative()
  }
}
</script>

<style scoped>
.bond-card {
  font-size: 0.8rem;
}

.bond-hint {
  color: var(--muted);
  font-size: 0.72rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.bond-hint strong {
  color: var(--sao-cyan);
}

.chapter-pill {
  display: inline-block;
  font-size: 0.65rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--sao-border-dim);
  border-radius: 4px;
  color: var(--sao-cyan);
  margin-bottom: 0.65rem;
}

.flag-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.7rem;
  color: var(--muted);
  margin-bottom: 0.55rem;
}

.flag-row span.ok {
  color: var(--ok);
}

.bond-row {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin-bottom: 0.4rem;
}

.bond-name {
  width: 52px;
  font-weight: 700;
  font-size: 0.75rem;
}

.bond-track {
  flex: 1;
  height: 10px;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--sao-border-dim);
}

.bond-fill {
  height: 100%;
  border-radius: 3px;
  opacity: 0.85;
  transition: width 0.35s ease;
}

.bond-num {
  width: 28px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: var(--muted);
  font-size: 0.75rem;
}

.run-id {
  margin-top: 0.45rem;
  font-size: 0.65rem;
  color: var(--muted);
  word-break: break-all;
}

.reset-mini {
  margin-top: 0.65rem;
  width: 100%;
  font-size: 0.7rem;
  padding: 0.35rem;
  opacity: 0.85;
}
</style>
