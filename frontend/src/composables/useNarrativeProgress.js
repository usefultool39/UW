import { ref, watch } from 'vue'

/** 与 docs/product 中「本地存档 + 预留云同步」一致 */
export const NARRATIVE_STORAGE_KEY = '30town_narrative_v1'

function defaultFlags() {
  return { c1Done: false, c2Done: false }
}

function defaultNarrative() {
  return {
    v: 1,
    chapterId: 'ch1',
    bond: { alice: 50, eugeo: 50 },
    choiceLog: [],
    userIdReserved: null,
    lastSyncedRunId: null,
    flags: defaultFlags(),
    endingShown: false
  }
}

function loadNarrative() {
  try {
    const raw = localStorage.getItem(NARRATIVE_STORAGE_KEY)
    if (!raw) return defaultNarrative()
    const p = JSON.parse(raw)
    if (p?.v !== 1 || typeof p.bond !== 'object') return defaultNarrative()
    const base = defaultNarrative()
    return {
      ...base,
      ...p,
      bond: { ...base.bond, ...p.bond },
      choiceLog: Array.isArray(p.choiceLog) ? p.choiceLog : [],
      flags: { ...defaultFlags(), ...(p.flags || {}) },
      endingShown: Boolean(p.endingShown)
    }
  } catch {
    return defaultNarrative()
  }
}

export function useNarrativeProgress() {
  const narrative = ref(loadNarrative())

  watch(
    narrative,
    (n) => {
      try {
        localStorage.setItem(NARRATIVE_STORAGE_KEY, JSON.stringify(n))
      } catch {
        /* quota / private mode */
      }
    },
    { deep: true }
  )

  function applyDeltas(deltas, label) {
    const b = narrative.value.bond
    for (const [k, delta] of Object.entries(deltas)) {
      if (k in b && typeof delta === 'number') {
        b[k] = Math.max(0, Math.min(100, b[k] + delta))
      }
    }
    narrative.value.choiceLog.push({ t: Date.now(), label: label || '' })
    if (narrative.value.choiceLog.length > 80) {
      narrative.value.choiceLog.splice(0, narrative.value.choiceLog.length - 80)
    }
  }

  function resetNarrative() {
    narrative.value = defaultNarrative()
  }

  /** 后端重置新一局时：清章节流程与收束标记，保留羁绊数值（可手动「重置剧情」全清） */
  function resetChapterFlags() {
    narrative.value.flags = defaultFlags()
    narrative.value.endingShown = false
  }

  function setSyncedRunId(runId) {
    narrative.value.lastSyncedRunId = runId ?? null
  }

  function markC1Done() {
    narrative.value.flags.c1Done = true
  }

  function markC2Done() {
    narrative.value.flags.c2Done = true
  }

  function markEndingShown() {
    narrative.value.endingShown = true
  }

  return {
    narrative,
    applyDeltas,
    resetNarrative,
    resetChapterFlags,
    setSyncedRunId,
    markC1Done,
    markC2Done,
    markEndingShown
  }
}
