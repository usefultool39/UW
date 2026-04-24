<template>
  <div
    v-show="modelValue && profile"
    class="profile-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="emit('update:modelValue', false)"
  >
    <section class="profile-panel" @click.stop>
      <header class="profile-header">
        <div>
          <p class="profile-kicker">关系档案</p>
          <h3>{{ profile?.display }}</h3>
        </div>
        <button
          type="button"
          class="profile-close"
          aria-label="关闭"
          @click="emit('update:modelValue', false)"
        >
          ×
        </button>
      </header>

      <p class="profile-role">{{ profile?.role }}</p>

      <dl class="relation-grid">
        <div>
          <dt>好感</dt>
          <dd>{{ rel.affinity }}</dd>
        </div>
        <div>
          <dt>信任</dt>
          <dd>{{ rel.trust }}</dd>
        </div>
        <div>
          <dt>紧张</dt>
          <dd>{{ rel.tension }}</dd>
        </div>
      </dl>

      <p class="relation-note">{{ rel.note || rel.mood_note || '平稳' }}</p>

      <section class="memory-section">
        <h4>重要记忆</h4>
        <p v-if="!profile?.important_memories?.length" class="empty">还没有留下关键记忆。</p>
        <ul v-else>
          <li v-for="item in profile.important_memories.slice(0, 5)" :key="item.recorded_at || item.summary">
            {{ item.summary }}
          </li>
        </ul>
      </section>

      <section v-if="profile?.promises?.length" class="memory-section">
        <h4>承诺</h4>
        <ul>
          <li v-for="item in profile.promises" :key="item">{{ item }}</li>
        </ul>
      </section>

      <section v-if="profile?.tensions?.length" class="memory-section">
        <h4>紧张点</h4>
        <ul>
          <li v-for="item in profile.tensions" :key="item">{{ item }}</li>
        </ul>
      </section>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  profile: { type: Object, default: null },
  modelValue: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

const rel = computed(() => props.profile?.relationship || {})
</script>

<style scoped>
.profile-backdrop {
  position: fixed;
  inset: 0;
  z-index: 88;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(4, 8, 18, 0.76);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.profile-panel {
  width: min(94vw, 460px);
  max-height: min(88vh, 640px);
  overflow: auto;
  padding: 1rem;
  border-radius: 12px;
  background: linear-gradient(165deg, rgba(25, 37, 56, 0.98), rgba(8, 12, 22, 0.98));
  border: 1px solid rgba(94, 207, 255, 0.32);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55), 0 0 24px rgba(94, 207, 255, 0.1);
}

.profile-header {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  padding-bottom: 0.72rem;
  border-bottom: 1px solid rgba(94, 207, 255, 0.16);
}

.profile-kicker {
  margin: 0 0 0.15rem;
  font-size: 0.62rem;
  letter-spacing: 0.14em;
  color: var(--sao-cyan);
  font-weight: 800;
}

.profile-header h3 {
  margin: 0;
  font-size: 1.18rem;
}

.profile-close {
  width: 2rem;
  height: 2rem;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(51, 65, 85, 0.6);
  color: #e2e8f0;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}

.profile-role {
  margin: 0.72rem 0;
  color: #cbd5e1;
  font-size: 0.82rem;
}

.relation-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.45rem;
  margin: 0 0 0.65rem;
}

.relation-grid div {
  padding: 0.55rem;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.relation-grid dt {
  color: var(--muted);
  font-size: 0.68rem;
}

.relation-grid dd {
  margin: 0.18rem 0 0;
  color: #f8fafc;
  font-weight: 800;
}

.relation-note {
  margin: 0 0 0.8rem;
  padding: 0.5rem 0.6rem;
  border-radius: 10px;
  color: #dbeafe;
  background: rgba(30, 64, 175, 0.18);
  border: 1px solid rgba(147, 197, 253, 0.18);
  font-size: 0.8rem;
}

.memory-section {
  margin-top: 0.75rem;
}

.memory-section h4 {
  margin: 0 0 0.35rem;
  font-size: 0.78rem;
  color: var(--sao-gold);
}

.memory-section ul {
  margin: 0;
  padding-left: 1rem;
  color: #e2e8f0;
  font-size: 0.78rem;
  line-height: 1.55;
}

.empty {
  margin: 0;
  color: var(--muted);
  font-size: 0.78rem;
}
</style>
