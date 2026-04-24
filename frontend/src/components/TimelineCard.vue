<template>
  <div class="timeline-card sao-panel">
    <button
      type="button"
      class="timeline-toggle"
      :aria-expanded="expanded"
      @click="expanded = !expanded"
    >
      <span class="timeline-title">系统日志</span>
      <span class="timeline-count">{{ events.length }} 条</span>
      <span class="timeline-chevron" :class="{ open: expanded }" aria-hidden="true">▼</span>
    </button>
    <div v-show="expanded" class="timeline-body-wrap">
      <div class="timeline-body">
        <div v-if="!events.length" class="empty-state">点击「单步」开始模拟</div>
        <div
          v-for="(ev, idx) in recentEvents"
          :key="idx"
          class="event-item"
          :class="getEventClass(ev)"
        >
          <span class="event-actor" :style="{ color: getAgentMeta(ev.actor).color }">
            [{{ getAgentMeta(ev.actor).display || ev.actor }}]
          </span>
          <span class="event-action">{{ getActionLabel(ev) }}</span>
          <div class="event-detail">{{ ev.detail }}</div>
          <div class="event-thinking" v-if="ev.llm_thinking">
            💭 {{ ev.llm_thinking }}
          </div>
          <details class="event-llm" v-if="ev.decision_mode === 'llm'">
            <summary>查看大模型往返过程</summary>
            <div class="event-llm-meta" v-if="ev.llm_model">模型：{{ ev.llm_model }}</div>
            <div class="event-llm-block" v-if="ev.llm_prompt_user">
              <div class="event-llm-title">发送给模型的上下文</div>
              <pre>{{ ev.llm_prompt_user }}</pre>
            </div>
            <div class="event-llm-block" v-if="ev.llm_raw">
              <div class="event-llm-title">模型原始回复</div>
              <pre>{{ ev.llm_raw }}</pre>
            </div>
          </details>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { AGENT_META } from '../constants/agents.js'

const props = defineProps({
  events: { type: Array, required: true }
})

const expanded = ref(false)

const ACTION_LABELS = {
  chop: '砍树', rest: '休息', move: '移动', noop: '观望',
  eat: '吃饭', sleep: '睡觉', go_home: '回家', cook: '做饭'
}

const recentEvents = computed(() => props.events.slice(-50).reverse())

function getAgentMeta(id) {
  return AGENT_META[id] || { display: id, color: '#fff' }
}

function getActionName(ev) {
  try {
    const a = typeof ev.action === 'string' ? JSON.parse(ev.action) : ev.action
    return a?.name || 'noop'
  } catch {
    return 'noop'
  }
}

function getActionLabel(ev) {
  return ACTION_LABELS[getActionName(ev)] || getActionName(ev)
}

function getEventClass(ev) {
  const actionName = getActionName(ev)
  if (!ev.ok) return 'fail'
  const classMap = {
    chop: 'chop', rest: 'rest', eat: 'eat', sleep: 'sleep', cook: 'cook', move: 'move'
  }
  return classMap[actionName] || 'noop'
}
</script>

<style scoped>
.timeline-card {
  border-radius: 0 0 14px 14px;
  overflow: hidden;
  flex-shrink: 0;
}

.timeline-toggle {
  position: relative;
  z-index: 3;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.55rem 1rem;
  margin: 0;
  border: none;
  background: rgba(0, 0, 0, 0.35);
  color: var(--ink);
  font: inherit;
  cursor: pointer;
  text-align: left;
  border-bottom: 1px solid var(--sao-border-dim);
  transition: background 0.2s ease;
}

.timeline-toggle:hover {
  background: rgba(94, 207, 255, 0.08);
}

.timeline-title {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--sao-cyan);
}

.timeline-count {
  font-size: 0.75rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
  margin-left: auto;
}

.timeline-chevron {
  font-size: 0.65rem;
  color: var(--muted);
  transition: transform 0.2s ease;
}

.timeline-chevron.open {
  transform: rotate(-180deg);
}

.timeline-body-wrap {
  max-height: min(40vh, 280px);
  overflow: hidden;
}

.timeline-body {
  max-height: min(40vh, 280px);
  overflow-y: auto;
  padding: 0.65rem 0.85rem 0.85rem;
}

.event-item {
  padding: 0.45rem 0.5rem;
  border-radius: 6px;
  margin-bottom: 0.35rem;
  background: rgba(255, 255, 255, 0.04);
  border-left: 3px solid var(--accent);
  font-size: 0.78rem;
}

.event-item.chop { border-left-color: var(--accent); }
.event-item.rest { border-left-color: var(--ok); }
.event-item.eat { border-left-color: #ffa500; }
.event-item.sleep { border-left-color: #7fff00; }
.event-item.cook { border-left-color: #ff6b6b; }
.event-item.move { border-left-color: var(--river); }
.event-item.fail { border-left-color: var(--bad); opacity: 0.75; }

.event-actor {
  font-weight: bold;
}

.event-action {
  color: var(--muted);
  margin-left: 0.25rem;
}

.event-detail {
  color: var(--ok);
  font-size: 0.72rem;
  margin-top: 0.15rem;
}

.event-thinking {
  color: var(--muted);
  font-size: 0.7rem;
  font-style: italic;
  margin-top: 0.2rem;
  padding: 0.25rem 0.4rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 4px;
}

.event-llm {
  margin-top: 0.28rem;
  border-top: 1px dashed rgba(255, 255, 255, 0.16);
  padding-top: 0.28rem;
}

.event-llm summary {
  cursor: pointer;
  color: var(--sao-cyan);
  font-size: 0.7rem;
}

.event-llm-meta {
  margin-top: 0.3rem;
  color: var(--muted);
  font-size: 0.68rem;
}

.event-llm-block {
  margin-top: 0.32rem;
}

.event-llm-title {
  color: var(--muted);
  font-size: 0.68rem;
  margin-bottom: 0.15rem;
}

.event-llm pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 10rem;
  overflow: auto;
  background: rgba(0, 0, 0, 0.28);
  border: 1px solid var(--sao-border-dim);
  border-radius: 4px;
  padding: 0.35rem;
  color: #d6ecff;
  font-size: 0.66rem;
  line-height: 1.35;
}

.empty-state {
  text-align: center;
  color: var(--muted);
  padding: 1.25rem;
  font-size: 0.85rem;
}
</style>
