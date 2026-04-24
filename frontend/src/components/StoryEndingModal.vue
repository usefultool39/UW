<template>
  <Teleport to="body">
    <div v-if="open && ending" class="modal-root" role="dialog" aria-modal="true">
      <div class="modal-backdrop" />
      <div class="modal-panel sao-window">
        <h2 class="modal-title">{{ ending.title }}</h2>
        <div class="modal-body">
          <p v-for="(line, i) in ending.lines" :key="i" class="line">{{ line }}</p>
        </div>
        <button type="button" class="primary close-btn" @click="$emit('close')">关闭</button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { CH1_ENDINGS } from '../data/ch1Choices.js'

const props = defineProps({
  open: { type: Boolean, default: false },
  endingId: { type: String, default: 'neutral' }
})

defineEmits(['close'])

const ending = computed(() => CH1_ENDINGS[props.endingId] || CH1_ENDINGS.neutral)
</script>

<style scoped>
.modal-root {
  position: fixed;
  inset: 0;
  z-index: 2100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(4, 8, 18, 0.82);
  backdrop-filter: blur(6px);
}

.modal-panel {
  position: relative;
  z-index: 1;
  max-width: 440px;
  width: 100%;
  padding: 1.35rem 1.45rem;
  border-radius: 14px;
}

.modal-title {
  font-size: 1.05rem;
  margin: 0 0 0.85rem;
  color: var(--sao-gold, #c9a227);
  letter-spacing: 0.05em;
}

.modal-body {
  margin-bottom: 1rem;
}

.line {
  margin: 0 0 0.65rem;
  font-size: 0.88rem;
  line-height: 1.65;
  color: var(--ink);
}

.line:last-child {
  margin-bottom: 0;
}

.close-btn {
  width: 100%;
}
</style>
