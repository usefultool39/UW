<template>
  <div class="card">
    <div class="card-title">角色状态</div>
    <div class="agents-grid">
      <div v-for="agent in agents" :key="agent.id" class="agent-mini">
        <img
          :src="getAgentMeta(agent.id).img"
          :alt="getAgentMeta(agent.id).display"
          @error="onAgentImgError($event, getAgentMeta(agent.id))"
        />
        <div class="agent-mini-name" :style="{ color: getAgentMeta(agent.id).color }">
          {{ getAgentMeta(agent.id).display }}
        </div>
        <div class="agent-mini-loc">{{ locationLabels[agent.location] || agent.location }}</div>
        <div class="bar-row" style="margin-top: 0.3rem">
          <span class="bar-label">体力</span>
          <div class="bar-track">
            <div class="bar-fill stamina" :style="{ width: (agent.stamina / agent.stamina_max) * 100 + '%' }"></div>
          </div>
        </div>
        <div class="bar-row">
          <span class="bar-label">饥饿</span>
          <div class="bar-track">
            <div class="bar-fill hunger" :style="{ width: agent.hunger + '%' }"></div>
          </div>
        </div>
        <div class="bar-row">
          <span class="bar-label">心情</span>
          <div class="bar-track">
            <div class="bar-fill mood" :style="{ width: (agent.mood || 50) + '%' }"></div>
          </div>
        </div>
        <div class="agent-contribution" v-if="agent.daily_contribution !== undefined">
          今日贡献: {{ agent.daily_contribution }}次
        </div>
        <div class="agent-thought" v-if="agent.thought" :title="agent.thought">
          💭 {{ agent.thought }}
        </div>
        <div class="agent-mini-action">{{ actionLabels[agent.last_action] || agent.last_action }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { getAgentMeta, onAgentImgError } from '../constants/agents.js'

defineProps({
  agents: { type: Array, required: true }
})

const actionLabels = {
  chop: '砍树', rest: '休息', move: '移动', noop: '观望',
  eat: '吃饭', sleep: '睡觉', go_home: '回家', cook: '做饭'
}

const locationLabels = {
  at_tree: '树旁', bench: '长椅', home: '家', table: '餐桌'
}
</script>

<style scoped>
.agents-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.6rem;
}

@media (max-width: 900px) {
  .agents-grid {
    grid-template-columns: 1fr;
  }
}

.agent-mini {
  background: rgba(0, 0, 0, 0.22);
  border-radius: 10px;
  padding: 0.6rem;
  text-align: center;
  border: 1px solid var(--sao-border-dim);
}

.agent-mini img {
  width: 45px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid rgba(94, 207, 255, 0.35);
}

.agent-mini-name {
  font-size: 0.8rem;
  font-weight: bold;
  margin-top: 0.3rem;
}

.agent-mini-loc {
  font-size: 0.7rem;
  color: var(--muted);
  margin-top: 0.2rem;
}

.agent-mini-action {
  font-size: 0.7rem;
  color: var(--ok);
  margin-top: 0.2rem;
}

.agent-contribution {
  font-size: 0.65rem;
  color: var(--sao-cyan);
  margin-top: 0.2rem;
}

.agent-thought {
  font-size: 0.65rem;
  color: var(--muted);
  font-style: italic;
  margin-top: 0.2rem;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 4.2em;
  overflow: auto;
  max-width: 100%;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.bar-label {
  width: 50px;
  font-size: 0.75rem;
  color: var(--muted);
}

.bar-track {
  flex: 1;
  height: 12px;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid var(--sao-border-dim);
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.35s ease;
}

.bar-fill.stamina {
  background: linear-gradient(90deg, #4ecca3, #7fff00);
}

.bar-fill.hunger {
  background: linear-gradient(90deg, #ff6b6b, #ffa500);
}

.bar-fill.mood {
  background: linear-gradient(90deg, #ff69b4, #ff1493);
}
</style>
