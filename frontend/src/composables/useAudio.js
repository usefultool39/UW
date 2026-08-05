import { ref, computed } from 'vue'
import { RUNTIME_AUDIO } from '../field/runtimeAssetPaths.js'

const STORAGE_KEY = 'uw-audio-muted'
const VOLUME_STORAGE_KEY = 'uw-audio-volume'
const missingAudioUrls = new Set()
const warnedAudioUrls = new Set()
const PROCEDURAL_SFX_URLS = new Set([
  '/assets/audio/sfx_step.mp3',
  '/assets/audio/sfx_activity.mp3'
])
const PROCEDURAL_BGM_URL = 'procedural:luin_morning'
const RUNTIME_BGM_URL = RUNTIME_AUDIO.bgmVillageDawn
const RUNTIME_AMBIENCE_URLS = { drizzle: RUNTIME_AUDIO.ambienceDrizzle }

function loadSettings() {
  try {
    if (typeof localStorage === 'undefined') throw new Error('storage unavailable')
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
    if (typeof localStorage === 'undefined') return
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

function createMorningBgm(ctx) {
  const seconds = 7.5
  const length = Math.floor(ctx.sampleRate * seconds)
  const buffer = ctx.createBuffer(2, length, ctx.sampleRate)
  const notes = [196, 246.94, 293.66, 329.63]
  for (let ch = 0; ch < buffer.numberOfChannels; ch += 1) {
    const data = buffer.getChannelData(ch)
    for (let i = 0; i < length; i += 1) {
      const t = i / ctx.sampleRate
      const chord = notes.reduce((sum, freq, index) => {
        const drift = Math.sin(t * 0.18 + index) * 0.8
        const panOffset = ch === 0 ? index * 0.04 : index * 0.06
        return sum + Math.sin(2 * Math.PI * (freq + drift) * (t + panOffset)) * (0.035 / (index + 1))
      }, 0)
      const bell =
        Math.sin(2 * Math.PI * 784 * t) *
        Math.max(0, Math.sin((t / seconds) * Math.PI * 2)) *
        0.012
      const breath = Math.sin(2 * Math.PI * 0.09 * t + ch) * 0.018
      data[i] = chord + bell + breath
    }
  }
  return buffer
}

function createDrizzleBuffer(ctx) {
  const seconds = 2.8
  const length = Math.floor(ctx.sampleRate * seconds)
  const buffer = ctx.createBuffer(2, length, ctx.sampleRate)
  for (let ch = 0; ch < buffer.numberOfChannels; ch += 1) {
    const data = buffer.getChannelData(ch)
    let smooth = 0
    for (let i = 0; i < length; i += 1) {
      const white = Math.random() * 2 - 1
      smooth = smooth * 0.94 + white * 0.06
      const t = i / ctx.sampleRate
      const ripple = Math.sin(2 * Math.PI * (1.7 + ch * 0.2) * t) * 0.025
      data[i] = smooth * 0.16 + ripple
    }
  }
  return buffer
}

const settings = loadSettings()
const muted = ref(settings.muted)
const volume = ref(Math.min(1, Math.max(0, settings.volume)))
const bgmPlaying = ref(false)
const ambiencePlaying = ref(false)

let audioContext = null
let bgmGain = null
let bgmSource = null
let ambienceGain = null
let ambienceSource = null

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

function bgmLevel() {
  return muted.value ? 0 : volume.value * 0.34
}

function ambienceLevel() {
  return muted.value ? 0 : volume.value * 0.2
}

function applyOutputLevels() {
  const ctx = audioContext
  if (!ctx) return
  if (bgmGain) bgmGain.gain.setTargetAtTime(bgmLevel(), ctx.currentTime, 0.08)
  if (ambienceGain) ambienceGain.gain.setTargetAtTime(ambienceLevel(), ctx.currentTime, 0.08)
}

export function useAudio() {

  // --- BGM ---
  async function playBgm(url = PROCEDURAL_BGM_URL) {
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
      bgmGain.gain.setValueAtTime(bgmLevel(), ctx.currentTime)
      let audioBuffer = url === PROCEDURAL_BGM_URL
        ? createMorningBgm(ctx)
        : await (async () => {
          const arrayBuffer = await fetchAudioBuffer(url)
          return arrayBuffer ? ctx.decodeAudioData(arrayBuffer) : null
        })()
      // Runtime 素材是增强层；若本地打包或浏览器不支持，自动回退到程序化晨曲。
      if (!audioBuffer && url !== PROCEDURAL_BGM_URL) audioBuffer = createMorningBgm(ctx)
      if (!audioBuffer) return
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

  async function startAmbience(kind = 'drizzle') {
    if (muted.value) return
    ensureResumed()
    try {
      const ctx = getCtx()
      if (ambienceSource) {
        try { ambienceSource.stop() } catch { /* ignore */ }
        ambienceSource = null
      }
      if (!ambienceGain) {
        ambienceGain = ctx.createGain()
        ambienceGain.connect(ctx.destination)
      }
      ambienceGain.gain.setValueAtTime(ambienceLevel(), ctx.currentTime)
      const runtimeUrl = RUNTIME_AMBIENCE_URLS[kind]
      const arrayBuffer = runtimeUrl ? await fetchAudioBuffer(runtimeUrl) : null
      const audioBuffer = arrayBuffer ? await ctx.decodeAudioData(arrayBuffer) : createDrizzleBuffer(ctx, kind)
      const source = ctx.createBufferSource()
      source.buffer = audioBuffer
      source.loop = true
      source.connect(ambienceGain)
      source.start()
      ambienceSource = source
      ambiencePlaying.value = true
    } catch (e) {
      console.warn('[useAudio] ambience failed:', e)
    }
  }

  function stopAmbience() {
    if (ambienceSource) {
      try { ambienceSource.stop() } catch { /* ignore */ }
      ambienceSource = null
    }
    ambiencePlaying.value = false
  }

  async function startFieldAudio(weather = 'drizzle') {
    if (muted.value) return
    await playBgm(RUNTIME_BGM_URL)
    await startAmbience(weather)
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
    applyOutputLevels()
  }

  function setVolume(v) {
    const next = Math.min(1, Math.max(0, Number(v) || 0))
    volume.value = next
    saveSettings(muted.value, next)
    applyOutputLevels()
  }

  const isMuted = computed(() => muted.value)
  const currentVolume = computed(() => volume.value)

  return {
    muted,
    isMuted,
    currentVolume,
    bgmPlaying,
    ambiencePlaying,
    playBgm,
    stopBgm,
    startAmbience,
    stopAmbience,
    startFieldAudio,
    playSfx,
    toggleMute,
    setVolume
  }
}
