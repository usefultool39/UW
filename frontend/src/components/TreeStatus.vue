<template>
  <div class="card">
    <div class="card-title">巨树状态</div>
    <div class="tree-info">
      <div class="tree-name">基拉斯杉</div>
      <div class="tree-hp-text">
        生命值 <span class="nums">{{ formattedHp }}</span>
      </div>
      <div class="tree-hp-rpg" role="img" :aria-label="'生命值约 ' + Math.round(hpPercent) + '%'">
        <img class="hp-cap" src="/assets/kenney-ui/barBack_horizontalLeft.png" alt="" />
        <div class="hp-mid">
          <div class="hp-fill" :style="{ width: hpPercent + '%' }" />
        </div>
        <img class="hp-cap" src="/assets/kenney-ui/barBack_horizontalRight.png" alt="" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tree: { type: Object, required: true }
})

const hpPercent = computed(() => {
  const max = props.tree.hp_max || 1
  return Math.min(100, Math.max(0, (props.tree.hp / max) * 100))
})

const formattedHp = computed(() => {
  return (props.tree.hp || 0).toLocaleString()
})
</script>

<style scoped>
.tree-info {
  text-align: center;
  padding: 0.45rem 0.25rem;
}

.tree-name {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--ok);
  letter-spacing: 0.06em;
}

.tree-hp-text {
  font-size: 0.85rem;
  color: var(--muted);
  margin-top: 0.35rem;
}

.nums {
  font-variant-numeric: tabular-nums;
}

.tree-hp-rpg {
  display: flex;
  align-items: center;
  margin-top: 0.65rem;
  height: 22px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.35));
}

.hp-cap {
  height: 22px;
  width: auto;
  display: block;
  flex-shrink: 0;
  image-rendering: pixelated;
}

.hp-mid {
  flex: 1;
  height: 16px;
  margin: 0 -1px;
  background: url("/assets/kenney-ui/barBack_horizontalMid.png") repeat-x center;
  background-size: auto 100%;
  position: relative;
  min-width: 24px;
}

.hp-fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  max-width: 100%;
  border-radius: 2px;
  background: url("/assets/kenney-ui/barBlue_horizontalBlue.png") repeat-x center;
  background-size: auto 100%;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25);
  transition: width 0.45s cubic-bezier(0.22, 1, 0.36, 1);
}

@media (prefers-reduced-motion: reduce) {
  .hp-fill {
    transition: none;
  }
}
</style>
