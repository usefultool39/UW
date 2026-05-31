<template>
  <header class="field-header">
    <div class="field-title">
      <p class="field-kicker">{{ GAME_CHAPTER_INFO.kicker }}</p>
      <h2>{{ GAME_CHAPTER_INFO.title }}</h2>
    </div>
    <div class="header-actions">
      <button type="button" class="tb tb-ghost save-action" :disabled="busy" @click="$emit('export-save')">
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M3 17h14v-2H3v2zm9-9L6 12h4v4h4v-4h4l-6-6z"/></svg>存档
      </button>
      <button type="button" class="tb tb-ghost save-action" :disabled="busy" @click="$emit('import-save')">
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M17 17H3v-2h14v2zm-6-8L6 13h4v4h4v-4h4l-6-6z"/></svg>读档
      </button>
      <button type="button" class="tb tb-ghost sync-action" :disabled="busy" @click="$emit('refresh')">
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M10 3v2a5 5 0 0 1 5.12 4.87l-1.02-1.74A3 3 0 1 0 14 10h2l-2-3-2 3H9a3 3 0 0 0 0 6 5 5 0 0 1 .12 9.95L10 17v-3H7l2-3 2 3h-1z"/></svg>同步
      </button>
      <div class="audio-cluster">
        <button type="button" class="tb tb-ghost audio-action" :title="audioTitle" @click="onAudioClick">
          <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
            <path v-if="isMuted" d="M4 7h3l4-4v14l-4-4H4V7zm10.6 2.4 1.4-1.4 1.5 1.5L19 8l1 1-1.5 1.5L20 12l-1 1-1.5-1.5L16 13l-1.4-1.4 1.5-1.6-1.5-1.6z"/>
            <path v-else d="M3 7h4l5-4v14l-5-4H3V7zm11.2 1.1 1.2-1.2A4.7 4.7 0 0 1 17 10a4.7 4.7 0 0 1-1.6 3.1l-1.2-1.2A3 3 0 0 0 15.2 10a3 3 0 0 0-1-1.9z"/>
          </svg>{{ audioLabel }}
        </button>
        <input
          class="audio-volume"
          type="range"
          min="0"
          max="1"
          step="0.05"
          :value="currentVolume"
          aria-label="音量"
          @input="setVolume(Number($event.target.value))"
        />
      </div>
      <button type="button" class="tb tb-primary" :disabled="busy" @click="$emit('daily')">
        <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor"><path d="M6 3l1.5 3.5L11 5l-1.5 3.5L14 11l-3.5 1.5L11 16l-.5-3.5L7 14l-3.5-1.5L4 9l3.5-1.5L6 3z"/></svg>时间推进
      </button>
    </div>
    <input
      ref="saveFileEl"
      class="save-file"
      type="file"
      accept="application/json,.json"
      @change="$emit('import-file', $event)"
    />
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { GAME_CHAPTER_INFO } from '../field/gameContentConfig.js'
import { useAudio } from '../composables/useAudio.js'

defineProps({
  busy: { type: Boolean, default: false }
})

defineEmits([
  'export-save',
  'import-save',
  'import-file',
  'refresh',
  'daily'
])

const { isMuted, currentVolume, bgmPlaying, toggleMute, setVolume, startFieldAudio } = useAudio()

const audioLabel = computed(() => {
  if (isMuted.value) return '恢复'
  return bgmPlaying.value ? '声景' : '开启声景'
})

const audioTitle = computed(() => {
  if (isMuted.value) return '恢复音乐和环境声'
  return bgmPlaying.value ? '静音' : '开启清晨音乐和细雨环境声'
})

async function onAudioClick() {
  if (isMuted.value) {
    toggleMute()
    await startFieldAudio('drizzle')
    return
  }
  if (!bgmPlaying.value) {
    await startFieldAudio('drizzle')
    return
  }
  toggleMute()
}
</script>

<style scoped>
.field-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.55rem;
  flex-wrap: wrap;
}

.field-title {
  flex: 0 0 auto;
}

.field-kicker {
  margin: 0 0 0.1rem;
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  color: var(--sao-gold);
  font-weight: 700;
  text-transform: uppercase;
}

.field-title h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: 0;
  background: linear-gradient(110deg, #fff7df 0%, #ffe2a3 55%, #9bd5d7 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.save-file {
  display: none;
}

/* Toolbar buttons */
.tb {
  font-size: 0.74rem;
  padding: 0.36rem 0.6rem;
  border-radius: 8px;
  border: 1px solid var(--sao-border-dim);
  background: rgba(67, 51, 31, 0.55);
  color: var(--ink);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease, transform 0.12s ease;
  will-change: transform;
}

.tb:hover:not(:disabled) {
  background: rgba(255, 239, 198, 0.12);
  border-color: var(--sao-border);
  box-shadow: var(--sao-glow);
}

.tb:active:not(:disabled) {
  transform: translateY(1px);
}

.tb:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.tb-ghost {
  background: rgba(43, 38, 25, 0.54);
}

.audio-cluster {
  display: inline-flex;
  align-items: center;
  gap: 0.32rem;
}

.tb-primary {
  background: linear-gradient(180deg, #c98242, #9f5b35);
  border-color: rgba(255, 226, 163, 0.42);
  color: #fff;
  font-weight: 600;
}

.tb-primary:hover:not(:disabled) {
  border-color: rgba(255, 226, 163, 0.78);
  box-shadow: 0 0 18px rgba(241, 199, 107, 0.28);
}

.audio-volume {
  width: 4.6rem;
  accent-color: var(--sao-gold);
}

.btn-icon {
  width: 0.85rem;
  height: 0.85rem;
  flex: 0 0 auto;
}

@media (max-width: 900px) {
  .field-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .save-action,
  .sync-action,
  .audio-volume {
    display: none;
  }

  .tb-primary {
    flex: 0 0 auto;
    min-width: 7rem;
    justify-content: center;
  }
}
</style>
