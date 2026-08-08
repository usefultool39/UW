<template>
  <div
    class="inventory-shell"
    :class="{ 'field-shell': fieldMode, 'overview-shell': !fieldMode }"
  >
    <button
      v-if="fieldMode"
      type="button"
      class="inventory-trigger"
      :aria-expanded="panelOpen"
      aria-controls="uw-inventory-panel"
      @click="panelOpen = !panelOpen"
    >
      <span class="trigger-icon" aria-hidden="true">◇</span>
      <span>物品栏</span>
      <span class="trigger-count">{{ totalCount }}</span>
    </button>

    <section
      v-if="!fieldMode || panelOpen"
      id="uw-inventory-panel"
      class="inventory-panel card"
      :class="{ 'field-drawer': fieldMode }"
      aria-labelledby="inventory-title"
    >
      <header class="inventory-header">
        <div>
          <p class="inventory-kicker">道具记录</p>
          <h2 id="inventory-title">物品栏</h2>
        </div>
        <div class="inventory-summary">
          <strong>{{ totalCount }}</strong>
          <span>件 · {{ itemCount }} 种</span>
        </div>
        <button
          v-if="fieldMode"
          type="button"
          class="inventory-close"
          aria-label="关闭物品栏"
          @click="panelOpen = false"
        >
          ×
        </button>
      </header>

      <p class="inventory-intro">收集到的材料、消耗品和关键道具都会在这里留下记录。</p>

      <nav class="category-tabs" aria-label="物品分类" role="tablist">
        <button
          v-for="category in categories"
          :key="category.id"
          type="button"
          role="tab"
          :aria-selected="activeCategory === category.id"
          :class="{ active: activeCategory === category.id }"
          @click="activeCategory = category.id"
        >
          <span>{{ category.label }}</span>
          <small>{{ category.count }}</small>
        </button>
      </nav>

      <div class="inventory-grid" aria-live="polite">
        <article
          v-for="(slot, index) in slots"
          :key="slot ? slot.id : `empty-${index}`"
          class="inventory-slot"
          :class="{ empty: !slot, occupied: Boolean(slot), usable: slot?.usable }"
        >
          <template v-if="slot">
            <div class="slot-topline">
              <span class="slot-icon" :class="`category-${slot.category}`" aria-hidden="true">{{ slot.icon }}</span>
              <span class="slot-count">×{{ slot.quantity }}</span>
            </div>
            <h3>{{ slot.name }}</h3>
            <p class="slot-category">{{ categoryLabel(slot.category) }}</p>
            <p class="slot-description">{{ slot.description }}</p>
            <button
              v-if="slot.usable"
              type="button"
              class="use-button"
              :disabled="busyItemId === slot.id"
              @click="useItem(slot)"
            >
              {{ busyItemId === slot.id ? '使用中…' : '使用' }}
            </button>
            <span v-else class="slot-note">{{ slot.category === 'key' ? '关键道具' : '暂不可使用' }}</span>
          </template>
          <span v-else class="empty-slot" aria-label="空槽位">空槽</span>
        </article>
      </div>

      <p v-if="overflowCount > 0" class="inventory-overflow">还有 {{ overflowCount }} 件物品未显示，请切换分类查看。</p>
      <p v-else-if="!filteredItems.length" class="inventory-empty-copy">这一类还没有记录，探索村庄后再回来看看。</p>

      <p
        v-if="feedback.text"
        class="inventory-feedback"
        :class="`feedback-${feedback.tone}`"
        role="status"
        aria-live="polite"
      >
        {{ feedback.text }}
      </p>
    </section>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const SLOT_COUNT = 8

