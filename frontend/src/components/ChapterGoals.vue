<template>
  <div class="card chapter-goals">
    <div class="card-title">序章目标</div>
    <ul class="goal-list">
      <li :class="{ done: act0Done }">
        <span class="mark">{{ act0Done ? '✓' : '○' }}</span>
        第一幕 · 日常：村庄会合、巨神树天职、禁忌目录之夜
      </li>
      <li :class="{ done: act1Done }">
        <span class="mark">{{ act1Done ? '✓' : '○' }}</span>
        第二幕 · 越界：出发尽头山脉、受伤者、爱丽丝越界、返村
      </li>
      <li :class="{ done: act2Done }">
        <span class="mark">{{ act2Done ? '✓' : '○' }}</span>
        第三幕 · 宣判与告别：骑士进村、告别、被带走
      </li>
    </ul>
    <p class="goal-hint">主线以爱丽丝被带走收束；过程中的选择会写入关系、记忆与回响。</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  state: { type: Object, required: true },
  flags: { type: Object, required: true }
})

const doneIds = computed(
  () => new Set(Array.isArray(props.state?.completed_event_ids) ? props.state.completed_event_ids : [])
)

const ACTS = [
  ['ch1pc_n01_rulid_daily', 'ch1pc_n02_gigas_calling', 'ch1pc_n03_talk_index_end_mountains'],
  ['ch1pc_n04_travel_to_end_mountains', 'ch1pc_n05_encounter_dark_territory_injured', 'ch1pc_n06_alice_crosses_boundary', 'ch1pc_n07_return_to_rulid'],
  ['ch1pc_n08_knights_arrive_village', 'ch1pc_n09_alice_farewell', 'ch1pc_n10_alice_captured']
]

const act0Done = computed(() => ACTS[0].every((id) => doneIds.value.has(id)))
const act1Done = computed(() => ACTS[1].every((id) => doneIds.value.has(id)))
const act2Done = computed(() => ACTS[2].every((id) => doneIds.value.has(id)))
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
