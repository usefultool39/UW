<template>
  <div class="card chapter-goals">
    <div class="card-title">第一章目标</div>
    <ul class="goal-list">
      <li :class="{ done: treeWeakened }">
        <span class="mark">{{ treeWeakened ? '✓' : '○' }}</span>
        削弱巨树：HP 低于 50%（{{ treeHp }} / {{ treeMax }}）
      </li>
      <li :class="{ done: flags.c1Done }">
        <span class="mark">{{ flags.c1Done ? '✓' : '○' }}</span>
        在伐木节奏点做出抉择（约 Tick 10–29 触发）
      </li>
      <li :class="{ done: flags.c2Done }">
        <span class="mark">{{ flags.c2Done ? '✓' : '○' }}</span>
        在食桌时段完成膳食抉择（Tick ≥ 30）
      </li>
    </ul>
    <p class="goal-hint">击倒巨树后将依羁绊倾向展示第一章收束。</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  state: { type: Object, required: true },
  flags: { type: Object, required: true }
})

const treeHp = computed(() => props.state?.tree?.hp ?? 0)
const treeMax = computed(() => props.state?.tree?.hp_max ?? 1)

const treeWeakened = computed(() => {
  const max = treeMax.value || 1
  return treeHp.value <= max * 0.5
})
</script>

<style scoped>
.chapter-goals {
  font-size: 0.78rem;
}

.goal-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.goal-list li {
  display: flex;
  gap: 0.4rem;
  align-items: flex-start;
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--sao-border-dim);
  color: var(--muted);
  line-height: 1.45;
}

.goal-list li.done {
  color: var(--ok);
}

.mark {
  flex-shrink: 0;
  width: 1.1rem;
  font-weight: 700;
}

.goal-hint {
  margin-top: 0.55rem;
  font-size: 0.68rem;
  color: var(--muted);
  line-height: 1.5;
}
</style>
