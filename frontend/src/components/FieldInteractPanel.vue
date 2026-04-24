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
            class="tb tb-primary"
            :disabled="busy"
            @click="emit('interact-action', act)"
          >
            {{ act.label }}
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

.interact-actions .tb {
  width: 100%;
  justify-content: center;
}

.interact-card-note {
  margin: 0;
  font-size: 0.68rem;
  line-height: 1.45;
  color: #64748b;
}

.tb {
  font-size: 0.76rem;
  padding: 0.38rem 0.65rem;
  border-radius: 9px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(51, 65, 85, 0.45);
  color: #e2e8f0;
  cursor: pointer;
}

.tb:hover:not(:disabled) {
  background: rgba(71, 85, 105, 0.55);
}

.tb-accent {
  background: linear-gradient(180deg, #6366f1, #4f46e5);
  border-color: rgba(165, 180, 252, 0.4);
  color: #fff;
  font-weight: 600;
}

.tb-primary {
  background: linear-gradient(180deg, #e94560, #c73e54);
  border-color: rgba(251, 113, 133, 0.4);
  color: #fff;
  font-weight: 600;
}

.tb:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
