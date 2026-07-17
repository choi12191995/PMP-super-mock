<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

const { t } = useI18n()
const route = useRoute()

const tabs = [
  { to: '/', key: 'nav.home', icon: '🏠' },
  { to: '/mode', key: 'nav.practice', icon: '▶️' },
  { to: '/dashboard', key: 'nav.dashboard', icon: '📊' },
  { to: '/history', key: 'nav.history', icon: '🕘' },
  { to: '/settings', key: 'nav.settings', icon: '⚙️' },
]

function isActive(to: string) {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}
</script>

<template>
  <nav
    class="pointer-events-none fixed inset-x-0 bottom-0 z-40 flex justify-center px-4"
    :style="{ paddingBottom: 'max(env(safe-area-inset-bottom), 0.75rem)' }"
    role="navigation"
    :aria-label="t('nav.mainNav')"
  >
    <div class="liquid-glass pointer-events-auto flex items-center rounded-full p-1.5">
      <router-link
        v-for="tab in tabs"
        :key="tab.to"
        :to="tab.to"
        class="flex min-w-[3.5rem] flex-col items-center gap-0.5 rounded-full px-3 py-1.5 text-[11px] transition-colors duration-200 active:scale-95 sm:min-w-[4.5rem] sm:px-4"
        :class="
          isActive(tab.to)
            ? 'bg-primary/15 font-semibold text-primary dark:bg-primary/20'
            : 'text-on-surface-muted'
        "
      >
        <span class="text-lg leading-none sm:text-xl" aria-hidden="true">{{ tab.icon }}</span>
        <span>{{ t(tab.key) }}</span>
      </router-link>
    </div>
  </nav>
</template>
