<template>
  <div
    v-show="modelValue"
    class="cooking-backdrop"
    role="dialog"
    aria-modal="true"
    @click.self="close"
  >
    <section class="cooking-panel" @click.stop>
      <header class="cooking-header">
        <div>
          <p class="cooking-kicker">家中炉火 · 双阶段烹饪</p>
          <h3>{{ activity?.title || '炉火边备餐' }}</h3>
        </div>
        <button type="button" class="cooking-close" aria-label="关闭" :disabled="busy || phase === 'cutting'" @click="close">×</button>
      </header>

      <p class="cooking-desc">
        先在刀声里跟上节奏，再用滑杆收住火候。两阶段都完美，成品数量会翻倍。
      </p>

      <section v-if="phase === 'empty'" class="cooking-empty" data-testid="cooking-empty-state">
        <div class="empty-icon">炉</div>
        <strong>现在没有可用材料</strong>
        <p>需要 1 份野薄荷、湖鳞鱼或雾银鱼。请先去西侧田野采药，或在南湖旧渡钓鱼；本次不会消耗任何库存。</p>
        <button type="button" class="cooking-ghost" :disabled="busy" @click="close">先去找材料</button>
      </section>

      <template v-else>
        <section v-if="phase === 'recipe'" class="recipe-stage">
          <div class="stage-heading">
            <span class="stage-number">01</span>
            <div>
              <strong>选择材料</strong>
              <small>优先使用你已经带回家的材料</small>
            </div>
          </div>

          <div class="recipe-options">
            <button
              v-for="recipe in availableRecipes"
              :key="recipe.id"
              type="button"
              class="recipe-card"
              :class="{ selected: selectedRecipe?.id === recipe.id }"
              :disabled="busy"
              @click="selectedRecipeId = recipe.id"
            >
              <span class="recipe-emoji">{{ recipe.emoji }}</span>
              <span class="recipe-copy">
                <strong>{{ recipe.label }}</strong>
                <small>{{ recipe.hint }}</small>
              </span>
              <span class="recipe-count">×{{ inventory[recipe.ingredientId] || 0 }}</span>
            </button>
          </div>

          <p v-if="selectedRecipe" class="recipe-preview">
            {{ selectedRecipe.ingredientName }} → {{ selectedRecipe.outputName }} · 普通 1 份 / 完美 2 份
          </p>

          <footer class="cooking-actions">
            <button type="button" class="cooking-ghost" :disabled="busy" @click="close">稍后再做</button>
            <button type="button" class="cooking-primary" :disabled="busy || !selectedRecipe" @click="startCutting">
              开始切菜
            </button>
          </footer>
        </section>

        <section v-else-if="phase === 'cutting'" class="cutting-stage">
          <div class="stage-heading">
            <span class="stage-number">02</span>
            <div>
              <strong>切菜节奏</strong>
              <small>在亮环靠近中心时按下，5 刀后进入火候</small>
            </div>
          </div>

          <div class="cutting-meter" :class="{ pulse: beatProgress > 72 }">
            <div class="cutting-ring" :style="{ '--beat-progress': `${beatProgress}%` }">
              <span>{{ cuttingBeat }}/5</span>
              <small>{{ cuttingStatus }}</small>
            </div>
          </div>
          <div class="meter-track" aria-label="切菜节拍进度">
            <span :style="{ width: `${beatProgress}%` }"></span>
          </div>
          <p class="cutting-hint">命中 {{ cuttingHits }} · 偏离 {{ cuttingMisses }} · 不必连点，听清下一声刀响。</p>

          <footer class="cooking-actions">
            <button type="button" class="cooking-primary chop-button" :disabled="busy" @click="tapCut">
              切下这一刀
            </button>
          </footer>
        </section>

        <section v-else-if="phase === 'heat'" class="heat-stage">
          <div class="stage-heading">
            <span class="stage-number">03</span>
            <div>
              <strong>火候力度</strong>
              <small>把火收在 68–82 之间，才算完美</small>
            </div>
          </div>

          <div class="heat-gauge">
            <div class="heat-scale"><span>小火</span><span>合适火候</span><span>猛火</span></div>
            <div class="heat-bar">
              <span class="heat-perfect-band"></span>
              <span class="heat-marker" :style="{ left: `${heatPower}%` }"></span>
            </div>
            <output>{{ heatPower }}%</output>
          </div>
          <input v-model.number="heatPower" class="heat-slider" type="range" min="0" max="100" step="1" aria-label="火候力度" />
          <p class="heat-hint">切菜命中 {{ cuttingHits }}/5。{{ heatPower >= 68 && heatPower <= 82 ? '火候正在合适的窄窗里。' : '先把火候调到合适的窄窗。' }}</p>

          <footer class="cooking-actions">
            <button type="button" class="cooking-ghost" :disabled="busy" @click="phase = 'recipe'">换一种材料</button>
            <button type="button" class="cooking-primary" :disabled="busy" @click="confirmHeat">确认火候</button>
          </footer>
        </section>

        <section v-else class="cooking-result" data-testid="cooking-result">
          <div class="result-badge" :class="pendingResult?.tier">{{ pendingResult?.label }}</div>
          <strong>{{ selectedRecipe?.outputName }}</strong>
          <p>{{ pendingResult?.text }}</p>
          <dl class="result-stats">
            <div><dt>切菜</dt><dd>{{ cuttingHits }}/5</dd></div>
            <div><dt>火候</dt><dd>{{ heatPower }}%</dd></div>
            <div><dt>产出</dt><dd>×{{ pendingResult?.quantity }}</dd></div>
          </dl>
          <footer class="cooking-actions">
            <button type="button" class="cooking-primary" :disabled="busy" @click="finish">装盘并结算</button>
          </footer>
        </section>
      </template>

      <p v-if="notice" class="cooking-note" role="status">{{ notice }}</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  activity: { type: Object, default: null },
  inventory: { type: Object, default: () => ({}) },
  busy: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'complete'])

