<template>
  <Teleport to="body">
    <div v-if="open" class="modal-root" role="dialog" aria-modal="true">
      <div class="modal-backdrop" @click.self="noop" />
      <div class="modal-panel sao-window">
        <h2 class="modal-title">{{ title }}</h2>
        <p class="modal-intro">{{ intro }}</p>
        <div class="modal-actions">
          <button type="button" class="choice-a" @click="emitPick(keys[0])">{{ labels[0] }}</button>
          <button type="button" class="choice-b" @click="emitPick(keys[1])">{{ labels[1] }}</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { CHOICE_INTRO } from '../data/ch1Dialogue.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  type: { type: String, default: '' } // 'c1' | 'c2'
})

const emit = defineEmits(['pick', 'close'])

const title = computed(() =>
  props.type === 'c2' ? '食桌 · 膳食抉择' : '伐木区 · 节奏抉择'
)

const intro = computed(() => CHOICE_INTRO[props.type] || '')

const keys = computed(() =>
  props.type === 'c2' ? ['c2_alice', 'c2_self'] : ['c1_rush', 'c1_safe']
)

const labels = computed(() =>
  props.type === 'c2'
    ? ['采纳艾琳的安排', '自行安排餐桌']
    : ['加快削木（更信凛斗）', '稳扎稳打（更信尤里）']
)

function emitPick(key) {
  emit('pick', key)
  emit('close')
}

function noop() {}
</script>

<style scoped>
.modal-root {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(4, 8, 18, 0.75);
  backdrop-filter: blur(4px);
}

.modal-panel {
  position: relative;
  z-index: 1;
  max-width: 420px;
  width: 100%;
  padding: 1.25rem 1.35rem;
  border-radius: 14px;
}

.modal-title {
  font-size: 1rem;
  margin: 0 0 0.5rem;
  color: var(--sao-cyan);
  letter-spacing: 0.06em;
}

.modal-intro {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  color: var(--ink);
  line-height: 1.55;
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.modal-actions button {
  width: 100%;
  text-align: left;
  padding: 0.55rem 0.65rem;
  font-size: 0.82rem;
}

.choice-a {
  border-color: rgba(233, 69, 96, 0.55);
}

.choice-b {
  border-color: rgba(94, 207, 255, 0.45);
}
</style>
