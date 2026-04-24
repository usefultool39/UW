<template>
  <div class="control-hud-inner">
    <div class="controls">
      <button type="button" @click="$emit('reset')" :disabled="loading">重置</button>
      <button type="button" class="primary" @click="$emit('toggle-auto')" :disabled="loading">
        <span v-if="loading" class="spinner"></span>
        {{ autoRunning ? '⏸ 暂停' : '▶ 开始' }}
      </button>
      <div class="speed-selector">
        <span class="speed-label">速度</span>
        <button
          v-for="s in [1, 2, 5]"
          :key="s"
          type="button"
          :class="{ active: speed === s }"
          @click="$emit('update:speed', s)"
          :disabled="loading"
        >{{ s }}倍</button>
      </div>
      <select :value="mode" aria-label="决策模式" @change="$emit('update:mode', $event.target.value)" :disabled="loading">
        <option value="heuristic">规则模式</option>
        <option value="llm">智能模式</option>
      </select>
    </div>
  </div>
</template>

<script setup>
defineProps({
  autoRunning: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  speed: { type: Number, default: 1 },
  llmConfigured: { type: Boolean, default: false },
  llmProvider: { type: String, default: '' },
  mode: { type: String, default: 'heuristic' }
})

defineEmits(['toggle-auto', 'reset', 'update:speed', 'update:mode'])
</script>

<style scoped>
.control-hud-inner {
  background: linear-gradient(180deg, transparent 0%, rgba(6, 10, 20, 0.88) 40%, rgba(6, 10, 20, 0.94) 100%);
  padding: 1.35rem 0.85rem 0.7rem;
  border-top: 1px solid var(--sao-border-dim);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  align-items: center;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.speed-selector {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.speed-label {
  color: var(--muted);
  font-size: 0.75rem;
  margin-right: 0.25rem;
}

.speed-selector button {
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--sao-border-dim);
  background: transparent;
  color: var(--muted);
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
}

.speed-selector button.active {
  background: var(--sao-green);
  color: #000;
  border-color: var(--sao-green);
}

.spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 4px;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
