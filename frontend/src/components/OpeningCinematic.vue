<template>
  <Transition name="opening-cinematic">
    <section v-if="modelValue" class="opening-cinematic-root" role="dialog" aria-modal="true">
      <div class="opening-bg" aria-hidden="true" />
      <div class="opening-rain" aria-hidden="true" />
      <div class="opening-copy">
        <p class="opening-kicker">UNDERWORLD · 分支记录 07</p>
        <h1>卢利特村</h1>
        <p class="opening-lead">
          你是卢利特村的见习记录员。今天原本只有天命登记与剑术练习，教会书库里却出现了一页不该存在的北境记录。
        </p>
        <div class="opening-objective">
          <span>当前目标</span>
          <strong>先去教会书库，确认被修改的北境记录。</strong>
        </div>
        <div class="opening-actions">
          <button type="button" class="opening-primary" @click="$emit('focus-first-event')">
            开始记录
          </button>
          <button type="button" class="opening-secondary" @click="$emit('skip')">
            开始行动
          </button>
        </div>
      </div>
      <div class="opening-status" aria-hidden="true">
        <span>Day 1</span>
        <span>细雨</span>
        <span>卢利特村广场</span>
      </div>
    </section>
  </Transition>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false }
})

defineEmits(['focus-first-event', 'skip'])
</script>

<style scoped>
.opening-cinematic-root {
  position: fixed;
  inset: 0;
  z-index: 140;
  overflow: hidden;
  color: #fff7df;
  background: #172018;
  display: grid;
  align-items: center;
  padding: clamp(1.2rem, 4vw, 4.5rem);
}

.opening-bg {
  position: absolute;
  inset: -4%;
  background:
    linear-gradient(90deg, rgba(6, 10, 18, 0.88) 0%, rgba(6, 10, 18, 0.48) 48%, rgba(6, 10, 18, 0.16) 100%),
    radial-gradient(circle at 74% 38%, rgba(246, 211, 110, 0.18), transparent 28%),
    url('/assets/game/field-bg-tv-v3.jpg') center / cover no-repeat;
  filter: saturate(1.06) contrast(1.04);
  transform: scale(1.04);
  animation: opening-drift 8s ease-out both;
}

.opening-rain {
  position: absolute;
  inset: 0;
  opacity: 0.34;
  background:
    repeating-linear-gradient(112deg, rgba(226, 232, 240, 0.26) 0 1px, transparent 1px 16px),
    linear-gradient(180deg, rgba(255, 247, 214, 0.08), transparent 44%);
  animation: opening-rain 1.4s linear infinite;
}

.opening-copy {
  position: relative;
  z-index: 2;
  width: min(680px, 100%);
  text-shadow: 0 2px 16px rgba(0, 0, 0, 0.55);
}

.opening-kicker {
  margin: 0 0 0.55rem;
  color: #f6d36e;
  font-size: 0.82rem;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.opening-copy h1 {
  margin: 0;
  color: #fff7df;
  font-size: clamp(3rem, 8vw, 6.8rem);
  line-height: 0.92;
  font-weight: 900;
}

.opening-lead {
  max-width: 36rem;
  margin: 1.15rem 0 0;
  color: rgba(255, 247, 223, 0.9);
  font-size: clamp(1rem, 2vw, 1.28rem);
  line-height: 1.72;
}

.opening-objective {
  width: min(520px, 100%);
  margin-top: 1.25rem;
  padding: 0.78rem 0.92rem;
  border-left: 3px solid #f6d36e;
  background: linear-gradient(90deg, rgba(12, 18, 28, 0.74), rgba(12, 18, 28, 0.22));
}

.opening-objective span {
  display: block;
  color: #bae6fd;
  font-size: 0.72rem;
  font-weight: 900;
  letter-spacing: 0.1em;
}

.opening-objective strong {
  display: block;
  margin-top: 0.22rem;
  color: #fff7df;
  font-size: 1rem;
  line-height: 1.45;
}

.opening-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.72rem;
  margin-top: 1.35rem;
}

.opening-actions button {
  min-height: 2.8rem;
  padding: 0 1.1rem;
  border-radius: 8px;
  font-size: 0.96rem;
  font-weight: 900;
}

.opening-primary {
  color: #2e2113;
  background: linear-gradient(180deg, #fff2bb, #d89442);
  border: 1px solid rgba(255, 247, 214, 0.8);
  box-shadow: 0 0 26px rgba(246, 211, 110, 0.24);
}

.opening-secondary {
  color: #fff7df;
  background: rgba(10, 16, 28, 0.5);
  border: 1px solid rgba(255, 239, 198, 0.3);
}

.opening-status {
  position: absolute;
  right: clamp(1rem, 4vw, 4rem);
  bottom: clamp(1rem, 4vw, 3rem);
  z-index: 2;
  display: flex;
  gap: 0.5rem;
  color: rgba(255, 247, 223, 0.82);
  font-size: 0.78rem;
  font-weight: 800;
}

.opening-status span {
  padding: 0.28rem 0.55rem;
  border-radius: 999px;
  background: rgba(5, 10, 18, 0.5);
  border: 1px solid rgba(255, 239, 198, 0.18);
}

.opening-cinematic-enter-active,
.opening-cinematic-leave-active {
  transition: opacity 0.45s ease, transform 0.45s ease;
}

.opening-cinematic-enter-from,
.opening-cinematic-leave-to {
  opacity: 0;
  transform: scale(1.01);
}

@keyframes opening-drift {
  from { transform: scale(1.1) translate3d(1.5%, -1%, 0); }
  to { transform: scale(1.04) translate3d(0, 0, 0); }
}

@keyframes opening-rain {
  from { background-position: 0 0, 0 0; }
  to { background-position: -28px 72px, 0 0; }
}

@media (max-width: 720px) {
  .opening-cinematic-root {
    align-items: end;
    padding: 1rem 1rem 6.2rem;
  }

  .opening-bg {
    background:
      linear-gradient(180deg, rgba(6, 10, 18, 0.16) 0%, rgba(6, 10, 18, 0.88) 72%),
      url('/assets/game/field-bg-tv-v3.jpg') center / cover no-repeat;
  }

  .opening-copy h1 {
    font-size: 3.35rem;
  }

  .opening-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }

  .opening-actions button {
    padding: 0 0.55rem;
    font-size: 0.88rem;
  }

  .opening-status {
    left: 1rem;
    right: auto;
    bottom: 1rem;
    flex-wrap: wrap;
  }
}
</style>
