export type TimerMode = 'off' | 'count-up' | 'countdown'

export interface ExamTimerSerialized {
  mode: TimerMode
  totalSeconds?: number
  startedAt: number | null
  pausedAt: number | null
  pausedAccum: number
}

export class ExamTimer {
  private mode: TimerMode
  private totalSeconds: number | undefined
  private startedAt: number | null = null
  private pausedAt: number | null = null
  private pausedAccum = 0
  private tickInterval: ReturnType<typeof setInterval> | null = null
  private tickCallbacks = new Set<(remaining: number) => void>()
  private expireCallbacks = new Set<() => void>()
  private expired = false
  private visibilityHandler: (() => void) | null = null

  constructor(mode: TimerMode, totalSeconds?: number) {
    this.mode = mode
    this.totalSeconds = totalSeconds
  }

  start(): void {
    if (this.mode === 'off' || this.startedAt !== null) return
    this.startedAt = Date.now()
    this.expired = false
    this.attachVisibilityHandler()
    this.startTickInterval()
  }

  pause(): void {
    if (this.mode === 'off' || this.startedAt === null || this.pausedAt !== null) return
    this.pausedAt = Date.now()
    this.stopTickInterval()
  }

  resume(): void {
    if (this.mode === 'off' || this.startedAt === null || this.pausedAt === null) return
    this.pausedAccum += Date.now() - this.pausedAt
    this.pausedAt = null
    this.startTickInterval()
    this.recompute()
  }

  getElapsed(): number {
    if (this.mode === 'off' || this.startedAt === null) return 0
    const end = this.pausedAt ?? Date.now()
    return Math.max(0, (end - this.startedAt - this.pausedAccum) / 1000)
  }

  getRemaining(): number {
    if (this.mode !== 'countdown' || this.totalSeconds === undefined) {
      return this.mode === 'count-up' ? this.getElapsed() : 0
    }
    return Math.max(0, this.totalSeconds - this.getElapsed())
  }

  isExpired(): boolean {
    if (this.mode !== 'countdown' || this.totalSeconds === undefined) return false
    return this.getRemaining() <= 0
  }

  onTick(callback: (remaining: number) => void): void {
    this.tickCallbacks.add(callback)
  }

  onExpire(callback: () => void): void {
    this.expireCallbacks.add(callback)
  }

  destroy(): void {
    this.stopTickInterval()
    this.detachVisibilityHandler()
    this.tickCallbacks.clear()
    this.expireCallbacks.clear()
  }

  serialize(): ExamTimerSerialized {
    return {
      mode: this.mode,
      totalSeconds: this.totalSeconds,
      startedAt: this.startedAt,
      pausedAt: this.pausedAt,
      pausedAccum: this.pausedAccum,
    }
  }

  static deserialize(data: ExamTimerSerialized): ExamTimer {
    const timer = new ExamTimer(data.mode, data.totalSeconds)
    timer.startedAt = data.startedAt
    timer.pausedAt = data.pausedAt
    timer.pausedAccum = data.pausedAccum
    if (timer.startedAt !== null && timer.pausedAt === null) {
      timer.attachVisibilityHandler()
      timer.startTickInterval()
      timer.recompute()
    }
    return timer
  }

  private startTickInterval(): void {
    if (this.mode === 'off' || this.tickInterval !== null) return
    this.tickInterval = setInterval(() => this.recompute(), 1000)
  }

  private stopTickInterval(): void {
    if (this.tickInterval === null) return
    clearInterval(this.tickInterval)
    this.tickInterval = null
  }

  private attachVisibilityHandler(): void {
    if (typeof document === 'undefined' || this.visibilityHandler !== null) return
    this.visibilityHandler = () => {
      if (document.visibilityState === 'visible') this.recompute()
    }
    document.addEventListener('visibilitychange', this.visibilityHandler)
  }

  private detachVisibilityHandler(): void {
    if (typeof document === 'undefined' || this.visibilityHandler === null) return
    document.removeEventListener('visibilitychange', this.visibilityHandler)
    this.visibilityHandler = null
  }

  private recompute(): void {
    const tickValue = this.getRemaining()
    for (const callback of this.tickCallbacks) callback(tickValue)

    if (this.mode === 'countdown' && !this.expired && this.isExpired()) {
      this.expired = true
      this.stopTickInterval()
      for (const callback of this.expireCallbacks) callback()
    }
  }
}
