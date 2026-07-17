<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

const { t } = useI18n()
const route = useRoute()

const items = [
  { to: '/', label: 'nav.home', icon: 'home' },
  { to: '/mode', label: 'nav.practice', icon: 'play' },
  { to: '/dashboard', label: 'nav.dashboard', icon: 'chart' },
  { to: '/history', label: 'nav.history', icon: 'clock' },
  { to: '/settings', label: 'nav.settings', icon: 'gear' },
]

function isActive(to: string) {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}
</script>

<template>
  <nav class="app-bottom-nav fixed bottom-0 left-0 right-0 z-40 border-t border-border bg-surface safe-area-pb" role="navigation" :aria-label="t('nav.mainNav')">
    <div class="mx-auto flex max-w-5xl items-center justify-around">
      <router-link
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="flex min-w-[64px] flex-col items-center gap-0.5 px-3 py-2 text-xs transition"
        :class="isActive(item.to) ? 'text-primary font-semibold' : 'text-on-surface-muted'"
      >
        <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <template v-if="item.icon === 'home'">
            <path d="M3 12l9-9 9 9" /><path d="M5 10v10a1 1 0 001 1h3a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1h3a1 1 0 001-1V10" />
          </template>
          <template v-else-if="item.icon === 'play'">
            <polygon points="5 3 19 12 5 21 5 3" fill="currentColor" />
          </template>
          <template v-else-if="item.icon === 'chart'">
            <path d="M18 20V10M12 20V4M6 20v-6" stroke-linecap="round" />
          </template>
          <template v-else-if="item.icon === 'clock'">
            <circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" />
          </template>
          <template v-else-if="item.icon === 'gear'">
            <circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" />
          </template>
        </svg>
        <span>{{ t(item.label) }}</span>
      </router-link>
    </div>
  </nav>
</template>

<style scoped>
.safe-area-pb {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>