const recipes = [
  {
    id: 'herb_soup',
    ingredientId: 'field_mint',
    ingredientName: '野薄荷',
    outputName: '草药汤',
    label: '草药汤',
    hint: '清凉草叶，熬成能恢复神圣力的热汤。',
    emoji: '🌿',
    normalChoiceId: 'cook_herb_soup_normal',
    perfectChoiceId: 'cook_herb_soup_perfect'
  },
  {
    id: 'dried_rations_common',
    ingredientId: 'south_lake_common_fish',
    ingredientName: '湖鳞鱼',
    outputName: '干粮',
    label: '湖鳞鱼干粮',
    hint: '把普通鱼做成适合巡查途中使用的干粮。',
    emoji: '🐟',
    normalChoiceId: 'cook_dried_rations_common_normal',
    perfectChoiceId: 'cook_dried_rations_common_perfect'
  },
  {
    id: 'dried_rations_rare',
    ingredientId: 'south_lake_rare_fish',
    ingredientName: '雾银鱼',
    outputName: '干粮',
    label: '雾银鱼干粮',
    hint: '不浪费稀有鱼的鲜味，做成更充足的干粮。',
    emoji: '✨',
    normalChoiceId: 'cook_dried_rations_rare_normal',
    perfectChoiceId: 'cook_dried_rations_rare_perfect'
  }
]

const phase = ref('recipe')
const selectedRecipeId = ref('')
const cuttingBeat = ref(0)
const cuttingHits = ref(0)
const cuttingMisses = ref(0)
const beatProgress = ref(0)
const heatPower = ref(50)
const pendingResult = ref(null)
const notice = ref('')

let cutTimer = null
let nextBeatAt = 0
const totalBeats = 5
const beatLengthMs = 720
const hitWindowMs = 230

const inventory = computed(() => props.inventory || {})
const authoredChoices = computed(() => Array.isArray(props.activity?.choices) ? props.activity.choices : [])
const availableRecipes = computed(() => recipes.filter((recipe) => Number(inventory.value[recipe.ingredientId] || 0) > 0))
const selectedRecipe = computed(() => recipes.find((recipe) => recipe.id === selectedRecipeId.value) || null)
const cuttingStatus = computed(() => {
  if (cuttingBeat.value >= totalBeats) return '完成'
  if (beatProgress.value > 72) return '按下'
  return '听刀声'
})

