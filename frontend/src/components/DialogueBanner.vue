<template>
  <Transition name="banner">
    <div v-if="message" class="dialogue-banner" role="status">
      {{ message }}
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  message: { type: String, default: '' }
})
</script>

<style scoped>
.dialogue-banner {
  position: fixed;
  top: 0.75rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1500;
  max-width: min(520px, 92vw);
  padding: 0.55rem 1rem;
  font-size: 0.82rem;
  line-height: 1.5;
  color: var(--ink);
  background: rgba(12, 20, 36, 0.92);
  border: 1px solid var(--sao-border-dim);
  border-radius: 10px;
  box-shadow: var(--shadow);
  text-align: center;
}

.banner-enter-active,
.banner-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.banner-enter-from,
.banner-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-8px);
}
</style>