const ITEM_CATALOG = Object.freeze({
  field_mint: {
    name: '野薄荷',
    description: '带着清凉气味的野生药草，可作为调配材料。',
    category: 'material',
    icon: '✦'
  },
  dewgrass: {
    name: '露草',
    description: '清晨叶尖凝着露水的草药，适合保存。',
    category: 'material',
    icon: '❋'
  },
  silverleaf: {
    name: '银叶草',
    description: '叶面泛着银光的草药，常被村民晒干备用。',
    category: 'material',
    icon: '❈'
  },
  rain_bell: {
    name: '雨铃花',
    description: '细雨后才会开放的花，花茎会发出轻响。',
    category: 'material',
    icon: '✿'
  },
  moon_blossom: {
    name: '月见花',
    description: '夜色里微微发亮的花，边境记录中偶有提及。',
    category: 'material',
    icon: '☾'
  },
  south_lake_common_fish: {
    name: '湖鳞鱼',
    description: '南湖旧渡靠岸浅水里的普通鱼，适合做成家常料理。',
    category: 'material',
    icon: '◒'
  },
  south_lake_rare_fish: {
    name: '雾银鱼',
    description: '只在雾中短暂咬钩的稀有鱼，鳞片像被月光擦亮。',
    category: 'material',
    icon: '◓'
  },
  stone_tablet_fragment: {
    name: '石碑碎片',
    description: '刻着古老纹路的碎石，三块似乎能够拼合。',
    category: 'key',
    icon: '◈'
  },
  record_notebook: {
    name: '记录本',
    description: '桐人用来整理村中见闻的记录本。',
    category: 'key',
    icon: '▤',
    usable: true
  },
  dried_rations: {
    name: '干粮',
    description: '适合巡查途中补充体力的简单干粮。',
    category: 'consumable',
    icon: '▰',
    usable: true
  },
  herb_soup: {
    name: '草药汤',
    description: '用田野草药熬成的温热汤剂，能恢复神圣力。',
    category: 'consumable',
    icon: '∿',
    usable: true
  },
  healing_potion: {
    name: '回复药水',
    description: '饮用后恢复少量生命值。',
    category: 'consumable',
    icon: '●',
    usable: true
  },
  small_healing_potion: {
    name: '小回复药',
    description: '便于随身携带的基础回复药。',
    category: 'consumable',
    icon: '●',
    usable: true
  },
  stamina_potion: {
    name: '体力药',
    description: '短时间内补回一部分行动体力。',
    category: 'consumable',
    icon: '▲',
    usable: true
  },
  mp_potion: {
    name: '神圣力药',
    description: '恢复少量神圣力，适合在探索间隙使用。',
    category: 'consumable',
    icon: '✧',
    usable: true
  },
  bread: {
    name: '面包',
    description: '朴素但扎实的食物，能够恢复一点体力。',
    category: 'consumable',
    icon: '▰',
    usable: true
  },
  water: {
    name: '清水',
    description: '旅途中不可缺少的饮水。',
    category: 'consumable',
    icon: '≈',
    usable: true
  }
})

const CATEGORY_META = Object.freeze([
  { id: 'all', label: '全部' },
  { id: 'material', label: '材料' },
  { id: 'consumable', label: '消耗品' },
  { id: 'key', label: '关键道具' }
])

const props = defineProps({
  simState: {
    type: Object,
    default: () => ({})
  },
  playerAction: {
    type: Function,
    required: true
  },
  fieldMode: {
    type: Boolean,
    default: false
  }
})

const activeCategory = ref('all')
const panelOpen = ref(false)
const busyItemId = ref('')
const feedback = ref({ tone: '', text: '' })

const rawInventory = computed(() => {
  const inventory = props.simState?.inventory
  return inventory && typeof inventory === 'object' && !Array.isArray(inventory) ? inventory : {}
})

function inferCategory(itemId) {
  const normalized = String(itemId || '').toLowerCase()
  if (/(potion|elixir|medicine|antidote|bread|water|food|meal|tea|drink)/.test(normalized)) return 'consumable'
  if (/(fragment|tablet|key|relic|letter|seal|memory)/.test(normalized)) return 'key'
  return 'material'
}

