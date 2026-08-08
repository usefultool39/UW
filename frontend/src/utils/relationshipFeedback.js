const RELATIONSHIP_FIELDS = Object.freeze({
  affinity: '好感',
  trust: '信任',
  tension: '紧张'
})

const FIELD_KEYS = new Set(Object.keys(RELATIONSHIP_FIELDS))

export function relationshipFieldLabel(field) {
  return RELATIONSHIP_FIELDS[field] || field || '关系'
}

export function relationshipPercent(value, field = 'affinity') {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return 0
  if (field === 'tension') return clamp(numeric, 0, 100)
  return clamp((numeric + 100) / 2, 0, 100)
}

export function clamp(value, min = 0, max = 100) {
  return Math.min(max, Math.max(min, Number(value) || 0))
}

/**
 * Normalize the relationship payloads used by story choices, activities and NPC intents.
 * The backend currently returns an array of { npc_id, field, before, after, delta },
 * but this also tolerates nested/aliased shapes so the UI remains useful during migrations.
 */
export function normalizeRelationshipChanges(raw) {
  const entries = collectEntries(raw)
  return entries
    .map((entry) => normalizeEntry(entry))
    .filter(Boolean)
}

function collectEntries(raw, hintedNpcId = '') {
  if (!raw) return []
  if (Array.isArray(raw)) return raw.flatMap((entry) => collectEntries(entry, hintedNpcId))
  if (typeof raw !== 'object') return []

  for (const key of ['relationship_changes', 'changes', 'relationships']) {
    if (raw[key]) return collectEntries(raw[key], hintedNpcId)
  }

  const directField = raw.field || raw.dimension || raw.stat || raw.metric
  const directNpc = raw.npc_id || raw.agent_id || raw.character_id || raw.npc || hintedNpcId
  if (directField || raw.delta !== undefined || raw.change !== undefined || raw.amount !== undefined) {
    return [{ ...raw, npc_id: directNpc }]
  }

  return Object.entries(raw).flatMap(([npcId, value]) => {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      const nestedFields = Object.entries(value)
        .filter(([field]) => FIELD_KEYS.has(field))
        .map(([field, delta]) => ({ npc_id: npcId, field, delta }))
      if (nestedFields.length) return nestedFields
      return collectEntries(value, npcId)
    }
    return []
  })
}

function normalizeEntry(entry) {
  if (!entry || typeof entry !== 'object') return null
  const npcId = String(entry.npc_id || entry.agent_id || entry.character_id || entry.npc || '').trim()
  const field = String(entry.field || entry.dimension || entry.stat || entry.metric || '').trim()
  if (!npcId || !FIELD_KEYS.has(field)) return null

  const before = numberOrNull(entry.before ?? entry.previous ?? entry.from)
  const after = numberOrNull(entry.after ?? entry.current ?? entry.to)
  const explicitDelta = numberOrNull(entry.delta ?? entry.change ?? entry.amount)
  const delta = explicitDelta ?? (before !== null && after !== null ? after - before : null)
  if (delta === null || delta === 0) return null

  return {
    npc_id: npcId,
    field,
    before,
    after,
    delta
  }
}

function numberOrNull(value) {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : null
}
