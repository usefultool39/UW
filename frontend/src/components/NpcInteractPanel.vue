<template>
  <div
    v-show="modelValue && npc"
    class="npc-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="emit('update:modelValue', false)"
  >
    <section class="npc-panel" @click.stop>
      <header class="npc-header">
        <div>
          <p class="npc-kicker">NPC</p>
          <h3 class="npc-title">{{ displayName }}</h3>
        </div>
        <button
          type="button"
          class="npc-close"
          aria-label="关闭"
          @click="emit('update:modelValue', false)"
        >
          ×
        </button>
      </header>

      <dl class="npc-facts">
        <div>
          <dt>情绪</dt>
          <dd>{{ moodLabel }}</dd>
        </div>
        <div>
          <dt>当前行动</dt>
          <dd>{{ actionLabel }}</dd>
        </div>
        <div>
          <dt>位置</dt>
          <dd>{{ locationLabel }}</dd>
        </div>
      </dl>

      <p v-if="npc?.thought" class="npc-thought">{{ npc.thought }}</p>

      <div class="npc-actions">
        <button type="button" class="npc-action primary" :disabled="busy" @click="emit('talk')">
          对话
        </button>
        <button type="button" class="npc-action" :disabled="busy" @click="emit('relationship')">
          查看关系
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  npc: { type: Object, default: null },
  modelValue: { type: Boolean, default: false },
  busy: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'talk', 'relationship'])

const NAMES = {
  alice: '艾琳',
  eugeo: '尤里',
  kirito: '凛斗'
}

const LOCATION_LABELS = {
  at_tree: '巨树清场',
  bench: '村道长椅',
  home: '小屋',
  table: '餐桌'
}

const ACTION_LABELS = {
  init: '等待安排',
  noop: '观察周围',
  move: '移动中',
  chop: '练习挥斧',
  rest: '休息',
  eat: '用餐',
  sleep: '睡眠',
  go_home: '回家',
  cook: '准备餐食'
}

const displayName = computed(() => NAMES[props.npc?.id] || props.npc?.id || '未知角色')

const moodLabel = computed(() => {
  const mood = Number(props.npc?.mood ?? 50)
  if (mood >= 75) return '轻快'
  if (mood >= 55) return '平稳'
  if (mood >= 35) return '有些疲惫'
  return '低落'
})

const actionLabel = computed(() => {
  const goal = props.npc?.current_goal
  if (goal) return goal
  return ACTION_LABELS[props.npc?.last_action] || props.npc?.last_action || '等待安排'
})

const locationLabel = computed(() => {
  const loc = LOCATION_LABELS[props.npc?.location] || props.npc?.scene_id || '未知地点'
  const x = props.npc?.tile_x
  const y = props.npc?.tile_y
  if (Number.isFinite(Number(x)) && Number.isFinite(Number(y))) {
    return `${loc} · (${x}, ${y})`
  }
  return loc
})
</script>

<style scoped>
.npc-backdrop {
  position: fixed;
  inset: 0;
  z-index: 82;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(4, 8, 18, 0.76);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.npc-panel {
  width: min(92vw, 560px);
  padding: 1.25rem;
  border-radius: 16px;
  background: linear-gradient(165deg, rgba(25, 37, 56, 0.97), rgba(8, 12, 22, 0.98));
  border: 1px solid var(--sao-border);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55), 0 0 24px rgba(94, 207, 255, 0.1);
}

.npc-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.npc-kicker {
  margin: 0 0 0.15rem;
  font-size: 0.62rem;
  letter-spacing: 0.14em;
  color: var(--sao-cyan);
  font-weight: 700;
}

.npc-title {
  margin: 0;
  font-size: 1.5rem;
  color: #f8fafc;
}

.npc-close {
  flex: 0 0 auto;
  width: 2.4rem;
  height: 2.4rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 8px;
  background: rgba(51, 65, 85, 0.6);
  color: #e2e8f0;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}

.npc-facts {
  display: grid;
  gap: 0.55rem;
  margin: 0 0 0.85rem;
}

.npc-facts div {
  display: grid;
  grid-template-columns: 4.2rem 1fr;
  gap: 0.5rem;
  align-items: baseline;
}

.npc-facts dt {
  color: var(--muted);
  font-size: 0.84rem;
}

.npc-facts dd {
  margin: 0;
  color: #e2e8f0;
  font-size: 1rem;
  line-height: 1.45;
}

.npc-thought {
  margin: 0 0 0.85rem;
  padding: 0.55rem 0.65rem;
  border-radius: 10px;
  color: #dbeafe;
  background: rgba(30, 64, 175, 0.18);
  border: 1px solid rgba(147, 197, 253, 0.2);
  font-size: 0.95rem;
  line-height: 1.55;
}

.npc-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.55rem;
}

.npc-action {
  min-height: 3rem;
  border-radius: 9px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(51, 65, 85, 0.45);
  color: #e2e8f0;
  font-size: 0.98rem;
  font-weight: 600;
  cursor: pointer;
}

.npc-action:hover:not(:disabled) {
  background: rgba(71, 85, 105, 0.6);
}

.npc-action.primary {
  background: linear-gradient(180deg, #e94560, #c73e54);
  border-color: rgba(251, 113, 133, 0.45);
  color: #fff;
}

.npc-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
