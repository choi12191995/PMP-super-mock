import { describe, it, expect } from 'vitest'
import { EXAM, ECO_TASKS } from './examConstants'

describe('examConstants', () => {
  it('has 180 total questions', () => {
    expect(EXAM.TOTAL_QUESTIONS).toBe(180)
  })

  it('section totals equal total questions', () => {
    expect(EXAM.SECTION_A_TOTAL + EXAM.SECTION_B_TOTAL + EXAM.SECTION_C_TOTAL).toBe(
      EXAM.TOTAL_QUESTIONS,
    )
  })

  it('domain weights sum to 1', () => {
    const sum = Object.values(EXAM.DOMAIN_WEIGHTS).reduce((a, b) => a + b, 0)
    expect(sum).toBeCloseTo(1, 5)
  })

  it('has 26 ECO tasks', () => {
    const total =
      ECO_TASKS.people.length + ECO_TASKS.process.length + ECO_TASKS.business.length
    expect(total).toBe(26)
  })
})
