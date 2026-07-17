import type { Question, CaseSet, BankManifest } from '../types'

let manifestCache: BankManifest | null = null
const chunkCache = new Map<string, Question[]>()
const caseCache = new Map<string, CaseSet[]>()

export async function loadManifest(): Promise<BankManifest> {
  if (manifestCache) return manifestCache
  const res = await fetch('/questions/manifest.json')
  if (!res.ok) throw new Error(`Failed to load manifest: ${res.status}`)
  manifestCache = (await res.json()) as BankManifest
  return manifestCache
}

export async function loadChunk(file: string): Promise<Question[]> {
  const cached = chunkCache.get(file)
  if (cached) return cached
  const res = await fetch(`/questions/${file}`)
  if (!res.ok) throw new Error(`Failed to load chunk ${file}: ${res.status}`)
  const questions = (await res.json()) as Question[]
  chunkCache.set(file, questions)
  return questions
}

export async function loadCases(file: string): Promise<CaseSet[]> {
  const cached = caseCache.get(file)
  if (cached) return cached
  const res = await fetch(`/questions/${file}`)
  if (!res.ok) throw new Error(`Failed to load cases ${file}: ${res.status}`)
  const cases = (await res.json()) as CaseSet[]
  caseCache.set(file, cases)
  return cases
}

export async function loadAllQuestions(): Promise<Question[]> {
  const manifest = await loadManifest()
  const chunks = await Promise.all(manifest.chunks.map((c) => loadChunk(c.file)))
  return chunks.flat()
}

export async function loadAllCases(): Promise<CaseSet[]> {
  const manifest = await loadManifest()
  const caseSets = await Promise.all(manifest.cases.map((c) => loadCases(c.file)))
  return caseSets.flat()
}

export function clearCache() {
  manifestCache = null
  chunkCache.clear()
  caseCache.clear()
}