function authoredChoice(id, fallback) {
  return authoredChoices.value.find((choice) => choice?.id === id) || fallback
}

function clearCutTimer() {
  if (cutTimer) window.clearInterval(cutTimer)
  cutTimer = null
}

function reset() {
  clearCutTimer()
  phase.value = availableRecipes.value.length ? 'recipe' : 'empty'
  selectedRecipeId.value = availableRecipes.value[0]?.id || ''
  cuttingBeat.value = 0
  cuttingHits.value = 0
  cuttingMisses.value = 0
  beatProgress.value = 0
  heatPower.value = 50
  pendingResult.value = null
  notice.value = availableRecipes.value.length ? '' : '材料不足：本次烹饪被明确拒绝，库存保持不变。'
}

function close() {
  if (phase.value === 'cutting') return
  clearCutTimer()
  emit('update:modelValue', false)
}

function startCutting() {
  if (!selectedRecipe.value || props.busy) return
  phase.value = 'cutting'
  cuttingBeat.value = 0
  cuttingHits.value = 0
  cuttingMisses.value = 0
  beatProgress.value = 0
  notice.value = '下一声刀响会在亮环靠近中心时出现。'
  nextBeatAt = Date.now() + 620
  cutTimer = window.setInterval(tickCutting, 50)
}

function tickCutting() {
  const untilBeat = nextBeatAt - Date.now()
  beatProgress.value = Math.max(0, Math.min(100, 100 - (untilBeat / beatLengthMs) * 100))
  if (Date.now() > nextBeatAt + hitWindowMs) advanceCut(false)
}

function advanceCut(hit) {
  if (phase.value !== 'cutting') return
  if (hit) cuttingHits.value += 1
  else cuttingMisses.value += 1
  cuttingBeat.value += 1
  if (cuttingBeat.value >= totalBeats) {
    clearCutTimer()
    beatProgress.value = 100
    phase.value = 'heat'
    heatPower.value = 50
    notice.value = '切菜完成。现在把火候收进合适的窄窗。'
    return
  }
  nextBeatAt = Date.now() + beatLengthMs
  beatProgress.value = 0
}

function tapCut() {
  if (phase.value !== 'cutting' || props.busy) return
  const distance = Math.abs(Date.now() - nextBeatAt)
  advanceCut(distance <= hitWindowMs)
}

function confirmHeat() {
  if (!selectedRecipe.value || phase.value !== 'heat' || props.busy) return
  const perfect = cuttingHits.value === totalBeats && heatPower.value >= 68 && heatPower.value <= 82
  const tier = perfect ? 'perfect' : 'normal'
  const quantity = perfect ? 2 : 1
  const choiceId = perfect ? selectedRecipe.value.perfectChoiceId : selectedRecipe.value.normalChoiceId
  const authored = authoredChoice(choiceId, {})
  pendingResult.value = {
    tier,
    label: perfect ? '完美成品' : '普通成品',
    score: cuttingHits.value * 20 + (perfect ? 100 : Math.round(heatPower.value)),
    quantity,
    choiceId,
    recipeId: selectedRecipe.value.id,
    ingredientId: selectedRecipe.value.ingredientId,
    outputItemId: selectedRecipe.value.id === 'herb_soup' ? 'herb_soup' : 'dried_rations',
    cuttingHits: cuttingHits.value,
    heatPower: heatPower.value,
    text: authored.result_text || (perfect ? '刀声与火声在同一个节拍上停下。' : '成品略朴素，但足够支撑下一段路。')
  }
  phase.value = 'result'
}

function finish() {
  if (!pendingResult.value || props.busy) return
  emit('complete', {
    choice_id: pendingResult.value.choiceId,
    result: pendingResult.value
  })
}

watch(() => props.modelValue, (open) => {
  if (open) reset()
  else clearCutTimer()
})

