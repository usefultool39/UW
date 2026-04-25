<template>
  <nav class="action-hotbar" aria-label="快捷操作">
    <button
      v-for="action in actions"
      :key="action.key"
      type="button"
      :disabled="busy || (action.requiresEvents && !hasEvents)"
      @click="$emit('action', action.id)"
      :title="action.desc"
    >
      <kbd>{{ action.key }}</kbd>
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
  { id: 'talk',  key: '1', label: '对话',  desc: '与附近的 NPC 对话' },
  { id: 'read',  key: '2', label: '读书',  desc: '阅读书页，了解规则与边界' },
  { id: 'train', key: '3', label: '训练',  desc: '消耗一个时刻进行训练' },
  { id: 'rest',  key: '4', label: '休息',  desc: '回小屋休息，推进到第二天' },
  { id: 'event', key: '5', label: '事件',  desc: '触发章节剧情事件', requiresEvents: true }
]
</script>

<style scoped>
.action-hotbar {
  position: absolute;
  z-index: 5;
  left: 50%;
  bottom: 0.72rem;
  transform: translateX(-50%);
  display: grid;
  grid-template-columns: repeat(5, minmax(3.7rem, 1fr));
  gap: 0.45rem;
  width: min(520px, calc(100% - 1.5rem));
  padding: 0.45rem;
  border-radius: 12px;
  background: rgba(4, 8, 18, 0.82);
  border: 1px solid rgba(229, 196, 92, 0.3);
  box-shadow: 0 18px 38px rgba(0, 0, 0, 0.38), inset 0 1px 0 rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.action-hotbar button {
  min-height: 3.1rem;
  padding: 0.35rem 0.28rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.18rem;
  background: linear-gradient(180deg, rgba(82, 63, 35, 0.92), rgba(18, 25, 38, 0.96));
  border-color: rgba(245, 208, 112, 0.34);
  color: #f8fafc;
  font-size: 0.72rem;
  font-weight: 800;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.12s ease;
  will-change: transform;
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
