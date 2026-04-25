<template>
  <div class="mmo-player-frame">
    <div class="avatar-disc">
      <img v-if="avatarUrl" :src="avatarUrl" alt="玩家头像" @error="imgError = true" />
      <span v-else>你</span>
    </div>
    <div class="player-vitals">
      <div class="vital-name">{{ playerName }}</div>
      <div class="bar hp"><span :style="{ width: hpPercent + '%' }"></span></div>
      <div class="bar mp"><span :style="{ width: mpPercent + '%' }"></span></div>
      <div class="bar stamina"><span :style="{ width: staminaPercent + '%' }"></span></div>
    </div>
    <div class="player-meta">
      <span class="meta-tag day">Day {{ day }}</span>
      <span class="meta-tag scene">{{ sceneLabel }}</span>
      <span class="meta-tag weather">{{ weatherLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  simState: { type: Object, default: null },
  sceneLabel: { type: String, default: '——' }
})

const imgError = ref(false)
const avatarUrl = computed(() => {
  if (imgError.value) return null
  return '/assets/game/player-token-tv.png'
})

const playerName = computed(() =>
  props.simState?.player?.name || '外来者 · Lv.1'
)

const day = computed(() => props.simState?.day ?? 1)
const weatherLabel = computed(() => props.simState?.weather_label || '晴朗')

const hpPercent = computed(() => {
  const hp = props.simState?.player?.hp
  const maxHp = props.simState?.player?.max_hp
  if (!Number.isFinite(hp) || !Number.isFinite(maxHp) || maxHp === 0) return 92
  return Math.round((hp / maxHp) * 100)
})

const mpPercent = computed(() => {
  const mp = props.simState?.player?.mp
  const maxMp = props.simState?.player?.max_mp
  if (!Number.isFinite(mp) || !Number.isFinite(maxMp) || maxMp === 0) return 68
  return Math.round((mp / maxMp) * 100)
})
const staminaPercent = computed(() => {
  const s = props.simState?.player?.stamina
  const maxS = props.simState?.player?.max_stamina
  if (!Number.isFinite(s) || !Number.isFinite(maxS) || maxS === 0) return 100
  return Math.round((s / maxS) * 100)
})
</script>

<style scoped>
.mmo-player-frame {
  position: absolute;
  z-index: 3;
  top: 0.75rem;
  left: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: min(300px, calc(100% - 1.5rem));
  padding: 0.58rem 0.72rem;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(8, 13, 23, 0.9), rgba(16, 28, 45, 0.75));
  border: 1px solid rgba(229, 196, 92, 0.36);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.32);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  pointer-events: none;
}

.avatar-disc {
  flex: 0 0 auto;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 50%;
  display: grid;
  place-items: center;
  overflow: hidden;
  color: #fff8dc;
  font-weight: 800;
  font-size: 0.85rem;
  background:
    radial-gradient(circle at 38% 30%, rgba(255, 255, 255, 0.35), transparent 28%),
    linear-gradient(145deg, #b67a28, #4a2d16 72%);
  border: 2px solid rgba(255, 232, 151, 0.68);
  box-shadow: 0 0 14px rgba(212, 175, 55, 0.2);
}

.avatar-disc img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.player-vitals {
  flex: 1;
  min-width: 0;
}

.vital-name {
  font-size: 0.75rem;
  color: #fff7d6;
  font-weight: 800;
  margin-bottom: 0.22rem;
  text-shadow: 0 1px 2px #000;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar {
  height: 0.42rem;
  border-radius: 999px;
  overflow: hidden;
  margin-top: 0.2rem;
  background: rgba(2, 6, 14, 0.82);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  transition: width 0.4s ease;
}

.bar.hp span {
  background: linear-gradient(90deg, #e11d48, #fb7185);
}

.bar.mp span {
  background: linear-gradient(90deg, #0ea5e9, #67e8f9);
}

.bar.stamina span {
  background: linear-gradient(90deg, #f59e0b, #fcd34d);
}

.player-meta {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  flex: 0 0 auto;
}

.meta-tag {
  padding: 0.15rem 0.4rem;
  border-radius: 999px;
  font-size: 0.6rem;
  font-weight: 700;
  white-space: nowrap;
}

.meta-tag.day {
  background: rgba(201, 162, 39, 0.2);
  border: 1px solid rgba(201, 162, 39, 0.4);
  color: var(--sao-gold);
}

.meta-tag.scene {
  background: rgba(94, 207, 255, 0.12);
  border: 1px solid rgba(94, 207, 255, 0.22);
  color: var(--sao-cyan);
}

.meta-tag.weather {
  background: rgba(125, 211, 252, 0.1);
  border: 1px solid rgba(186, 230, 253, 0.18);
  color: #dbeafe;
}

@media (max-width: 900px) {
  .mmo-player-frame {
    width: min(260px, calc(100% - 1.1rem));
  }
}
</style>
