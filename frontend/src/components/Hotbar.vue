<template>
  <nav class="action-hotbar" aria-label="快捷操作">
    <button
      v-for="action in actions"
      :key="action.key"
      type="button"
      :disabled="isActionDisabled(action)"
      @click="$emit('action', action.id)"
      :title="getActionTitle(action)"
      :aria-label="getActionAriaLabel(action)"
      :class="`action-${action.id}`"
    >
      <kbd>{{ action.key }}</kbd>
      <span class="action-icon" aria-hidden="true">
        <span class="icon-symbol"></span>
        <span class="icon-fallback">{{ action.icon }}</span>
      </span>
      <span>{{ action.label }}</span>
    </button>
  </nav>
</template>

<script setup>
const props = defineProps({
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

function getDisabledReason(action) {
  if (props.busy) return '系统正忙，请稍候'
  if (action.requiresEvents && !props.hasEvents) return '附近暂无可处理线索'
  return ''
}

function isActionDisabled(action) {
  return !!getDisabledReason(action)
}

function getActionTitle(action) {
  return getDisabledReason(action) || action.desc
}

function getActionAriaLabel(action) {
  const reason = getDisabledReason(action)
  return reason ? `${action.label}不可用：${reason}` : `${action.label}：${action.desc}`
}
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
  position: relative;
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
  --action-accent: #7dd3fc;
  --action-glow: rgba(125, 211, 252, 0.24);
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.12s ease, background 0.18s ease;
  will-change: transform;
}

.action-hotbar button.action-talk { --action-accent: #22d3ee; --action-glow: rgba(34, 211, 238, 0.28); }
.action-hotbar button.action-read { --action-accent: #fde047; --action-glow: rgba(253, 224, 71, 0.28); }
.action-hotbar button.action-train { --action-accent: #fbbf24; --action-glow: rgba(251, 191, 36, 0.3); }
.action-hotbar button.action-rest { --action-accent: #a78bfa; --action-glow: rgba(167, 139, 250, 0.3); }
.action-hotbar button.action-journal { --action-accent: #c4b5fd; --action-glow: rgba(196, 181, 253, 0.28); }

.action-hotbar button.action-event:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.7);
  box-shadow: 0 0 18px rgba(212, 175, 55, 0.18);
}

.action-hotbar button:hover:not(:disabled) {
  border-color: color-mix(in srgb, var(--action-accent) 82%, white 18%);
  box-shadow: 0 0 18px var(--action-glow);
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
  position: relative;
  border-radius: 8px;
  color: var(--action-accent);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.1), rgba(2, 6, 23, 0.04)),
    rgba(94, 207, 255, 0.1);
  border: 1px solid color-mix(in srgb, var(--action-accent) 42%, transparent);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 0 12px var(--action-glow);
}

.icon-symbol,
.icon-symbol::before,
.icon-symbol::after {
  box-sizing: border-box;
  position: absolute;
  content: '';
  display: block;
}

.icon-fallback {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  font-size: 0.01px;
}

.action-talk .icon-symbol {
  width: 1rem;
  height: 0.72rem;
  border: 2px solid currentColor;
  border-radius: 0.4rem;
}

.action-talk .icon-symbol::after {
  right: 0.1rem;
  bottom: -0.32rem;
  width: 0.36rem;
  height: 0.36rem;
  border-left: 2px solid currentColor;
  border-bottom: 2px solid currentColor;
  transform: rotate(-18deg);
}

.action-read .icon-symbol {
  width: 1.08rem;
  height: 0.72rem;
  border: 2px solid currentColor;
  border-radius: 999px;
}

.action-read .icon-symbol::before {
  inset: 0.2rem 0.38rem;
  border-radius: 999px;
  background: currentColor;
}

.action-train .icon-symbol {
  width: 0.16rem;
  height: 1.12rem;
  border-radius: 999px;
  background: currentColor;
  transform: rotate(42deg);
}

.action-train .icon-symbol::before {
  left: -0.33rem;
  top: 0.4rem;
  width: 0.82rem;
  height: 0.16rem;
  border-radius: 999px;
  background: currentColor;
}

.action-rest .icon-symbol {
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  background: currentColor;
}

.action-rest .icon-symbol::after {
  right: -0.14rem;
  top: -0.04rem;
  width: 0.9rem;
  height: 0.9rem;
  border-radius: 50%;
  background: #0a101c;
}

.action-journal .icon-symbol {
  width: 0.95rem;
  height: 1.05rem;
  border: 2px solid currentColor;
  border-radius: 0.16rem;
}

.action-journal .icon-symbol::before,
.action-journal .icon-symbol::after {
  left: 0.18rem;
  width: 0.5rem;
  height: 0.1rem;
  border-radius: 999px;
  background: currentColor;
}

.action-journal .icon-symbol::before { top: 0.28rem; }
.action-journal .icon-symbol::after { top: 0.55rem; }

@supports not (color: color-mix(in srgb, white, black)) {
  .action-hotbar button:hover:not(:disabled) {
    border-color: rgba(253, 224, 71, 0.8);
  }

  .action-icon {
    border-color: rgba(125, 211, 252, 0.32);
  }
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

