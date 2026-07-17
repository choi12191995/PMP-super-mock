import { db } from './index'

const SCHEMA_VERSION = 1

export interface BackupData {
  schemaVersion: number
  exportedAt: string
  settings: Record<string, unknown> | null
  ai: Record<string, unknown> | null
  attempts: unknown[]
  answers: unknown[]
  srs: unknown[]
  daily: unknown[]
}

export async function exportData(includeApiKey = false): Promise<BackupData> {
  const [attempts, answers, srs, daily] = await Promise.all([
    db.attempts.toArray(),
    db.answers.toArray(),
    db.srs.toArray(),
    db.daily.toArray(),
  ])

  let settingsRaw: Record<string, unknown> | null = null
  try {
    const s = localStorage.getItem('settings')
    if (s) settingsRaw = JSON.parse(s)
  } catch {
    /* ignore */
  }

  let aiRaw: Record<string, unknown> | null = null
  if (includeApiKey) {
    try {
      const a = localStorage.getItem('ai')
      if (a) aiRaw = JSON.parse(a)
    } catch {
      /* ignore */
    }
  }

  return {
    schemaVersion: SCHEMA_VERSION,
    exportedAt: new Date().toISOString(),
    settings: settingsRaw,
    ai: aiRaw,
    attempts,
    answers,
    srs,
    daily,
  }
}

export async function importData(data: BackupData, merge = false): Promise<void> {
  if (!data.schemaVersion || data.schemaVersion > SCHEMA_VERSION) {
    throw new Error(`Unsupported backup version: ${data.schemaVersion}`)
  }

  if (!merge) {
    await Promise.all([
      db.attempts.clear(),
      db.answers.clear(),
      db.srs.clear(),
      db.daily.clear(),
    ])
  }

  await Promise.all([
    db.attempts.bulkPut(data.attempts as Parameters<typeof db.attempts.bulkPut>[0]),
    db.answers.bulkPut(data.answers as Parameters<typeof db.answers.bulkPut>[0]),
    db.srs.bulkPut(data.srs as Parameters<typeof db.srs.bulkPut>[0]),
    db.daily.bulkPut(data.daily as Parameters<typeof db.daily.bulkPut>[0]),
  ])

  if (data.settings) {
    localStorage.setItem('settings', JSON.stringify(data.settings))
  }
  if (data.ai) {
    localStorage.setItem('ai', JSON.stringify(data.ai))
  }
}

export function downloadJson(data: unknown, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
