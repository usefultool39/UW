<template>
  <div class="card">
    <div class="card-title">系统状态</div>
    <div class="time-display">
      <div class="day-text">第 <span class="nums">{{ state.day }}</span> 天</div>
      <div class="time-text">
        {{ displayHour }}:00
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  state: { type: Object, required: true }
})

const displayHour = computed(() => {
  const tick = props.state.tick || 0
  return Math.floor(tick * 24 / 61)
})
</script>

<style scoped>
.time-display {
  text-align: center;
  padding: 0.5rem;
}

.day-text {
  font-size: 1.45rem;
  font-weight: 800;
  color: var(--sao-cyan);
  letter-spacing: 0.04em;
}

.time-text {
  font-size: 1.1rem;
  color: var(--muted);
  margin-top: 0.35rem;
  font-variant-numeric: tabular-nums;
}

.nums {
  font-variant-numeric: tabular-nums;
}
</style>
