<template>
  <div class="field-interact-root">
    <div
      v-show="modelValue && nearbyInteract"
      class="interact-backdrop"
      role="dialog"
      aria-modal="true"
      @click.self="emit('update:modelValue', false)"
    >
      <div class="interact-card" @click.stop>
        <header class="interact-card-hd">
          <div>
            <div v-if="regionLabel" class="interact-region">{{ regionLabel }}</div>
            <h3 class="interact-card-title">{{ displayInteractTitle }}</h3>
          </div>
          <button
            type="button"
            class="interact-close"
            aria-label="关闭"
            @click="emit('update:modelValue', false)"
          >
            ×
          </button>
        </header>
        <p class="interact-card-body">{{ displayInteractBody }}</p>
        <div class="interact-actions">
          <button
            v-for="act in displayVisibleInteractActions"
            :key="act.id"
            type="button"
            class="interact-action"
            :class="{
              blocked: !!act.blockedReason,
              recommended: act.type === 'story_event',
              relationship: act.activity?.interaction_kind === 'meal_choice' || act.type === 'npc_intent_response',
              challenge: act.activity?.interaction_kind === 'reading_keywords' || act.activity?.interaction_kind === 'training'
            }"
            :data-action-id="act.id"
            :data-action-type="act.type || ''"
            :data-activity-id="act.activity?.id || act.activity_id || ''"
            :disabled="busy || !!act.blockedReason"
            @click="emit('interact-action', act)"
          >
            <span class="action-kicker">{{ actionKicker(act) }}<b v-if="act.type === 'story_event'">建议优先</b></span>
            <span class="action-label">{{ act.label }}</span>
            <span v-if="act.meta" class="action-meta">{{ act.meta }}</span>
            <span v-if="act.description" class="action-desc">{{ act.description }}</span>
            <span class="action-outcome">{{ actionOutcome(act) }}</span>
          </button>
        </div>
        <p class="interact-card-note">
          主线结果由规则系统决定；同伴会记住你的关键选择。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { compactPlayerText, uwCanonText } from '../utils/uwCanonText.js'

const props = defineProps({
  nearbyInteract: { type: Object, default: null },
  visibleInteractActions: { type: Array, default: () => [] },
  busy: { type: Boolean, default: false },
  modelValue: { type: Boolean, default: false }
})

const REGION_LABELS = {
  work: '训练区域',
  rest: '休息区域',
  interact: '互动区域',
  locked: '边界区域',
  forbidden: '不可进入'
}

const displayInteractTitle = computed(() => uwCanonText(props.nearbyInteract?.title || '附近互动'))
const displayInteractBody = computed(() => compactPlayerText(props.nearbyInteract?.body || '', 140))

function playerFacingMeta(action) {
  if (action?.type === 'npc_intent_response') return '回应会改变关系与后续态度'
  if (action?.source === 'npc_intent') return '同伴主动提出'
  if (action?.type === 'story_event') return '关键线索 · 推进主线'
  if (action?.type === 'scene_activity') return action?.blockedReason || action?.meta || '消耗时间 · 获得进展'
  return action?.blockedReason || action?.meta || ''
}

const displayVisibleInteractActions = computed(() =>
  (Array.isArray(props.visibleInteractActions) ? props.visibleInteractActions : []).map((action) => ({
    ...action,
    label: compactPlayerText(action.label, 44),
    meta: compactPlayerText(playerFacingMeta(action), 56),
    description: compactPlayerText(action.description, 92)
  }))
)

function actionOutcome(action) {
  if (action?.blockedReason) return `暂不可用：${uwCanonText(action.blockedReason)}`
  if (action?.type === 'npc_intent_response') return '结果预览：关系 / 记忆'
  if (action?.source === 'npc_intent') return '结果预览：同伴事件 / 关系'
  if (action?.type === 'story_event') return '结果预览：剧情推进 / 新线索'
  if (action?.activity?.interaction_kind === 'boundary_patrol') return '结果预览：生命 / 体力 / 标记奖励'
  if (action?.type === 'scene_activity') return '结果预览：时间推进 / 活动收益'
  return '结果预览：世界状态变化'
}

const regionLabel = computed(() => {
  const poi = props.nearbyInteract
  const type = poi?.regionType
  if (!type && !poi?.zoneEntry) return ''
  return REGION_LABELS[type] || poi?.zoneLabel || '可互动区域'
})

function actionKicker(action) {
  if (action?.type === 'npc_intent_response') return 'NPC 回应'
  if (action?.source === 'npc_intent') return 'NPC 主动'
  if (action?.type === 'story_event') return '章节线索'
  if (action?.activity?.interaction_kind === 'reading_keywords') return '轻量玩法 · 读书'
  if (action?.activity?.interaction_kind === 'meal_choice') return '关系选择'
  if (action?.activity?.interaction_kind === 'boundary_patrol') return '短程探索 · 战术巡查'
  if (action?.type === 'scene_activity') return '场景活动'
  if (action?.type === 'daily_tick') return '日常推进'
  return '确认互动'
}

