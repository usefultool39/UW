<template>
  <header class="field-header">
    <div class="field-title">
      <p class="field-kicker">{{ GAME_CHAPTER_INFO.kicker }}</p>
      <h2>{{ GAME_CHAPTER_INFO.title }}</h2>
    </div>
    <div class="header-actions">
      <button type="button" class="tb tb-ghost" :disabled="busy" @click="$emit('export-save')">
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M3 17h14v-2H3v2zm9-9L6 12h4v4h4v-4h4l-6-6z"/></svg>导出存档
      </button>
      <button type="button" class="tb tb-ghost" :disabled="busy" @click="$emit('import-save')">
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M17 17H3v-2h14v2zm-6-8L6 13h4v4h4v-4h4l-6-6z"/></svg>导入存档
      </button>
      <button type="button" class="tb tb-ghost" :disabled="busy" @click="$emit('refresh')">
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M10 3v2a5 5 0 0 1 5.12 4.87l-1.02-1.74A3 3 0 1 0 14 10h2l-2-3-2 3H9a3 3 0 0 0 0 6 5 5 0 0 1 .12 9.95L10 17v-3H7l2-3 2 3h-1z"/></svg>刷新
      </button>
      <button type="button" class="tb tb-primary" :disabled="busy" @click="$emit('daily')">
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M6 3l1.5 3.5L11 5l-1.5 3.5L14 11l-3.5 1.5L11 16l-.5-3.5L7 14l-3.5-1.5L4 9l3.5-1.5L6 3z"/></svg>时间推进
      </button>
    </div>
    <input
      ref="saveFileEl"
      class="save-file"
      type="file"
      accept="application/json,.json"
      @change="$emit('import-file', $event)"
    />
  </header>
</template>

<script setup>
import { GAME_CHAPTER_INFO } from '../field/gameContentConfig.js'

defineProps({
  busy: { type: Boolean, default: false }
})

defineEmits([
  'export-save',
  'import-save',
  'import-file',
  'refresh',
  'daily'
])
</script>

<style scoped>
.field-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.55rem;
  flex-wrap: wrap;
}

.field-title {
  flex: 0 0 auto;
}

.field-kicker {
  margin: 0 0 0.1rem;
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  color: var(--sao-cyan);
  font-weight: 700;
  text-transform: uppercase;
}

.field-title h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: 0;
  background: linear-gradient(110deg, #fff 0%, var(--sao-cyan) 55%, var(--sao-gold) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.save-file {
  display: none;
}

/* Toolbar buttons */
.tb {
  font-size: 0.74rem;
  padding: 0.36rem 0.6rem;
  border-radius: 8px;
  border: 1px solid var(--sao-border-dim);
  background: rgba(15, 23, 42, 0.55);
  color: var(--ink);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease, transform 0.12s ease;
  will-change: transform;
}

.tb:hover:not(:disabled) {
  background: rgba(94, 207, 255, 0.1);
  border-color: var(--sao-border);
  box-shadow: var(--sao-glow);
}

.tb:active:not(:disabled) {
  transform: translateY(1px);
}

.tb:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.tb-ghost {
  background: rgba(12, 20, 36, 0.5);
}

.tb-primary {
  background: linear-gradient(180deg, var(--accent), #b8324a);
  border-color: rgba(251, 113, 133, 0.45);
  color: #fff;
  font-weight: 600;
}

.tb-primary:hover:not(:disabled) {
  border-color: rgba(251, 113, 133, 0.8);
  box-shadow: 0 0 18px rgba(233, 69, 96, 0.35);
}

.btn-icon {
  width: 0.85rem;
  height: 0.85rem;
  flex: 0 0 auto;
}

@media (max-width: 900px) {
  .field-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
