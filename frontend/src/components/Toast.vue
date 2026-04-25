<template>
  <Teleport to="body">
    <Transition name="toast-slide">
      <div v-if="visible" class="toast" :class="type" role="status" aria-live="polite">
        <div class="toast-icon">
          <span v-if="type === 'success'">✓</span>
          <span v-else-if="type === 'error'">✕</span>
          <span v-else-if="type === 'warn'">⚠</span>
          <span v-else>ℹ</span>
        </div>
        <p class="toast-message">{{ message }}</p>
        <button class="toast-close" @click="dismiss" aria-label="关闭">×</button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  message: { type: String, default: '' },
  type: { type: String, default: 'info' }, // info | success | error | warn
  duration: { type: Number, default: 3400 },
  modelValue: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
let timer = null

function show() {
  visible.value = true
  clearTimeout(timer)
  if (props.duration > 0) {
    timer = setTimeout(() => {
      dismiss()
    }, props.duration)
  }
}

function dismiss() {
  visible.value = false
  clearTimeout(timer)
  emit('update:modelValue', false)
}

watch(() => props.modelValue, (val) => {
  if (val) show()
  else dismiss()
})
</script>

<style scoped>
.toast {
  position: fixed;
  bottom: 5.5rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.6rem 0.85rem 0.6rem 0.75rem;
  border-radius: 12px;
  max-width: min(92vw, 480px);
  min-width: 240px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45), 0 0 16px rgba(94, 207, 255, 0.1);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid;
  pointer-events: auto;
}

.toast.info {
  background: rgba(15, 23, 42, 0.92);
  border-color: rgba(94, 207, 255, 0.3);
  color: #e2e8f0;
}

.toast.success {
  background: rgba(16, 60, 30, 0.94);
  border-color: rgba(110, 231, 183, 0.4);
  color: #d1fae5;
}

.toast.error {
  background: rgba(127, 29, 29, 0.94);
  border-color: rgba(248, 113, 113, 0.4);
  color: #fecaca;
}

.toast.warn {
  background: rgba(120, 53, 15, 0.94);
  border-color: rgba(253, 224, 71, 0.4);
  color: #fef3c7;
}

.toast-icon {
  flex: 0 0 auto;
  font-size: 1rem;
  font-weight: 900;
  opacity: 0.85;
}

.toast-message {
  flex: 1;
  margin: 0;
  font-size: 0.84rem;
  line-height: 1.45;
}

.toast-close {
  flex: 0 0 auto;
  background: transparent;
  border: none;
  color: inherit;
  opacity: 0.6;
  font-size: 1.1rem;
  padding: 0;
  cursor: pointer;
  line-height: 1;
  transition: opacity 0.15s;
  box-shadow: none;
}

.toast-close:hover {
  opacity: 1;
  box-shadow: none;
  background: transparent;
  border-color: transparent;
}

/* Slide-up transition */
.toast-slide-enter-active {
  animation: toast-in 0.32s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.toast-slide-leave-active {
  animation: toast-out 0.22s ease-in both;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(12px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
}

@keyframes toast-out {
  from {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateX(-50%) translateY(8px) scale(0.97);
  }
}
</style>
