let persistRequested = false

export async function requestPersistentStorage(): Promise<boolean> {
  if (persistRequested) return true
  if (!navigator.storage?.persist) return false

  try {
    const already = await navigator.storage.persisted()
    if (already) {
      persistRequested = true
      return true
    }
    const granted = await navigator.storage.persist()
    persistRequested = granted
    return granted
  } catch {
    return false
  }
}

export async function getStorageEstimate(): Promise<{ usage: number; quota: number } | null> {
  if (!navigator.storage?.estimate) return null
  try {
    const est = await navigator.storage.estimate()
    return { usage: est.usage ?? 0, quota: est.quota ?? 0 }
  } catch {
    return null
  }
}
