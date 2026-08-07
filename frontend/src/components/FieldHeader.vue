<template>
  <header class="field-header">
    <div class="field-title">
      <p class="field-kicker">{{ GAME_CHAPTER_INFO.kicker }}</p>
      <h2>{{ GAME_CHAPTER_INFO.title }}</h2>
    </div>

    <div class="header-actions">
      <span class="runtime-badge" :class="`runtime-${npcRuntime}`" :title="runtimeTitle">
        <i></i>{{ runtimeLabel }}
      </span>

      <div class="audio-cluster">
        <button type="button" class="tb tb-ghost audio-action" :title="audioTitle" @click="onAudioClick">
          <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path v-if="isMuted" d="M4 7h3l4-4v14l-4-4H4V7zm10.6 2.4 1.4-1.4 1.5 1.5L19 8l1 1-1.5 1.5L20 12l-1 1-1.5-1.5L16 13l-1.4-1.4 1.5-1.6-1.5-1.6z"/>
            <path v-else d="M3 7h4l5-4v14l-5-4H3V7zm11.2 1.1 1.2-1.2A4.7 4.7 0 0 1 17 10a4.7 4.7 0 0 1-1.6 3.1l-1.2-1.2A3 3 0 0 0 15.2 10a3 3 0 0 0-1-1.9z"/>
          </svg>
          {{ audioLabel }}
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

      <details class="system-menu">
        <summary class="tb tb-ghost">菜单</summary>
        <div class="system-menu-popover">
          <button type="button" :disabled="busy" @click="$emit('export-save')">保存进度</button>
          <button type="button" :disabled="busy" @click="$emit('import-save')">读取存档</button>
          <button type="button" :disabled="busy" @click="$emit('refresh')">同步状态</button>
        </div>
      </details>
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

const props = defineProps({
  busy: { type: Boolean, default: false },
  npcRuntime: { type: String, default: 'scripted' }
})

defineEmits(['export-save', 'import-save', 'import-file', 'refresh'])

const { isMuted, currentVolume, bgmPlaying, toggleMute, setVolume, startFieldAudio } = useAudio()

const audioLabel = computed(() => {
  if (isMuted.value) return '恢复声音'
  return bgmPlaying.value ? '声音' : '开启声音'
})

const audioTitle = computed(() => {
  if (isMuted.value) return '恢复音乐和环境声'
  return bgmPlaying.value ? '静音' : '开启音乐和环境声'
})

const npcRuntime = computed(() => ['scripted', 'hybrid', 'agent'].includes(props.npcRuntime) ? props.npcRuntime : 'scripted')
const runtimeLabel = computed(() => ({ scripted: '离线', hybrid: '混合', agent: '智能' })[npcRuntime.value])
const runtimeTitle = computed(() => ({
  scripted: '固定剧情与规则驱动，无需模型 API',
  hybrid: '关键剧情固定，普通表达可使用模型',
  agent: '模型提出意图，世界结果仍由规则校验'
})[npcRuntime.value])

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
  gap: 0.7rem;
}

.field-title { min-width: 0; }
.field-kicker {
  margin: 0 0 0.08rem;
  color: #f6d36e;
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.1em;
}
.field-title h2 {
  margin: 0;
  color: #fff7df;
  font-size: 1rem;
  line-height: 1.1;
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.42rem;
}

.runtime-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.32rem;
  padding: 0.28rem 0.48rem;
  border-radius: 999px;
  color: #dff8ff;
  background: rgba(8, 36, 46, 0.62);
  border: 1px solid rgba(125, 211, 252, 0.26);
  font-size: 0.66rem;
  font-weight: 900;
}
.runtime-badge i {
  width: 0.38rem;
  height: 0.38rem;
  border-radius: 50%;
  background: #7dd3fc;
  box-shadow: 0 0 8px rgba(125, 211, 252, 0.7);
}
.runtime-hybrid i { background: #f6d36e; }
.runtime-agent i { background: #a78bfa; }

.tb {
  min-height: 2rem;
  padding: 0.32rem 0.58rem;
  border-radius: 7px;
  font-size: 0.7rem;
  font-weight: 900;
  white-space: nowrap;
}
.tb-ghost {
  color: #fff7df;
  background: rgba(23, 29, 29, 0.62);
  border: 1px solid rgba(255, 239, 198, 0.18);
}
.btn-icon { width: 0.85rem; height: 0.85rem; margin-right: 0.2rem; vertical-align: -0.12rem; }
.audio-cluster { display: flex; align-items: center; gap: 0.32rem; }
.audio-volume { width: 4.5rem; accent-color: #f6d36e; }

.system-menu { position: relative; }
.system-menu summary { list-style: none; cursor: pointer; display: grid; place-items: center; }
.system-menu summary::-webkit-details-marker { display: none; }
.system-menu[open] summary { border-color: rgba(246, 211, 110, 0.54); }
.system-menu-popover {
  position: absolute;
  top: calc(100% + 0.45rem);
  right: 0;
  z-index: 90;
  width: 9.5rem;
  display: grid;
  gap: 0.32rem;
  padding: 0.48rem;
  border-radius: 9px;
  color: #fff7df;
  background: rgba(8, 13, 20, 0.96);
  border: 1px solid rgba(255, 239, 198, 0.22);
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.36);
}
.system-menu-popover button {
  width: 100%;
  min-height: 2.1rem;
  padding: 0.38rem 0.55rem;
  text-align: left;
  color: #fff7df;
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 239, 198, 0.14);
}
.save-file { display: none; }

@media (max-width: 760px) {
  .field-header { justify-content: flex-end; }
  .field-title, .audio-volume, .runtime-badge { display: none; }
  .header-actions { width: auto; }
}
</style>
