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

/**
 * Rewrite option label references in explanation text to match shuffled display order.
 * Maps "Option A/B/C/D" and "選項 A/B/C/D" from original bank order to displayed order.
 */
export function remapExplanationLabels(
  text: string,
  displayOrder: readonly number[],
): string {
  const labels = displayOrder.map((_, i) => String.fromCharCode(65 + i))
  const mapping = new Map<string, string>()
  for (let origIdx = 0; origIdx < displayOrder.length; origIdx++) {
    const origLabel = String.fromCharCode(65 + origIdx)
    const displayIdx = originalToDisplayIndex(origIdx, displayOrder)
    const displayLabel = labels[displayIdx] ?? origLabel
    if (origLabel !== displayLabel) {
      mapping.set(origLabel, displayLabel)
    }
  }

  if (mapping.size === 0) return text

  const placeholder = '\x00'
  let result = text
  const tempMap = new Map<string, string>()
  let tempIdx = 0

  for (const [orig, display] of mapping) {
    const temp = `${placeholder}${tempIdx}${placeholder}`
    tempMap.set(temp, display)
    const enPattern = new RegExp(`Option ${orig}\\b`, 'g')
    const zhPattern = new RegExp(`選項\\s*${orig}\\b`, 'g')
    result = result.replace(enPattern, `Option ${temp}`)
    result = result.replace(zhPattern, `選項 ${temp}`)
    tempIdx++
  }

  for (const [temp, display] of tempMap) {
    result = result.replaceAll(temp, display)
  }

  return result
}
