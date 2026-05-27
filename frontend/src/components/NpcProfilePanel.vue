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

      <section v-if="profile?.mind" class="mind-section">
        <div class="mind-head">
          <h4>当前目标与主观判断</h4>
          <span>{{ profile.mind.attitude || '平稳' }}</span>
        </div>
        <dl class="mind-grid">
          <div>
            <dt>现在想做</dt>
            <dd>{{ profile.mind.current_goal || '观察今天的变化' }}</dd>
          </div>
          <div>
            <dt>正在在意</dt>
            <dd>{{ profile.mind.active_focus || '暂无主动邀约' }}</dd>
          </div>
          <div>
            <dt>状态倾向</dt>
            <dd>{{ profile.mind.need || '状态平稳' }}</dd>
          </div>
        </dl>
        <p class="mind-reason">{{ profile.mind.active_reason }}</p>
        <ul v-if="mindBeliefs.length">
          <li v-for="item in mindBeliefs" :key="item">{{ item }}</li>
        </ul>
      </section>

      <section class="attitude-source">
        <div class="attitude-head">
          <h4>最近态度来源</h4>
          <span>{{ strongestSignal }}</span>
        </div>
        <p>{{ attitudeReason }}</p>
        <ul v-if="attitudeDetails.length">
          <li v-for="item in attitudeDetails" :key="item">{{ item }}</li>
        </ul>
      </section>

      <section class="memory-section">
        <h4>重要记忆</h4>
        <p v-if="!uniqueMemories.length" class="empty">还没有留下关键记忆。</p>
        <ul v-else>
          <li v-for="item in uniqueMemories" :key="item.recorded_at || item.summary">
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
const mindBeliefs = computed(() =>
  Array.isArray(props.profile?.mind?.beliefs) ? props.profile.mind.beliefs : []
)

const latestMemory = computed(() => {
  return uniqueMemories.value[0]?.summary || ''
})

const uniqueMemories = computed(() => {
  const memories = Array.isArray(props.profile?.important_memories) ? props.profile.important_memories : []
  const seen = new Set()
  return memories
    .filter((item) => {
      const summary = String(item?.summary || '').trim()
      if (!summary || seen.has(summary)) return false
      seen.add(summary)
      return true
    })
    .slice(0, 5)
})

const strongestSignal = computed(() => {
  const items = [
    { label: '好感', value: Number(rel.value.affinity || 0) },
    { label: '信任', value: Number(rel.value.trust || 0) },
    { label: '紧张', value: Number(rel.value.tension || 0) }
  ].sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
  const top = items[0]
  if (!top || top.value === 0) return '关系平稳'
  const sign = top.value > 0 ? '+' : ''
  return `${top.label} ${sign}${top.value}`
})

const attitudeReason = computed(() => {
  const trust = Number(rel.value.trust || 0)
  const affinity = Number(rel.value.affinity || 0)
  const tension = Number(rel.value.tension || 0)
  if (latestMemory.value) {
    if (tension >= 5) return `最近让 TA 放不下的是：${latestMemory.value}`
    if (trust >= 5) return `TA 现在更愿意相信你，因为记住了：${latestMemory.value}`
    if (affinity >= 5) return `TA 对你更亲近，最近的记忆是：${latestMemory.value}`
    return `最近留下的主要印象是：${latestMemory.value}`
  }
  if (tension > trust && tension > affinity) return 'TA 还没有关键记忆，但当前紧张值最高，说明最近的选择让关系略微绷紧。'
  if (trust > 0 || affinity > 0) return 'TA 还没有写下关键记忆，但关系数值已经开始向正面移动。'
  return 'TA 还没有形成明确态度来源。完成剧情选择或对话后，这里会显示最近原因。'
})

const attitudeDetails = computed(() => {
  const out = []
  const promises = Array.isArray(props.profile?.promises) ? props.profile.promises : []
  const tensions = Array.isArray(props.profile?.tensions) ? props.profile.tensions : []
  if (promises[0]) out.push(`承诺：${promises[0]}`)
  if (tensions[0]) out.push(`不安：${tensions[0]}`)
  if (!promises[0] && !tensions[0] && latestMemory.value) out.push('这条记忆会影响后续对话的语气。')
  return out
})
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
  width: min(94vw, 720px);
  max-height: min(88vh, 720px);
  overflow: auto;
  padding: 1.25rem;
  border-radius: 16px;
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
  font-size: 1.45rem;
}

