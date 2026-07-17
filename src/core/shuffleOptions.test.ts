import { describe, expect, it } from 'vitest'
import {
  displayToOriginalIndex,
  optionDisplayOrder,
  originalToDisplayIndex,
  remapCorrectListToDisplay,
  remapCorrectToDisplay,
} from './shuffleOptions'

describe('shuffleOptions', () => {
  it('produces stable order for same question id and session seed', () => {
    const a = optionDisplayOrder('PPL-0021', 4, 12345)
    const b = optionDisplayOrder('PPL-0021', 4, 12345)
    expect(a).toEqual(b)
  })

  it('varies order between session seeds', () => {
    const a = optionDisplayOrder('PPL-0021', 4, 1)
    const b = optionDisplayOrder('PPL-0021', 4, 2)
    expect(a).not.toEqual(b)
  })

  it('remaps indices correctly', () => {
    const order = optionDisplayOrder('PRC-0100', 4, 0)
    const original = 2
    const display = originalToDisplayIndex(original, order)
    expect(displayToOriginalIndex(display, order)).toBe(original)
    expect(remapCorrectToDisplay(original, order)).toBe(display)
  })

  it('remaps multi correct answers to display indices', () => {
    const order = optionDisplayOrder('BE-0020', 5, 99)
    const displayCorrect = remapCorrectListToDisplay([0, 3], order)
    expect(displayCorrect).toHaveLength(2)
    for (const d of displayCorrect) {
      expect(displayToOriginalIndex(d, order)).toBeGreaterThanOrEqual(0)
    }
  })
})