watch(availableRecipes, (next) => {
  if (!props.modelValue || phase.value === 'cutting' || phase.value === 'heat' || phase.value === 'result') return
  if (!next.some((recipe) => recipe.id === selectedRecipeId.value)) selectedRecipeId.value = next[0]?.id || ''
  if (!next.length) {
    phase.value = 'empty'
    notice.value = '材料不足：本次烹饪被明确拒绝，库存保持不变。'
  }
})

onUnmounted(clearCutTimer)
</script>

<style scoped>
.cooking-backdrop {
  position: fixed;
  inset: 0;
  z-index: 90;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 1rem;
  background: rgba(18, 13, 10, 0.35);
}

.cooking-panel {
  width: min(680px, 100%);
  max-height: min(82dvh, 720px);
  overflow: auto;
  padding: 1rem 1.05rem calc(1rem + env(safe-area-inset-bottom));
  border: 1px solid rgba(255, 229, 171, 0.28);
  border-radius: 18px 18px 12px 12px;
  color: #fff6df;
  background: linear-gradient(145deg, rgba(52, 38, 29, 0.98), rgba(28, 44, 39, 0.98));
  box-shadow: 0 20px 60px rgba(15, 10, 7, 0.5), 0 0 30px rgba(239, 177, 81, 0.12);
}

.cooking-header, .cooking-actions, .stage-heading, .heat-scale, .result-stats {
  display: flex;
  align-items: center;
}

