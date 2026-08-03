<template>
  <div
    v-show="modelValue && npc"
    class="dialogue-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="emit('update:modelValue', false)"
  >
    <section class="dialogue-panel" @click.stop>
      <header class="dialogue-header">
        <div>
          <p class="dialogue-kicker">对话</p>
          <h3>{{ displayName }}</h3>
        </div>
        <button
          type="button"
          class="dialogue-close"
          aria-label="关闭"
          @click="emit('update:modelValue', false)"
        >
          ×
        </button>
      </header>

      <div class="dialogue-log" aria-live="polite">
        <div v-if="!messages.length" class="dialogue-empty">
          {{ displayName }} 正看着你，等待你先开口。
        </div>
        <article
          v-for="(item, index) in messages"
          :key="index"
          class="dialogue-line"
          :class="item.role"
        >
          <span>{{ item.role === 'player' ? '你' : displayName }}</span>
          <p>{{ item.text }}</p>
        </article>
      </div>

      <form class="dialogue-form" @submit.prevent="submit">
        <input
          v-model="draft"
          type="text"
          :disabled="busy"
          maxlength="120"
          placeholder="问问边界、书库、训练，或只是打个招呼"
        />
        <button type="submit" class="dialogue-send" :disabled="busy || !draft.trim()">
          {{ busy ? '等待' : '发送' }}
        </button>
      </form>

      <p v-if="memoryHint" class="memory-hint">{{ memoryHint }}</p>
    </section>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  npc: { type: Object, default: null },
  modelValue: { type: Boolean, default: false },
  sendDialogue: { type: Function, required: true },
  playerSceneId: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const NAMES = {
  alice: '爱丽丝',
  eugeo: '尤吉欧',
  kirito: '凛斗'
}

const draft = ref('')
const busy = ref(false)
const messages = ref([])
const memoryHint = ref('')

const displayName = computed(() => NAMES[props.npc?.id] || props.npc?.id || 'NPC')

watch(
  () => props.npc?.id,
  () => {
    draft.value = ''
    messages.value = []
    memoryHint.value = ''
  }
)

async function submit() {
  const text = draft.value.trim()
  if (!text || !props.npc?.id || busy.value) return
  messages.value.push({ role: 'player', text })
  draft.value = ''
  busy.value = true
  memoryHint.value = ''
  try {
    const res = await props.sendDialogue({
      npc_id: props.npc.id,
      message: text,
      context: { scene_id: props.playerSceneId }
    })
    messages.value.push({ role: 'npc', text: res.reply || '……' })
    if (res.memory_committed && res.memory_candidate?.summary) {
      memoryHint.value = `${displayName.value} 记住了：${res.memory_candidate.summary}`
    }
  } catch (e) {
    messages.value.push({ role: 'npc', text: e.message || '对话失败，请稍后再试。' })
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.dialogue-backdrop {
  position: fixed;
  inset: 0;
  z-index: 84;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 1rem;
  background: linear-gradient(180deg, rgba(4, 8, 18, 0.35), rgba(4, 8, 18, 0.86));
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  animation: modal-backdrop-in 0.18s ease-out both;
}

.dialogue-panel {
  width: min(94vw, 940px);
  max-height: min(88vh, 760px);
  display: flex;
  flex-direction: column;
  padding: 1.2rem;
  border-radius: 16px;
  background: rgba(9, 14, 26, 0.96);
  border: 1px solid rgba(94, 207, 255, 0.34);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.58), 0 0 24px rgba(94, 207, 255, 0.12);
  animation: dialogue-rise-in 0.22s ease-out both;
}

@keyframes modal-backdrop-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes dialogue-rise-in {
  from {
    opacity: 0;
    transform: translateY(18px) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.dialogue-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  padding-bottom: 0.7rem;
  border-bottom: 1px solid rgba(94, 207, 255, 0.16);
}

.dialogue-kicker {
  margin: 0 0 0.15rem;
  font-size: 0.62rem;
  color: var(--sao-cyan);
  letter-spacing: 0.14em;
  font-weight: 700;
}

.dialogue-header h3 {
  margin: 0;
  font-size: 1.45rem;
}

.dialogue-close {
  flex: 0 0 auto;
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 8px;
  padding: 0;
  font-size: 1.25rem;
  line-height: 1;
}

.dialogue-log {
  min-height: 320px;
  overflow: auto;
  padding: 0.8rem 0.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.dialogue-empty {
  margin: auto;
  color: var(--muted);
  font-size: 1rem;
}

.dialogue-line {
  max-width: 78%;
}

.dialogue-line.player {
  align-self: flex-end;
}

.dialogue-line span {
  display: block;
  margin-bottom: 0.22rem;
  font-size: 0.78rem;
  color: var(--muted);
}

.dialogue-line p {
  margin: 0;
  padding: 0.78rem 0.95rem;
  border-radius: 12px;
  font-size: 1rem;
  line-height: 1.65;
  background: rgba(24, 37, 58, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.dialogue-line.player p {
  background: rgba(14, 116, 144, 0.48);
  border-color: rgba(103, 232, 249, 0.24);
}

.dialogue-form {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 0.55rem;
  padding-top: 0.7rem;
  border-top: 1px solid rgba(94, 207, 255, 0.16);
}

.dialogue-form input {
  min-width: 0;
  min-height: 3rem;
  font-size: 1rem;
}

.dialogue-send {
  min-width: 6.5rem;
  font-size: 1rem;
}

.memory-hint {
  margin: 0.65rem 0 0;
  padding: 0.45rem 0.55rem;
  border-radius: 9px;
  color: #d1fae5;
  background: rgba(16, 185, 129, 0.13);
  border: 1px solid rgba(110, 231, 183, 0.22);
  font-size: 0.9rem;
  line-height: 1.45;
}

@media (max-width: 640px) {
  .dialogue-form {
    grid-template-columns: 1fr;
  }

  .dialogue-line {
    max-width: 92%;
  }
}
</style>
