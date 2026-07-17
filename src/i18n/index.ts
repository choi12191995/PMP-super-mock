import { createI18n } from 'vue-i18n'
import en from './en.json'
import zhTW from './zh-TW.json'

function getDefaultLocale(): string {
  try {
    const stored = localStorage.getItem('settings')
    if (stored) {
      const s = JSON.parse(stored)
      if (s.lang) return s.lang
    }
  } catch {
    /* ignore */
  }
  const nav = navigator.language
  if (nav.startsWith('zh')) return 'zh-TW'
  return 'en'
}

export const i18n = createI18n({
  legacy: false,
  locale: getDefaultLocale(),
  fallbackLocale: 'en',
  messages: { en, 'zh-TW': zhTW },
})
