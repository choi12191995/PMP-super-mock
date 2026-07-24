import { describe, expect, it } from 'vitest'
import {
  displayToOriginalIndex,
  optionDisplayOrder,
  originalToDisplayIndex,
  remapCorrectListToDisplay,
  remapCorrectToDisplay,
  remapExplanationLabels,
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

describe('remapExplanationLabels', () => {
  it('remaps English option references to match display order', () => {
    // displayOrder [2, 0, 3, 1] means display A = original C, B = original A, etc.
    const order = [2, 0, 3, 1]
    const text = 'Option A is correct. Option B is wrong. Option C is also wrong. Option D is wrong.'
    const result = remapExplanationLabels(text, order)
    // Original A → display position = indexOf(0) = 1 → B
    // Original B → display position = indexOf(1) = 3 → D
    // Original C → display position = indexOf(2) = 0 → A
    // Original D → display position = indexOf(3) = 2 → C
    expect(result).toBe('Option B is correct. Option D is wrong. Option A is also wrong. Option C is wrong.')
  })

  it('remaps Chinese option references', () => {
    const order = [1, 0, 2, 3] // A↔B swap
    const text = '選項 A 正確。選項 B 錯誤。'
    const result = remapExplanationLabels(text, order)
    // Original A → indexOf(0) = 1 → B
    // Original B → indexOf(1) = 0 → A
    expect(result).toBe('選項 B 正確。選項 A 錯誤。')
  })

  it('returns text unchanged when order is identity', () => {
    const order = [0, 1, 2, 3]
    const text = 'Option A is correct. Option B is wrong.'
    expect(remapExplanationLabels(text, order)).toBe(text)
  })

  it('handles partial swaps without corrupting labels', () => {
    const order = [1, 0, 2, 3] // only A↔B are swapped
    const text = 'Option A is correct because it addresses the need. Option C is wrong.'
    const result = remapExplanationLabels(text, order)
    expect(result).toBe('Option B is correct because it addresses the need. Option C is wrong.')
  })
})
