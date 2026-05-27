<template>
  <nav class="action-hotbar" aria-label="快捷操作">
    <button
      v-for="action in actions"
      :key="action.key"
      type="button"
      :disabled="busy || (action.requiresEvents && !hasEvents)"
      @click="$emit('action', action.id)"
      :title="action.desc"
      :class="`action-${action.id}`"
    >
      <kbd>{{ action.key }}</kbd>
      <span class="action-icon" aria-hidden="true">{{ action.icon }}</span>
      <span>{{ action.label }}</span>
    </button>
  </nav>
</template>

<script setup>
defineProps({
  busy: { type: Boolean, default: false },
  hasEvents: { type: Boolean, default: false }
})

defineEmits(['action'])

const actions = [
  { id: 'talk', key: '1', icon: '话', label: '对话', desc: '与附近的 NPC 对话' },
  { id: 'read', key: '2', icon: '查', label: '调查', desc: '阅读书页，了解规则与边界' },
  { id: 'train', key: '3', icon: '剑', label: '训练', desc: '进行古誓树训练' },
  { id: 'rest', key: '4', icon: '眠', label: '休息', desc: '回小屋休息，推进到第二天' },
  { id: 'journal', key: '5', icon: '志', label: '日志', desc: '查看线索手册、NPC 记忆和关系暗线' }
]
</script>

<style scoped>
.action-hotbar {
  position: absolute;
  z-index: 45;
  left: 50%;
  bottom: 0.85rem;
  transform: translateX(-50%);
  display: grid;
  grid-template-columns: repeat(5, minmax(4.4rem, 1fr));
  gap: 0.55rem;
  width: min(620px, calc(100% - 1.5rem));
  padding: 0.46rem;
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(4, 8, 18, 0.84), rgba(10, 16, 28, 0.72));
  border: 1px solid rgba(125, 211, 252, 0.2);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.action-hotbar button {
  min-height: 3.25rem;
  padding: 0.32rem 0.28rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.12rem;
  background: linear-gradient(180deg, rgba(22, 36, 58, 0.92), rgba(9, 14, 24, 0.96));
  border-color: rgba(125, 211, 252, 0.24);
  color: #f8fafc;
  font-size: 0.82rem;
  font-weight: 800;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.12s ease;
  will-change: transform;
}

.action-hotbar button.action-event:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.7);
  box-shadow: 0 0 18px rgba(212, 175, 55, 0.18);
}

.action-hotbar button:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.8);
  box-shadow: 0 0 18px rgba(212, 175, 55, 0.34);
  transform: translateY(-1px);
}

.action-hotbar button:active:not(:disabled) {
  transform: translateY(0);
}

.action-hotbar button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.action-hotbar kbd {
  position: absolute;
  top: 0.32rem;
  left: 0.38rem;
  min-width: 1.2rem;
  height: 1.2rem;
  display: inline-grid;
  place-items: center;
  border-radius: 4px;
  color: #1f2937;
  background: #f8fafc;
  border: 1px solid rgba(255, 255, 255, 0.55);
  font-size: 0.68rem;
  font-weight: 900;
  font-family: inherit;
}

.action-icon {
  width: 1.65rem;
  height: 1.65rem;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: #dff7ff;
  background: rgba(94, 207, 255, 0.12);
  border: 1px solid rgba(125, 211, 252, 0.28);
  font-size: 0.92rem;
  font-weight: 900;
  line-height: 1;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

@media (max-width: 900px) {
  .action-hotbar {
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 0.28rem;
    width: calc(100% - 1rem);
    bottom: 0.5rem;
    padding: 0.35rem;
  }

  .action-hotbar button {
    min-height: 2.75rem;
  }

  .action-hotbar span {
    font-size: 0.66rem;
  }
}
</style>

