<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '@/stores/settings'

const { t, locale } = useI18n()
const settings = useSettingsStore()

function toggleLang() {
  const next = locale.value === 'en' ? 'zh-TW' : 'en'
  locale.value = next
  settings.setLang(next)
}

function cycleTheme() {
  const order: Array<'light' | 'dark' | 'system'> = ['light', 'dark', 'system']
  const idx = order.indexOf(settings.theme)
  const next = order[(idx + 1) % order.length]
  settings.setTheme(next)
}
</script>

<template>
  <header class="sticky top-0 z-40 border-b border-border bg-surface/95 backdrop-blur" role="banner">
    <div class="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
      <router-link to="/" class="flex items-center gap-2 font-bold text-primary">
        <span class="text-xl">{{ t('app.title') }}</span>
      </router-link>
      <div class="flex items-center gap-2">
        <button
          class="touch-target rounded-lg px-3 py-1.5 text-sm font-medium text-on-surface-muted transition hover:bg-surface-alt focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          :title="t('settings.theme')"
          @click="cycleTheme"
        >
          {{ settings.theme === 'dark' ? '🌙' : settings.theme === 'light' ? '☀️' : '💻' }}
        </button>
        <button
          class="touch-target rounded-lg px-3 py-1.5 text-sm font-medium text-on-surface-muted transition hover:bg-surface-alt"
          :title="t('settings.language')"
          :aria-label="locale === 'en' ? t('common.switchToZh') : t('common.switchToEn')"
          @click="toggleLang"
        >
          {{ locale === 'en' ? t('common.switchToZh') : t('common.switchToEn') }}
        </button>
      </div>
    </div>
  </header>
</template>
