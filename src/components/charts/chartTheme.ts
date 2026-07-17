export function chartColors(): {
  text: string
  grid: string
  primary: string
  success: string
  warning: string
  danger: string
  surface: string
} {
  const style = getComputedStyle(document.documentElement)
  const get = (name: string, fallback: string) =>
    style.getPropertyValue(name).trim() || fallback

  return {
    text: get('--color-on-surface-muted', '#64748b'),
    grid: get('--color-border', '#e2e8f0'),
    primary: get('--color-primary', '#4f46e5'),
    success: get('--color-success', '#16a34a'),
    warning: get('--color-warning', '#d97706'),
    danger: get('--color-danger', '#dc2626'),
    surface: get('--color-surface-raised', '#ffffff'),
  }
}

export function domainColor(domain: string): string {
  const style = getComputedStyle(document.documentElement)
  const map: Record<string, string> = {
    people: '--color-people',
    process: '--color-process',
    business: '--color-business',
  }
  const varName = map[domain]
  if (!varName) return '#4f46e5'
  return style.getPropertyValue(varName).trim() || '#4f46e5'
}