function fallbackName(itemId) {
  return String(itemId || '')
    .split(/[_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ') || '未知物品'
}

const inventoryItems = computed(() => Object.entries(rawInventory.value)
  .map(([id, value]) => {
    const quantity = Math.max(0, Math.floor(Number(value) || 0))
    const catalog = ITEM_CATALOG[id] || {}
    const category = catalog.category || inferCategory(id)
    return {
      id,
      quantity,
      category,
      name: catalog.name || fallbackName(id),
      description: catalog.description || '尚未记录详细说明，但它可能在之后的旅途中派上用场。',
      icon: catalog.icon || (category === 'key' ? '◈' : category === 'consumable' ? '●' : '✦'),
      usable: Boolean(catalog.usable)
    }
  })
  .filter((item) => item.quantity > 0)
  .sort((a, b) => a.name.localeCompare(b.name, 'zh-CN')))

const totalCount = computed(() => inventoryItems.value.reduce((sum, item) => sum + item.quantity, 0))
const itemCount = computed(() => inventoryItems.value.length)

const categories = computed(() => CATEGORY_META.map((category) => ({
  ...category,
  count: category.id === 'all'
    ? itemCount.value
    : inventoryItems.value.filter((item) => item.category === category.id).length
})))

const filteredItems = computed(() => activeCategory.value === 'all'
  ? inventoryItems.value
  : inventoryItems.value.filter((item) => item.category === activeCategory.value))

const slots = computed(() => [
  ...filteredItems.value.slice(0, SLOT_COUNT),
  ...Array.from({ length: Math.max(0, SLOT_COUNT - filteredItems.value.length) }, () => null)
])

const overflowCount = computed(() => Math.max(0, filteredItems.value.length - SLOT_COUNT))

function categoryLabel(categoryId) {
  return CATEGORY_META.find((category) => category.id === categoryId)?.label || '材料'
}

function actionFeedback(response, item) {
  const candidates = [
    response?.result_text,
    response?.message,
    response?.feedback,
    response?.result?.result_text,
    response?.result?.message,
    response?.result?.text,
    response?.item_result?.result_text
  ]
  const text = candidates.find((value) => typeof value === 'string' && value.trim())
  if (text) return text

  const change = response?.item_changes?.[item.id]
  if (change && Number.isFinite(Number(change.after))) {
    return `${item.name} 已使用，剩余 ${Math.max(0, Number(change.after))} 件。`
  }
  return `使用了 ${item.name}。`
}

async function useItem(item) {
  if (!item?.usable || busyItemId.value) return
  busyItemId.value = item.id
  feedback.value = { tone: '', text: '' }
  try {
    const response = await props.playerAction({
      kind: 'use_item',
      item_id: item.id,
      quantity: 1
    })
    feedback.value = { tone: 'success', text: actionFeedback(response, item) }
  } catch (error) {
    feedback.value = {
      tone: 'error',
      text: error?.message || `暂时无法使用${item.name}。`
    }
  } finally {
    busyItemId.value = ''
  }
}
</script>

<style scoped>
.inventory-shell {
  min-width: 0;
}

.field-shell {
  position: fixed;
  top: 4.35rem;
  right: 0.8rem;
  z-index: 140;
  pointer-events: none;
}

.field-shell > * {
  pointer-events: auto;
}

.inventory-trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.34rem;
  min-height: 2.25rem;
  padding: 0.42rem 0.64rem;
  border-radius: 9px;
  color: #fff7d6;
  border-color: rgba(246, 211, 110, 0.52);
  background: rgba(9, 16, 29, 0.84);
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.28), 0 0 16px rgba(246, 211, 110, 0.08);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  font-size: 0.78rem;
  font-weight: 800;
}

.inventory-trigger:hover,
.inventory-trigger[aria-expanded='true'] {
  border-color: rgba(253, 224, 71, 0.88);
  box-shadow: 0 0 18px rgba(253, 224, 71, 0.18);
}

.trigger-icon {
  color: var(--sao-gold, #f6d36e);
  font-size: 1.05rem;
  line-height: 1;
}

.trigger-count {
  min-width: 1.15rem;
  padding: 0.08rem 0.22rem;
  border-radius: 999px;
  color: #172033;
  background: #f6d36e;
  font-size: 0.7rem;
  text-align: center;
}

.inventory-panel {
  width: 100%;
  padding: 0.85rem;
  color: var(--ink);
}

.field-drawer {
  position: fixed;
  right: 0.8rem;
  bottom: max(0.75rem, env(safe-area-inset-bottom));
  width: min(410px, calc(100vw - 1.6rem));
  max-height: min(64dvh, 560px);
  overflow-y: auto;
  overscroll-behavior: contain;
  border-radius: 14px;
  border-color: rgba(125, 211, 252, 0.42);
  background: rgba(6, 12, 24, 0.96);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.46), 0 0 24px rgba(94, 207, 255, 0.12);
}

.inventory-header {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  min-width: 0;
}

