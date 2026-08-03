<template>
  <div class="mmo-player-frame">
    <div class="avatar-disc" aria-hidden="true">
      <div class="avatar-pixel" :style="avatarStyle">
        <span class="pixel-shadow"></span>
        <span class="pixel-cape"></span>
        <span class="pixel-head"></span>
        <span class="pixel-hair"></span>
        <span class="pixel-body"></span>
        <span class="pixel-accent"></span>
        <span class="pixel-leg left"></span>
        <span class="pixel-leg right"></span>
      </div>
    </div>
    <div class="player-vitals">
      <div class="vital-name">{{ playerName }}</div>
      <div class="bar hp" :aria-label="`生命 ${hpValue}/${maxHpValue}`"><span :style="{ width: hpPercent + '%' }"></span><b>HP {{ hpValue }}</b></div>
      <div class="bar mp" :aria-label="`神圣力 ${mpValue}/${maxMpValue}`"><span :style="{ width: mpPercent + '%' }"></span><b>MP {{ mpValue }}</b></div>
      <div class="bar stamina" :aria-label="`体力 ${staminaValue}/${maxStaminaValue}`"><span :style="{ width: staminaPercent + '%' }"></span><b>ST {{ staminaValue }}</b></div>
    </div>
    <div class="player-meta">
      <span class="meta-tag day">Day {{ day }}</span>
      <span class="meta-tag scene">{{ sceneLabel }}</span>
      <span class="meta-tag weather">{{ weatherLabel }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { AGENTS } from '../field/gameContentConfig.js'

const props = defineProps({
  simState: { type: Object, default: null },
  sceneLabel: { type: String, default: '——' }
})

function toCssColor(value, fallback) {
  if (!Number.isFinite(value)) return fallback
  return `#${value.toString(16).padStart(6, '0')}`
}

const playerPalette = AGENTS.player?.palette || {}
const avatarStyle = {
  '--pixel-outline': toCssColor(playerPalette.outline, '#17110a'),
  '--pixel-hair': toCssColor(playerPalette.hair, '#2f2418'),
  '--pixel-skin': toCssColor(playerPalette.skin, '#e9c8a5'),
  '--pixel-body': toCssColor(playerPalette.body, '#263044'),
  '--pixel-accent': toCssColor(playerPalette.accent, '#f6d36e'),
  '--pixel-cape': toCssColor(playerPalette.cape, '#1f6f68'),
  '--pixel-boots': toCssColor(playerPalette.boots, '#2b2018')
}

const playerName = computed(() =>
  props.simState?.player?.name || `${AGENTS.player?.label || '凛斗'} · Lv.1`
)

const day = computed(() => props.simState?.day ?? 1)
const weatherLabel = computed(() => props.simState?.weather_label || '晴朗')
const hpValue = computed(() => Number(props.simState?.player?.hp ?? 100))
const maxHpValue = computed(() => Number(props.simState?.player?.max_hp ?? 100))
const mpValue = computed(() => Number(props.simState?.player?.mp ?? 100))
const maxMpValue = computed(() => Number(props.simState?.player?.max_mp ?? 100))
const staminaValue = computed(() => Number(props.simState?.player?.stamina ?? 100))
const maxStaminaValue = computed(() => Number(props.simState?.player?.max_stamina ?? 100))

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
  z-index: 40;
  top: 4.7rem;
  left: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: min(286px, calc(100% - 1.5rem));
  padding: 0.52rem 0.62rem;
  border-radius: 8px;
  background:
    linear-gradient(135deg, rgba(65, 48, 29, 0.88), rgba(39, 50, 32, 0.68)),
    radial-gradient(circle at 0% 0%, rgba(246, 211, 110, 0.16), transparent 42%);
  border: 1px solid rgba(255, 239, 198, 0.28);
  box-shadow: 0 8px 18px rgba(25, 18, 10, 0.24), inset 0 1px 0 rgba(255, 247, 214, 0.08);
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
    radial-gradient(circle at 38% 30%, rgba(255, 247, 214, 0.34), transparent 28%),
    linear-gradient(145deg, #6d5834, #1d2618 72%);
  border: 2px solid rgba(246, 211, 110, 0.66);
  box-shadow: 0 0 14px rgba(246, 211, 110, 0.18);
  image-rendering: pixelated;
}

.avatar-pixel {
  position: relative;
  width: 1.45rem;
  height: 1.85rem;
  transform: translateY(0.06rem);
}

.avatar-pixel span {
  position: absolute;
  display: block;
}

.pixel-shadow {
  left: 0.23rem;
  bottom: 0;
  width: 1rem;
  height: 0.18rem;
  background: rgba(0, 0, 0, 0.35);
}

.pixel-cape {
  left: 0.14rem;
  top: 0.72rem;
  width: 1.18rem;
  height: 0.84rem;
  background: var(--pixel-cape);
  border: 0.12rem solid var(--pixel-outline);
}

.pixel-head {
  left: 0.38rem;
  top: 0.27rem;
  width: 0.72rem;
  height: 0.62rem;
  background: var(--pixel-skin);
  border: 0.12rem solid var(--pixel-outline);
}

.pixel-hair {
  left: 0.3rem;
  top: 0.12rem;
  width: 0.9rem;
  height: 0.38rem;
  background: var(--pixel-hair);
  border: 0.12rem solid var(--pixel-outline);
}

.pixel-body {
  left: 0.34rem;
  top: 0.88rem;
  width: 0.82rem;
  height: 0.65rem;
  background: var(--pixel-body);
  border: 0.12rem solid var(--pixel-outline);
}

.pixel-accent {
  left: 0.58rem;
  top: 1rem;
  width: 0.34rem;
  height: 0.36rem;
  background: var(--pixel-accent);
}

.pixel-leg {
  top: 1.44rem;
  width: 0.34rem;
  height: 0.34rem;
  background: var(--pixel-boots);
  border: 0.1rem solid var(--pixel-outline);
}

.pixel-leg.left {
  left: 0.34rem;
}

.pixel-leg.right {
  right: 0.3rem;
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
  text-shadow: 0 1px 2px rgba(20, 14, 8, 0.8);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar {
  height: 0.42rem;
  border-radius: 999px;
  overflow: hidden;
  margin-top: 0.2rem;
  background: rgba(26, 20, 12, 0.7);
  border: 1px solid rgba(255, 239, 198, 0.12);
}

.bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  transition: width 0.4s ease;
}

.bar.hp span {
  background: linear-gradient(90deg, #b94a45, #df7b69);
}

.bar.mp span {
  background: linear-gradient(90deg, #4f8a92, #9bd5d7);
}

.bar.stamina span {
  background: linear-gradient(90deg, #c28a39, #f1c76b);
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
  background: rgba(155, 213, 215, 0.12);
  border: 1px solid rgba(155, 213, 215, 0.22);
  color: var(--sao-cyan);
}

.meta-tag.weather {
  background: rgba(134, 192, 108, 0.1);
  border: 1px solid rgba(210, 232, 168, 0.18);
  color: #edf7d2;
}

@media (max-width: 900px) {
  .mmo-player-frame {
    top: 0.55rem;
    left: 0.55rem;
    width: min(260px, calc(100% - 1.1rem));
  }
}
.bar { position: relative; }
.bar b { position: absolute; inset: 0 .24rem 0 auto; display: flex; align-items: center; color: rgba(255,255,255,.86); font-size: .5rem; line-height: 1; letter-spacing: .02em; text-shadow: 0 1px 2px rgba(0,0,0,.8); }
</style>
