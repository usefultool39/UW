/** 与 SceneDisplay 中 currentScene 逻辑一致，供章节/台词复用 */
export function sceneFromAgents(agents) {
  if (!Array.isArray(agents)) return 'tree'
  const hasTable = agents.some((a) => a.location === 'table')
  const hasHome = agents.some((a) => a.location === 'home')
  const hasTree = agents.some((a) => a.location === 'at_tree' || a.location === 'bench')
  if (hasTable) return 'table'
  if (hasHome && !hasTree) return 'home'
  return 'tree'
}
