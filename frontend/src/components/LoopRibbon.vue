<template>
  <section class="loop-ribbon" aria-label="行动循环与关系回响">
    <div class="loop-head">
      <div>
        <span class="loop-kicker">本轮怎么推进</span>
        <strong>{{ loopTitle }}</strong>
      </div>
      <span class="runtime-chip" :title="runtimeTitle">{{ runtimeLabel }}</span>
    </div>
    <div class="loop-steps" aria-label="短循环步骤">
      <span v-for="(step, index) in steps" :key="step" :class="{ active: index === 0 }">
        <b>{{ index + 1 }}</b>{{ step }}
      </span>
    </div>
    <div class="loop-foot">
      <span class="echo-label">关系回响</span>
      <span class="echo-copy">{{ relationshipHint }}</span>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { getAgentLabel } from '../field/gameContentConfig.js'

const props = defineProps({
  simState: { type: Object, default: null },
  storyEvents: { type: Array, default: () => [] },
  npcRuntime: { type: String, default: 'scripted' }
})

const runtimeMeta = {
  scripted: ['固定 NPC', '固定对话与规则驱动，完整离线可玩'],
  hybrid: ['混合 NPC', '关键剧情固定，普通表达可扩展'],
  agent: ['智能体 NPC', '智能体只提议，世界规则最终裁决']
}

const runtimeLabel = computed(() => runtimeMeta[props.npcRuntime]?.[0] || runtimeMeta.scripted[0])
const runtimeTitle = computed(() => runtimeMeta[props.npcRuntime]?.[1] || runtimeMeta.scripted[1])
const loopTitle = computed(() => props.storyEvents.length ? '一条线索，做一次判断' : '行动、消耗、结算')
const steps = computed(() => props.storyEvents.length
  ? ['跟随金色线索', '做出选择', '看见关系变化']
  : ['选择地点行动', '管理 HP / MP / ST', '回到日程结算'])

const relationshipHint = computed(() => {
  const relationships = props.simState?.relationships || {}
  const intents = Array.isArray(props.simState?.npc_intents) ? props.simState.npc_intents : []
  const intent = intents[0]
  if (intent?.npc_id) return `${getAgentLabel(intent.npc_id)}正在等你的回应`
  const entry = Object.entries(relationships)
    .map(([id, rel]) => ({ id, score: Math.abs(Number(rel?.trust || 0)) + Math.abs(Number(rel?.affinity || 0)) + Math.abs(Number(rel?.tension || 0)) }))
    .sort((a, b) => b.score - a.score)[0]
  if (entry?.score) return `${getAgentLabel(entry.id)}会记住你这次的选择`
  return '每次回应都会写入信任、记忆和后续线索'
})
</script>

<style scoped>
.loop-ribbon {
  position: absolute;
  z-index: 39;
  left: 0.8rem;
  top: 18.8rem;
  width: min(330px, calc(100% - 1.5rem));
  padding: 0.55rem 0.64rem 0.62rem;
  border: 1px solid rgba(125, 211, 252, 0.22);
  border-radius: 9px;
  color: #e6f7ff;
  background: linear-gradient(135deg, rgba(8, 20, 30, 0.84), rgba(18, 31, 32, 0.68));
  box-shadow: 0 8px 20px rgba(2, 6, 23, 0.24), inset 2px 0 0 rgba(125, 211, 252, 0.52);
  pointer-events: none;
  backdrop-filter: blur(8px);
}
.loop-head { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.loop-kicker, .echo-label { display: block; color: #7dd3fc; font-size: 0.58rem; font-weight: 900; letter-spacing: 0.1em; }
.loop-head strong { display: block; margin-top: 0.12rem; color: #fff7df; font-size: 0.8rem; }
.runtime-chip { flex: 0 0 auto; padding: 0.2rem 0.38rem; border: 1px solid rgba(246, 211, 110, 0.28); border-radius: 999px; color: #ffe8a7; background: rgba(111, 75, 28, 0.25); font-size: 0.58rem; font-weight: 900; }
.loop-steps { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.28rem; margin-top: 0.52rem; }
.loop-steps span { display: flex; align-items: center; gap: 0.2rem; min-width: 0; padding: 0.27rem 0.28rem; border-radius: 5px; color: #b8c9d2; background: rgba(15, 23, 42, 0.4); font-size: 0.58rem; line-height: 1.15; }
.loop-steps span.active { color: #fff7df; background: rgba(14, 116, 144, 0.26); }
.loop-steps b { color: #f6d36e; font-size: 0.62rem; }
.loop-foot { display: flex; align-items: baseline; gap: 0.35rem; margin-top: 0.42rem; padding-top: 0.38rem; border-top: 1px solid rgba(255, 239, 198, 0.12); }
.echo-label { flex: 0 0 auto; color: #f6d36e; letter-spacing: 0.06em; }
.echo-copy { overflow: hidden; color: #dbeafe; font-size: 0.62rem; text-overflow: ellipsis; white-space: nowrap; }
@media (max-width: 900px) { .loop-ribbon { display: none; } }
</style>
