/**
 * Seeded option-order shuffle for MCQ / multi questions.
 * Uses question.id (and optional session seed) so display order is stable
 * while navigating within an exam but can vary across attempts.
 */

function hashString(input: string): number {
  let hash = 2166136261
  for (let i = 0; i < input.length; i += 1) {
    hash ^= input.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

function mulberry32(seed: number): () => number {
  let s = seed >>> 0
  return () => {
    s = (s + 0x6d2b79f5) | 0
    let t = Math.imul(s ^ (s >>> 15), 1 | s)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/** Returns a permutation mapping displayIndex -> originalIndex. */
export function optionDisplayOrder(
  questionId: string,
  optionCount: number,
  sessionSeed = 0,
): number[] {
  const seed = hashString(`${questionId}:${sessionSeed}`)
  const rng = mulberry32(seed)
  const order = Array.from({ length: optionCount }, (_, i) => i)
  for (let i = order.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rng() * (i + 1))
    ;[order[i], order[j]] = [order[j], order[i]]
  }
  return order
}

export function originalToDisplayIndex(
  originalIndex: number,
  displayOrder: readonly number[],
): number {
  return displayOrder.indexOf(originalIndex)
}

export function displayToOriginalIndex(
  displayIndex: number,
  displayOrder: readonly number[],
): number {
  return displayOrder[displayIndex] ?? displayIndex
}

export function remapCorrectToDisplay(
  originalCorrect: number,
  displayOrder: readonly number[],
): number {
  return originalToDisplayIndex(originalCorrect, displayOrder)
}

export function remapCorrectListToDisplay(
  originalCorrect: readonly number[],
  displayOrder: readonly number[],
): number[] {
  return originalCorrect
    .map((idx) => originalToDisplayIndex(idx, displayOrder))
    .sort((a, b) => a - b)
}
