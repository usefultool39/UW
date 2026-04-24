import characters from '@characters/meta.json'

/** Shared agent display metadata (paths under frontend/public). */
export const AGENT_IDS = characters.agents.map((agent) => agent.id)

/**
 * `img` 使用原先的立绘路径（你把 .avif / .png 放回 public 后即会显示）。
 * 若文件不存在，各组件通过 onAgentImgError 回退到 `imgFallback`（内置 SVG 占位）。
 */
export const AGENT_META = Object.fromEntries(
  characters.agents.map((agent) => [agent.id, agent])
)

export function getAgentMeta(id) {
  return (
    AGENT_META[id] || {
      display: id,
      color: '#fff',
      img: '',
      imgFallback: '',
      role: ''
    }
  )
}

/** 挂到 <img @error="onAgentImgError($event, getAgentMeta(id))">，避免裂图。 */
export function onAgentImgError(event, meta) {
  const el = event?.target
  if (!el || !meta?.imgFallback || el.dataset.usedFallback === '1') return
  el.dataset.usedFallback = '1'
  el.src = meta.imgFallback
}