.cooking-header, .cooking-actions { justify-content: space-between; gap: 0.75rem; }
.cooking-kicker { margin: 0 0 0.2rem; color: #f4ca7a; font-size: 0.7rem; font-weight: 900; letter-spacing: 0.08em; }
.cooking-header h3 { margin: 0; font-size: 1.2rem; }
.cooking-close { border: 0; color: #ffe8bb; background: transparent; font-size: 1.8rem; line-height: 1; cursor: pointer; }
.cooking-desc, .cooking-note, .cutting-hint, .heat-hint, .recipe-preview { color: rgba(255, 244, 218, 0.74); font-size: 0.84rem; line-height: 1.55; }
.cooking-desc { margin: 0.85rem 0; }
.stage-heading { gap: 0.65rem; margin: 0.5rem 0 0.9rem; }
.stage-heading strong, .stage-heading small { display: block; }
.stage-heading small { margin-top: 0.18rem; color: rgba(255, 244, 218, 0.62); }
.stage-number { display: grid; width: 2.15rem; height: 2.15rem; place-items: center; border-radius: 50%; color: #342518; background: #f4ca7a; font-weight: 900; }
.recipe-options { display: grid; gap: 0.55rem; }
.recipe-card { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 0.7rem; min-height: 4rem; padding: 0.7rem; text-align: left; color: #fff6df; border: 1px solid rgba(255, 235, 190, 0.18); border-radius: 12px; background: rgba(255, 247, 225, 0.06); cursor: pointer; }
.recipe-card.selected { border-color: #f4ca7a; background: rgba(244, 202, 122, 0.14); }
.recipe-emoji { font-size: 1.5rem; }
.recipe-copy strong, .recipe-copy small { display: block; }
.recipe-copy small { margin-top: 0.2rem; color: rgba(255, 244, 218, 0.66); }
.recipe-count { color: #f4ca7a; font-weight: 900; }
.recipe-preview { margin: 0.75rem 0; }
.cooking-primary, .cooking-ghost { min-height: 2.8rem; padding: 0.65rem 1rem; border-radius: 10px; font-weight: 900; cursor: pointer; touch-action: manipulation; }
.cooking-primary { border: 1px solid #f4ca7a; color: #332417; background: #f4ca7a; }
.cooking-ghost { border: 1px solid rgba(255, 235, 190, 0.3); color: #ffe8bb; background: transparent; }
button:disabled { opacity: 0.5; cursor: not-allowed; }
.cutting-stage, .heat-stage, .cooking-result, .cooking-empty { min-height: 19rem; }
.cutting-meter { display: grid; place-items: center; height: 9.5rem; }
.cutting-ring { display: grid; place-items: center; width: 8.5rem; height: 8.5rem; border: 7px solid rgba(255, 236, 186, 0.18); border-top-color: #f4ca7a; border-right-color: rgba(244, 202, 122, 0.35); border-radius: 50%; transform: rotate(calc(var(--beat-progress) * 1deg)); transition: transform 0.1s linear, box-shadow 0.15s ease; }
.cutting-ring span, .cutting-ring small { transform: rotate(calc(var(--beat-progress) * -1deg)); }
.cutting-ring span { font-size: 1.6rem; font-weight: 900; }
.cutting-ring small { color: rgba(255, 244, 218, 0.7); }
.cutting-meter.pulse .cutting-ring { box-shadow: 0 0 28px rgba(244, 202, 122, 0.45); }
.meter-track, .heat-bar { position: relative; height: 0.45rem; overflow: hidden; border-radius: 99px; background: rgba(255, 255, 255, 0.12); }
.meter-track span { display: block; height: 100%; background: #f4ca7a; transition: width 0.1s linear; }
.cutting-hint { text-align: center; }
.chop-button { width: 100%; }
.heat-gauge { padding: 1rem 0 0.5rem; }
.heat-scale { justify-content: space-between; color: rgba(255, 244, 218, 0.66); font-size: 0.72rem; }
.heat-bar { margin: 0.55rem 0; height: 1.4rem; background: linear-gradient(90deg, #6c8b67 0 40%, #e2b65f 40% 90%, #b65d53 90%); }
.heat-perfect-band { position: absolute; left: 68%; width: 14%; height: 100%; background: rgba(255, 250, 207, 0.7); }
.heat-marker { position: absolute; top: -0.25rem; width: 0.25rem; height: 1.9rem; background: #fff8dd; box-shadow: 0 0 0 2px rgba(37, 25, 16, 0.45); transform: translateX(-50%); }
.heat-gauge output { display: block; text-align: center; color: #f4ca7a; font-size: 1.45rem; font-weight: 900; }
.heat-slider { width: 100%; accent-color: #f4ca7a; touch-action: manipulation; }
.cooking-result { display: grid; place-items: center; text-align: center; padding: 1rem 0; }
.result-badge { padding: 0.4rem 0.8rem; border-radius: 99px; font-weight: 900; }
.result-badge.perfect { color: #342518; background: #f4ca7a; }
.result-badge.normal { color: #fff2cd; background: rgba(255, 244, 218, 0.16); }
.cooking-result strong { margin-top: 0.7rem; font-size: 1.35rem; }
.cooking-result p { max-width: 34rem; color: rgba(255, 244, 218, 0.76); line-height: 1.55; }
.result-stats { justify-content: center; gap: 1rem; margin: 0.25rem 0 1rem; }
.result-stats div { min-width: 4.3rem; padding: 0.45rem; border-radius: 8px; background: rgba(255, 255, 255, 0.07); }
.result-stats dt { color: rgba(255, 244, 218, 0.58); font-size: 0.7rem; }
.result-stats dd { margin: 0.2rem 0 0; color: #f4ca7a; font-weight: 900; }
.cooking-empty { display: grid; place-items: center; text-align: center; padding: 1.2rem; }
.empty-icon { display: grid; width: 3.2rem; height: 3.2rem; place-items: center; margin-bottom: 0.55rem; border-radius: 50%; color: #342518; background: #f4ca7a; font-weight: 900; }
.cooking-empty p { max-width: 33rem; color: rgba(255, 244, 218, 0.72); line-height: 1.6; }
.cooking-note { margin: 0.8rem 0 0; text-align: center; }

@media (max-width: 560px) {
  .cooking-backdrop { padding: 0; }
  .cooking-panel { max-height: min(82dvh, 720px); border-radius: 18px 18px 0 0; padding-bottom: calc(0.9rem + env(safe-area-inset-bottom)); }
  .cooking-actions { align-items: stretch; }
  .cooking-actions button { flex: 1; }
  .recipe-card { min-height: 3.7rem; }
  .cutting-stage, .heat-stage, .cooking-result, .cooking-empty { min-height: 16rem; }
}
</style>
