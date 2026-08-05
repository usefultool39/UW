import { activityIdForAction } from './activityRegistry.js'

/**
 * Keep the NPC-authored wrapper when it points at the same activity as a POI
 * action. This removes duplicate first-player entries without changing the
 * backend activity or intent contract.
 */
export function dedupeActivityActions(actions) {
  const rows = Array.isArray(actions) ? actions : []
  const npcActivityIds = new Set(
    rows
      .filter((action) => action?.type === 'scene_activity' && action?.source === 'npc_intent')
      .map(activityIdForAction)
      .filter(Boolean)
  )
  if (!npcActivityIds.size) return rows

  return rows.filter((action) => {
    if (action?.type !== 'scene_activity' || action?.source === 'npc_intent') return true
    return !npcActivityIds.has(activityIdForAction(action))
  })
}