const emit = defineEmits(['update:modelValue', 'interact-action'])
</script>

<style scoped>
.field-interact-root {
  width: 100%;
}

.interact-backdrop {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(4, 8, 18, 0.78);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  animation: modal-backdrop-in 0.18s ease-out both;
}

.interact-card {
  width: 100%;
  max-width: 760px;
  max-height: min(88vh, 680px);
  overflow: auto;
  padding: 1.35rem 1.45rem;
  border-radius: 16px;
  background: linear-gradient(165deg, rgba(30, 41, 59, 0.95), rgba(7, 10, 18, 0.98));
  border: 1px solid var(--sao-border);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55), 0 0 24px rgba(94, 207, 255, 0.08);
  animation: modal-rise-in 0.22s ease-out both;
}

@keyframes modal-backdrop-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modal-rise-in {
  from {
    opacity: 0;
    transform: translateY(16px) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.interact-card-hd {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.interact-card-title {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 600;
  color: #f8fafc;
}

.interact-region {
  display: inline-flex;
  margin-bottom: 0.22rem;
  padding: 0.14rem 0.38rem;
  border-radius: 999px;
  border: 1px solid rgba(246, 211, 110, 0.28);
  background: rgba(246, 211, 110, 0.08);
  color: #fde68a;
  font-size: 0.72rem;
  font-weight: 800;
}

.interact-close {
  flex-shrink: 0;
  width: 2.4rem;
  height: 2.4rem;
  border: none;
  border-radius: 8px;
  background: rgba(51, 65, 85, 0.6);
  color: #e2e8f0;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}

.interact-close:hover {
  background: rgba(71, 85, 105, 0.75);
}

.interact-card-body {
  margin: 0 0 1rem;
  font-size: 1rem;
  line-height: 1.7;
  color: #cbd5e1;
}

.interact-actions {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  margin-bottom: 0.85rem;
}

.interact-actions .interact-action {
  width: 100%;
}

.interact-card-note {
  margin: 0;
  font-size: 0.82rem;
  line-height: 1.55;
  color: #64748b;
}

.interact-action {
  font-size: 0.95rem;
  padding: 0.78rem 0.9rem;
  border-radius: 11px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: linear-gradient(180deg, rgba(185, 88, 58, 0.88), rgba(110, 46, 44, 0.92));
  color: #e2e8f0;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.18rem;
  text-align: left;
}

.interact-action:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.55);
  background: linear-gradient(180deg, rgba(210, 104, 68, 0.96), rgba(126, 55, 48, 0.96));
  box-shadow: 0 0 16px rgba(246, 211, 110, 0.14);
}

.interact-action:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.interact-action.blocked {
  background: rgba(31, 41, 55, 0.72);
  border-color: rgba(148, 163, 184, 0.16);
}

.action-label {
  color: #fff7d6;
  font-weight: 800;
  line-height: 1.35;
}

.action-kicker {
  color: #bae6fd;
  font-size: 0.7rem;
  font-weight: 800;
  line-height: 1;
}

.action-meta {
  color: #bae6fd;
  font-size: 0.8rem;
  line-height: 1.35;
}

.action-desc {
  color: #cbd5e1;
  font-size: 0.82rem;
  line-height: 1.45;
}
.action-outcome {
  margin-top: 0.28rem;
  padding-top: 0.38rem;
  border-top: 1px solid rgba(186, 230, 253, 0.12);
  color: #d9f99d;
  font-size: 0.72rem;
  font-weight: 800;
  line-height: 1.35;
}

.interact-action.recommended {
  background: linear-gradient(180deg, rgba(190, 128, 42, 0.96), rgba(105, 60, 25, 0.98));
  border-color: rgba(253, 224, 71, 0.64);
  box-shadow: 0 0 22px rgba(246, 211, 110, 0.12);
}
.interact-action.relationship {
  background: linear-gradient(180deg, rgba(126, 66, 105, 0.94), rgba(69, 38, 73, 0.98));
  border-color: rgba(244, 114, 182, 0.38);
}
.interact-action.challenge {
  background: linear-gradient(180deg, rgba(39, 98, 126, 0.94), rgba(24, 54, 78, 0.98));
  border-color: rgba(56, 189, 248, 0.4);
}
.action-kicker { width: 100%; display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.action-kicker b {
  padding: 0.14rem 0.38rem;
  border-radius: 999px;
  color: #2e2113;
  background: #fde68a;
  font-size: 0.62rem;
  letter-spacing: 0;
}

</style>

