import { ref, computed } from 'vue'

const STORAGE_KEY = 'uw-audio-muted'
const VOLUME_STORAGE_KEY = 'uw-audio-volume'
const missingAudioUrls = new Set()
const warnedAudioUrls = new Set()
const PROCEDURAL_SFX_URLS = new Set([
  '/assets/audio/sfx_step.mp3',
  '/assets/audio/sfx_activity.mp3'
])

function loadSettings() {
  try {
    return {
      muted: localStorage.getItem(STORAGE_KEY) === 'true',
      volume: Number(localStorage.getItem(VOLUME_STORAGE_KEY)) || 0.7
    }
  } catch {
    return { muted: false, volume: 0.7 }
  }
}

function saveSettings(muted, volume) {
  try {
    localStorage.setItem(STORAGE_KEY, String(muted))
    localStorage.setItem(VOLUME_STORAGE_KEY, String(volume))
  } catch {
    // ignore
  }
}

function warnMissingAudio(url) {
  if (!url || warnedAudioUrls.has(url)) return
  warnedAudioUrls.add(url)
  console.warn(`[useAudio] audio asset missing, skipping: ${url}`)
}

async function fetchAudioBuffer(url) {
  if (!url || missingAudioUrls.has(url)) return null
  try {
    const response = await fetch(url)
    if (!response.ok) {
      missingAudioUrls.add(url)
      warnMissingAudio(url)
      return null
    }
    return await response.arrayBuffer()
  } catch {
    missingAudioUrls.add(url)
    warnMissingAudio(url)
    return null
  }
}

function hasProceduralSfx(url) {
  return PROCEDURAL_SFX_URLS.has(String(url || ''))
}

function createStepSfx(ctx) {
  const length = Math.floor(ctx.sampleRate * 0.22)
  const buffer = ctx.createBuffer(1, length, ctx.sampleRate)
  const data = buffer.getChannelData(0)
  for (let i = 0; i < length; i += 1) {
    const t = i / ctx.sampleRate
    const env = Math.exp(-t * 18)
    const thump = Math.sin(2 * Math.PI * 95 * t) * 0.26
    const grit = (Math.random() * 2 - 1) * 0.11
    data[i] = (thump + grit) * env
  }
  return buffer
}

function createActivitySfx(ctx) {
  const length = Math.floor(ctx.sampleRate * 0.55)
  const buffer = ctx.createBuffer(1, length, ctx.sampleRate)
  const data = buffer.getChannelData(0)
  for (let i = 0; i < length; i += 1) {
    const t = i / ctx.sampleRate
    const env = Math.min(1, t / 0.035) * Math.exp(-t * 4.2)
    const bell = Math.sin(2 * Math.PI * 660 * t) * 0.18
    const overtone = Math.sin(2 * Math.PI * 990 * t) * 0.08
    data[i] = (bell + overtone) * env
  }
  return buffer
}

function createProceduralSfx(ctx, url) {
  if (url === '/assets/audio/sfx_step.mp3') return createStepSfx(ctx)
  if (url === '/assets/audio/sfx_activity.mp3') return createActivitySfx(ctx)
  return null
}

export function useAudio() {
  const settings = loadSettings()
  const muted = ref(settings.muted)
  const volume = ref(settings.volume)
  const bgmPlaying = ref(false)

  let audioContext = null
  let bgmGain = null
  let bgmSource = null

  function getCtx() {
    if (!audioContext) {
      audioContext = new (window.AudioContext || window.webkitAudioContext)()
    }
    return audioContext
  }

  function ensureResumed() {
    const ctx = getCtx()
    if (ctx.state === 'suspended') {
      ctx.resume()
    }
  }

  function applyVolumeToSource(source, gainNode) {
    if (!source || !gainNode) return
    gainNode.gain.setValueAtTime(muted.value ? 0 : volume.value, getCtx().currentTime)
  }

  // --- BGM ---
  async function playBgm(url) {
    if (muted.value || !url || missingAudioUrls.has(url)) return
    ensureResumed()
    try {
      const ctx = getCtx()
      if (bgmSource) {
        try { bgmSource.stop() } catch { /* ignore */ }
        bgmSource = null
      }
      if (!bgmGain) {
        bgmGain = ctx.createGain()
        bgmGain.connect(ctx.destination)
      }
      bgmGain.gain.setValueAtTime(volume.value, ctx.currentTime)
      const arrayBuffer = await fetchAudioBuffer(url)
      if (!arrayBuffer) return
      const audioBuffer = await ctx.decodeAudioData(arrayBuffer)
      const source = ctx.createBufferSource()
      source.buffer = audioBuffer
      source.loop = true
      source.connect(bgmGain)
      source.start()
      bgmSource = source
      bgmPlaying.value = true
    } catch (e) {
      console.warn('[useAudio] bgm failed:', e)
    }
  }

  function stopBgm() {
    if (bgmSource) {
      try { bgmSource.stop() } catch { /* ignore */ }
      bgmSource = null
    }
    bgmPlaying.value = false
  }

  // --- SFX ---
  async function playSfx(url) {
    if (muted.value || !url || (!hasProceduralSfx(url) && missingAudioUrls.has(url))) return
    ensureResumed()
    try {
      const ctx = getCtx()
      const audioBuffer = createProceduralSfx(ctx, url) || await (async () => {
        const arrayBuffer = await fetchAudioBuffer(url)
        return arrayBuffer ? ctx.decodeAudioData(arrayBuffer) : null
      })()
      if (!audioBuffer) return
      const source = ctx.createBufferSource()
      source.buffer = audioBuffer
      const gain = ctx.createGain()
      gain.gain.setValueAtTime(volume.value, ctx.currentTime)
      source.connect(gain)
      gain.connect(ctx.destination)
      source.start()
    } catch (e) {
      console.warn('[useAudio] sfx failed:', e)
    }
  }

  // --- Controls ---
  function toggleMute() {
    muted.value = !muted.value
    saveSettings(muted.value, volume.value)
    if (bgmGain && bgmSource) {
      bgmGain.gain.setValueAtTime(muted.value ? 0 : volume.value, getCtx().currentTime)
    }
  }

  function setVolume(v) {
    volume.value = v
    saveSettings(muted.value, v)
    if (bgmGain && !muted.value) {
      bgmGain.gain.setValueAtTime(v, getCtx().currentTime)
    }
  }

  const isMuted = computed(() => muted.value)
  const currentVolume = computed(() => volume.value)

  return {
    muted,
    isMuted,
    currentVolume,
    bgmPlaying,
    playBgm,
    stopBgm,
    playSfx,
    toggleMute,
    setVolume
  }
}
