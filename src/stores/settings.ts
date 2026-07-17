import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type ThemeMode = 'light' | 'dark' | 'system'

export const useSettingsStore = defineStore('settings', () => {
  const stored = loadStored()
  const theme = ref<ThemeMode>((stored.theme as ThemeMode) ?? 'system')
  const lang = ref<string>((stored.lang as string) ?? 'en')
  const examDate = ref<string | null>((stored.examDate as string) ?? null)
  const sounds = ref(Boolean(stored.sounds ?? true))
  const haptics = ref(Boolean(stored.haptics ?? true))
  const swipeNav = ref(Boolean(stored.swipeNav ?? true))

  function loadStored(): Record<string, unknown> {
    try {
      const raw = localStorage.getItem('settings')
      return raw ? JSON.parse(raw) : {}
    } catch {
      return {}
    }
  }

  function persist() {
    localStorage.setItem(
      'settings',
      JSON.stringify({
        theme: theme.value,
        lang: lang.value,
        examDate: examDate.value,
        sounds: sounds.value,
        haptics: haptics.value,
        swipeNav: swipeNav.value,
      }),
    )
  }

  function applyTheme(t: ThemeMode) {
    const isDark =
      t === 'dark' || (t === 'system' && matchMedia('(prefers-color-scheme:dark)').matches)
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
  }

  function setTheme(t: ThemeMode) {
    theme.value = t
    applyTheme(t)
    persist()
  }

  function setLang(l: string) {
    lang.value = l
    persist()
  }

  function setExamDate(d: string | null) {
    examDate.value = d
    persist()
  }

  function toggleSounds() {
    sounds.value = !sounds.value
    persist()
  }

  function toggleHaptics() {
    haptics.value = !haptics.value
    persist()
  }

  function toggleSwipeNav() {
    swipeNav.value = !swipeNav.value
    persist()
  }

  applyTheme(theme.value)

  if (theme.value === 'system') {
    matchMedia('(prefers-color-scheme:dark)').addEventListener('change', () => {
      if (theme.value === 'system') applyTheme('system')
    })
  }

  watch(theme, () => persist())

  return {
    theme,
    lang,
    examDate,
    sounds,
    haptics,
    swipeNav,
    setTheme,
    setLang,
    setExamDate,
    toggleSounds,
    toggleHaptics,
    toggleSwipeNav,
  }
})