.inventory-kicker {
  margin: 0 0 0.08rem;
  color: var(--sao-gold, #f6d36e);
  font-size: 0.64rem;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.inventory-header h2 {
  margin: 0;
  color: #fff7d6;
  font-size: 1rem;
  line-height: 1.25;
}

.inventory-summary {
  margin-left: auto;
  padding-top: 0.12rem;
  color: var(--muted);
  font-size: 0.68rem;
  text-align: right;
  white-space: nowrap;
}

.inventory-summary strong {
  color: #fff7d6;
  font-size: 0.98rem;
}

.inventory-close {
  flex: 0 0 auto;
  min-width: 1.9rem;
  min-height: 1.9rem;
  padding: 0;
  border-radius: 7px;
  font-size: 1.15rem;
  line-height: 1;
}

.inventory-intro {
  margin: 0.55rem 0 0.72rem;
  color: var(--muted);
  font-size: 0.72rem;
  line-height: 1.45;
}

.category-tabs {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.3rem;
  margin-bottom: 0.65rem;
}

.category-tabs button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.18rem;
  min-width: 0;
  padding: 0.38rem 0.24rem;
  border-color: rgba(125, 211, 252, 0.2);
  background: rgba(22, 36, 58, 0.48);
  color: var(--muted);
  font-size: 0.67rem;
  white-space: nowrap;
}

.category-tabs button small {
  color: var(--sao-gold, #f6d36e);
  font-size: 0.62rem;
}

.category-tabs button.active {
  color: #fff7d6;
  border-color: rgba(246, 211, 110, 0.68);
  background: rgba(120, 83, 35, 0.32);
  box-shadow: 0 0 12px rgba(246, 211, 110, 0.1);
}

.inventory-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.42rem;
}

.inventory-slot {
  position: relative;
  display: flex;
  min-width: 0;
  min-height: 7.6rem;
  flex-direction: column;
  padding: 0.45rem;
  border: 1px solid rgba(125, 211, 252, 0.14);
  border-radius: 8px;
  background: linear-gradient(180deg, rgba(22, 36, 58, 0.7), rgba(8, 14, 25, 0.76));
  overflow: hidden;
}

.inventory-slot.occupied {
  border-color: rgba(125, 211, 252, 0.3);
}

.inventory-slot.usable {
  border-color: rgba(246, 211, 110, 0.42);
}

.inventory-slot.empty {
  align-items: center;
  justify-content: center;
  min-height: 7.6rem;
  border-style: dashed;
  background: rgba(9, 15, 26, 0.35);
}

.empty-slot {
  color: rgba(166, 184, 207, 0.48);
  font-size: 0.67rem;
}

.slot-topline {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.25rem;
}

.slot-icon {
  display: grid;
  width: 1.65rem;
  height: 1.65rem;
  place-items: center;
  border-radius: 7px;
  color: #7dd3fc;
  background: rgba(94, 207, 255, 0.1);
  border: 1px solid rgba(125, 211, 252, 0.3);
  font-size: 1.05rem;
  line-height: 1;
}

.slot-icon.category-consumable {
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
  border-color: rgba(251, 191, 36, 0.34);
}

.slot-icon.category-key {
  color: #c4b5fd;
  background: rgba(196, 181, 253, 0.1);
  border-color: rgba(196, 181, 253, 0.36);
}

.slot-count {
  color: #fff7d6;
  font-size: 0.7rem;
  font-weight: 800;
}

.inventory-slot h3 {
  margin: 0.32rem 0 0;
  color: #f8fafc;
  font-size: 0.72rem;
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.slot-category {
  margin: 0.1rem 0 0;
  color: var(--sao-gold, #f6d36e);
  font-size: 0.58rem;
}

.slot-description {
  display: -webkit-box;
  flex: 1;
  margin: 0.28rem 0 0.35rem;
  color: var(--muted);
  font-size: 0.62rem;
  line-height: 1.35;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.use-button {
  width: 100%;
  min-height: 1.75rem;
  margin-top: auto;
  padding: 0.25rem 0.35rem;
  border-color: rgba(246, 211, 110, 0.62);
  color: #fff7d6;
  background: rgba(120, 83, 35, 0.42);
  font-size: 0.68rem;
}

.use-button:hover:not(:disabled) {
  border-color: rgba(253, 224, 71, 0.94);
  background: rgba(120, 83, 35, 0.68);
  box-shadow: 0 0 12px rgba(253, 224, 71, 0.16);
}

.use-button:disabled {
  cursor: wait;
  opacity: 0.58;
}

.slot-note {
  display: block;
  margin-top: auto;
  padding-top: 0.25rem;
  color: rgba(166, 184, 207, 0.68);
  font-size: 0.58rem;
}

.inventory-overflow,
.inventory-empty-copy {
  margin: 0.58rem 0 0;
  color: var(--muted);
  font-size: 0.66rem;
  line-height: 1.4;
}

.inventory-feedback {
  margin: 0.68rem 0 0;
  padding: 0.48rem 0.58rem;
  border-radius: 7px;
  font-size: 0.7rem;
  line-height: 1.4;
}

.feedback-success {
  color: #dcfce7;
  border: 1px solid rgba(74, 222, 128, 0.35);
  background: rgba(22, 101, 52, 0.22);
}

.feedback-error {
  color: #fee2e2;
  border: 1px solid rgba(248, 113, 113, 0.42);
  background: rgba(127, 29, 29, 0.25);
}

@media (max-width: 640px) {
  .field-shell {
    top: 3.9rem;
    right: 0.55rem;
  }

  .field-drawer {
    right: 0;
    bottom: 0;
    width: 100%;
    max-height: min(56dvh, 520px);
    padding: 0.82rem 0.72rem max(0.82rem, env(safe-area-inset-bottom));
    border-radius: 18px 18px 0 0;
  }

  .inventory-slot {
    min-height: 7.1rem;
    padding: 0.4rem;
  }

  .inventory-slot.empty {
    min-height: 7.1rem;
  }

  .slot-description {
    -webkit-line-clamp: 2;
  }
}

@media (prefers-reduced-motion: reduce) {
  .inventory-trigger,
  .category-tabs button,
  .use-button {
    transition: none;
  }
}
</style>
