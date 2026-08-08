/**
 * Player-facing Underworld terminology.
 *
 * Internal ids and old save/config strings intentionally remain unchanged so
 * existing saves and story gates stay compatible. Only rendered copy is
 * normalized here.
 */
const TERM_REPLACEMENTS = [
  ['露茵村', '卢利特村'],
  ['艾琳', '爱丽丝'],
  ['爱丽丝', '爱丽丝'],
  ['尤里', '尤吉欧'],
  ['悠吉欧', '尤吉欧'],
  ['凛斗', '桐人'],
  ['见习记录员', '桐人'],
  ['巨神树清场', '巨神树伐木场'],
  ['古誓树清场', '巨神树伐木场'],
  ['古誓树', '巨神树'],
  ['北境律令', '禁忌目录'],
  ['刻印术', '神圣术'],
  ['村西书道', '教会回廊'],
  ['村西书库', '教会书库']
]

export function uwCanonText(value) {
  let text = String(value || '')
  for (const [from, to] of TERM_REPLACEMENTS) {
    text = text.replaceAll(from, to)
  }
  return text.replace(/Day\s*(\d+)(?:-(\d+))?/g, (_, start, end) => end ? `第 ${start}–${end} 天` : `第 ${start} 天`)
}

export function compactPlayerText(value, maxLength = 52) {
  const text = uwCanonText(value).replace(/\s+/g, ' ').trim()
  if (!text) return ''
  return text.length > maxLength ? `${text.slice(0, Math.max(1, maxLength - 1))}…` : text
}
