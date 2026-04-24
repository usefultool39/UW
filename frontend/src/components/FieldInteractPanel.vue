<template>
  <div class="field-interact-root">
    <div
      v-show="modelValue && nearbyInteract"
      class="interact-backdrop"
      role="dialog"
      aria-modal="true"
      @click.self="emit('update:modelValue', false)"
    >
      <div class="interact-card" @click.stop>
        <header class="interact-card-hd">
          <h3 class="interact-card-title">{{ nearbyInteract?.title }}</h3>
          <button
            type="button"
            class="interact-close"
            aria-label="关闭"
            @click="emit('update:modelValue', false)"
          >
            ×
          </button>
        </header>
        <p class="interact-card-body">{{ nearbyInteract?.body }}</p>
        <div class="interact-actions">
          <button
            v-for="act in visibleInteractActions"
            :key="act.id"
            type="button"
            class="interact-action"
            :class="{ blocked: !!act.blockedReason }"
            :disabled="busy || !!act.blockedReason"
            @click="emit('interact-action', act)"
          >
            <span class="action-label">{{ act.label }}</span>
            <span v-if="act.meta" class="action-meta">{{ act.meta }}</span>
            <span v-if="act.description" class="action-desc">{{ act.description }}</span>
          </button>
        </div>
        <p class="interact-card-note">
          站定或走完路后再点地图上的「对话/互动」（移动中按钮会隐藏）。选项在下方。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  nearbyInteract: { type: Object, default: null },
  visibleInteractActions: { type: Array, default: () => [] },
  busy: { type: Boolean, default: false },
  modelValue: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'interact-action'])
</script>

<style scoped>
.field-interact-root {
  width: 100%;
}

.interact-backdrop {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(4, 8, 18, 0.78);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.interact-card {
  width: 100%;
  max-width: 420px;
  max-height: min(86vh, 520px);
  overflow: auto;
  padding: 1rem 1.1rem;
  border-radius: 14px;
  background: linear-gradient(165deg, rgba(30, 41, 59, 0.95), rgba(7, 10, 18, 0.98));
  border: 1px solid var(--sao-border);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55), 0 0 24px rgba(94, 207, 255, 0.08);
}

.interact-card-hd {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.interact-card-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #f8fafc;
}

.interact-close {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border: none;
  border-radius: 8px;
  background: rgba(51, 65, 85, 0.6);
  color: #e2e8f0;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}

.interact-close:hover {
  background: rgba(71, 85, 105, 0.75);
}

.interact-card-body {
  margin: 0 0 0.75rem;
  font-size: 0.88rem;
  line-height: 1.6;
  color: #cbd5e1;
}

.interact-actions {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  margin-bottom: 0.65rem;
}

.interact-actions .interact-action {
  width: 100%;
}

.interact-card-note {
  margin: 0;
  font-size: 0.68rem;
  line-height: 1.45;
  color: #64748b;
}

.interact-action {
  font-size: 0.76rem;
  padding: 0.52rem 0.65rem;
  border-radius: 9px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: linear-gradient(180deg, rgba(185, 88, 58, 0.88), rgba(110, 46, 44, 0.92));
  color: #e2e8f0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.18rem;
  text-align: left;
}

.interact-action:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.55);
  background: linear-gradient(180deg, rgba(210, 104, 68, 0.96), rgba(126, 55, 48, 0.96));
  box-shadow: 0 0 16px rgba(246, 211, 110, 0.14);
}

.interact-action:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.interact-action.blocked {
  background: rgba(31, 41, 55, 0.72);
  border-color: rgba(148, 163, 184, 0.16);
}

.action-label {
  color: #fff7d6;
  font-weight: 800;
  line-height: 1.35;
}

.action-meta {
  color: #bae6fd;
  font-size: 0.66rem;
  line-height: 1.35;
}

.action-desc {
  color: #cbd5e1;
  font-size: 0.68rem;
  line-height: 1.45;
}
</style>
