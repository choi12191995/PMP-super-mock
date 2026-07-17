import { describe, it, expect } from 'vitest'
import {
  SRS_INTERVALS_DAYS,
  nextIntervalDays,
  computeDue,
  createSrsRecord,
  advanceSrsRecord,
  pickDaily10Questions,
} from './index'

describe('SRS scheduling', () => {
  it('uses 1/3/7/14-day intervals', () => {
    expect(SRS_INTERVALS_DAYS).toEqual([1, 3, 7, 14])
    expect(nextIntervalDays(1)).toBe(1)
    expect(nextIntervalDays(2)).toBe(3)
    expect(nextIntervalDays(3)).toBe(7)
    expect(nextIntervalDays(4)).toBe(14)
    expect(nextIntervalDays(99)).toBe(14)
  })

  it('computes due date from last wrong + interval', () => {
    const now = 1_700_000_000_000
    expect(computeDue(now, 3)).toBe(now + 3 * 86_400_000)
  })

  it('creates initial SRS record on first wrong', () => {
    const now = 1_700_000_000_000
    const record = createSrsRecord('q1', now)
    expect(record.wrongCount).toBe(1)
    expect(record.interval).toBe(1)
    expect(record.due).toBe(now + 86_400_000)
  })

  it('advances interval on repeated wrong answers', () => {
    const now = 1_700_000_000_000
    let record = createSrsRecord('q1', now)
    record = advanceSrsRecord(record, now + 1000)
    expect(record.wrongCount).toBe(2)
    expect(record.interval).toBe(3)

    record = advanceSrsRecord(record, now + 2000)
    expect(record.wrongCount).toBe(3)
    expect(record.interval).toBe(7)
  })

  it('pickDaily10 mixes due SRS and fresh questions', () => {
    const all = Array.from({ length: 20 }, (_, i) => ({ id: `q${i}` }))
    const seen = new Set(['q5', 'q6'])
    const due = ['q0', 'q1']
    const picked = pickDaily10Questions(all, due, seen, 10)
    expect(picked).toHaveLength(10)
    expect(picked[0]).toBe('q0')
    expect(picked[1]).toBe('q1')
    expect(new Set(picked).size).toBe(10)
  })
})
