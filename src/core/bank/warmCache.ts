import { loadManifest } from './loader'

export interface WarmCacheProgress {
  done: number
  total: number
  pct: number
  current?: string
}

export async function warmQuestionBankCache(
  onProgress?: (p: WarmCacheProgress) => void,
): Promise<void> {
  const manifest = await loadManifest()
  const files = [
    '/questions/manifest.json',
    ...manifest.chunks.map((c) => `/questions/${c.file}`),
    ...manifest.cases.map((c) => `/questions/${c.file}`),
  ]

  const total = files.length
  let done = 0

  for (const url of files) {
    onProgress?.({ done, total, pct: Math.round((done / total) * 100), current: url })
    const res = await fetch(url, { cache: 'force-cache' })
    if (!res.ok) throw new Error(`Failed to cache ${url}: ${res.status}`)
    await res.blob()
    done += 1
    onProgress?.({ done, total, pct: Math.round((done / total) * 100), current: url })
  }
}

export async function isBankCached(): Promise<boolean> {
  if (!('caches' in window)) return false
  try {
    const cache = await caches.open('question-bank')
    const manifest = await cache.match('/questions/manifest.json')
    return manifest != null
  } catch {
    return false
  }
}
