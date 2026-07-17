import { useSettingsStore } from '@/stores/settings'

let audioCtx: AudioContext | null = null

function getAudioContext(): AudioContext | null {
  if (typeof window === 'undefined') return null
  if (!audioCtx) {
    try {
      audioCtx = new AudioContext()
    } catch {
      return null
    }
  }
  return audioCtx
}

export function playPassSound(): void {
  const settings = useSettingsStore()
  if (!settings.sounds) return

  const ctx = getAudioContext()
  if (!ctx) return

  const osc = ctx.createOscillator()
  const gain = ctx.createGain()
  osc.connect(gain)
  gain.connect(ctx.destination)
  osc.type = 'sine'
  osc.frequency.setValueAtTime(523.25, ctx.currentTime)
  osc.frequency.setValueAtTime(659.25, ctx.currentTime + 0.1)
  osc.frequency.setValueAtTime(783.99, ctx.currentTime + 0.2)
  gain.gain.setValueAtTime(0.15, ctx.currentTime)
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4)
  osc.start(ctx.currentTime)
  osc.stop(ctx.currentTime + 0.4)
}

export function playCorrectSound(): void {
  const settings = useSettingsStore()
  if (!settings.sounds) return

  const ctx = getAudioContext()
  if (!ctx) return

  const osc = ctx.createOscillator()
  const gain = ctx.createGain()
  osc.connect(gain)
  gain.connect(ctx.destination)
  osc.type = 'sine'
  osc.frequency.setValueAtTime(880, ctx.currentTime)
  gain.gain.setValueAtTime(0.1, ctx.currentTime)
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.15)
  osc.start(ctx.currentTime)
  osc.stop(ctx.currentTime + 0.15)
}

export function hapticSuccess(): void {
  const settings = useSettingsStore()
  if (!settings.haptics || !navigator.vibrate) return
  navigator.vibrate(50)
}

export function hapticPass(): void {
  const settings = useSettingsStore()
  if (!settings.haptics || !navigator.vibrate) return
  navigator.vibrate([30, 50, 30])
}