.profile-close {
  width: 2.4rem;
  height: 2.4rem;
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
  font-size: 1rem;
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
  font-size: 0.82rem;
}

.relation-grid dd {
  margin: 0.18rem 0 0;
  color: #f8fafc;
  font-weight: 800;
  font-size: 1.12rem;
}

.relation-note {
  margin: 0 0 0.8rem;
  padding: 0.5rem 0.6rem;
  border-radius: 10px;
  color: #dbeafe;
  background: rgba(30, 64, 175, 0.18);
  border: 1px solid rgba(147, 197, 253, 0.18);
  font-size: 0.96rem;
}

.attitude-source {
  margin: 0 0 0.85rem;
  padding: 0.68rem 0.72rem;
  border-radius: 10px;
  color: #e2e8f0;
  background: rgba(120, 83, 35, 0.16);
  border: 1px solid rgba(246, 211, 110, 0.24);
}

.mind-section {
  margin: 0 0 0.85rem;
  padding: 0.72rem;
  border-radius: 10px;
  background: rgba(14, 116, 144, 0.13);
  border: 1px solid rgba(125, 211, 252, 0.24);
}

.mind-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.55rem;
  margin-bottom: 0.5rem;
}

.mind-head h4 {
  margin: 0;
  color: #bae6fd;
  font-size: 0.94rem;
}

.mind-head span {
  flex: 0 0 auto;
  padding: 0.16rem 0.42rem;
  border-radius: 999px;
  color: #e0f2fe;
  background: rgba(14, 116, 144, 0.5);
  border: 1px solid rgba(125, 211, 252, 0.28);
  font-size: 0.72rem;
  font-weight: 900;
}

.mind-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.45rem;
  margin: 0;
}

.mind-grid div {
  padding: 0.52rem;
  border-radius: 9px;
  background: rgba(15, 23, 42, 0.56);
  border: 1px solid rgba(125, 211, 252, 0.14);
}

.mind-grid dt {
  color: #bae6fd;
  font-size: 0.72rem;
  font-weight: 800;
}

.mind-grid dd {
  margin: 0.22rem 0 0;
  color: #f8fafc;
  font-size: 0.86rem;
  line-height: 1.45;
}

.mind-reason {
  margin: 0.54rem 0 0;
  color: #dbeafe;
  font-size: 0.88rem;
  line-height: 1.5;
}

.mind-section ul {
  margin: 0.42rem 0 0;
  padding-left: 1rem;
  color: #e0f2fe;
  font-size: 0.86rem;
  line-height: 1.5;
}

.attitude-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.55rem;
  margin-bottom: 0.34rem;
}

.attitude-head h4 {
  margin: 0;
  color: var(--sao-gold);
  font-size: 0.94rem;
}

.attitude-head span {
  flex: 0 0 auto;
  padding: 0.16rem 0.42rem;
  border-radius: 999px;
  color: #fff7d6;
  background: rgba(120, 83, 35, 0.58);
  border: 1px solid rgba(246, 211, 110, 0.28);
  font-size: 0.72rem;
  font-weight: 900;
}

.attitude-source p {
  margin: 0;
  color: #f8fafc;
  font-size: 0.94rem;
  line-height: 1.55;
}

.attitude-source ul {
  margin: 0.38rem 0 0;
  padding-left: 1rem;
  color: #dbeafe;
  font-size: 0.86rem;
  line-height: 1.5;
}

.memory-section {
  margin-top: 0.75rem;
}

.memory-section h4 {
  margin: 0 0 0.35rem;
  font-size: 0.94rem;
  color: var(--sao-gold);
}

.memory-section ul {
  margin: 0;
  padding-left: 1rem;
  color: #e2e8f0;
  font-size: 0.94rem;
  line-height: 1.55;
}

.empty {
  margin: 0;
  color: var(--muted);
  font-size: 0.94rem;
}

@media (max-width: 640px) {
  .mind-grid {
    grid-template-columns: 1fr;
  }

  .mind-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
