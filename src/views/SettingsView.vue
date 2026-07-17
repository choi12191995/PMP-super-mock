<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '@/stores/settings'

const { t } = useI18n()
const settings = useSettingsStore()
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 pb-24 pt-6">
    <h1 class="mb-6 text-2xl font-bold text-on-surface">{{ t('settings.title') }}</h1>

    <section class="mb-6">
      <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-on-surface-muted">
        {{ t('settings.appearance') }}
      </h2>
      <div class="space-y-3">
        <div class="flex items-center justify-between rounded-xl border border-border bg-surface-raised p-4">
          <span class="text-on-surface">{{ t('settings.theme') }}</span>
          <div class="flex gap-1">
            <button
              v-for="opt in (['light', 'dark', 'system'] as const)"
              :key="opt"
              class="rounded-lg px-3 py-1.5 text-sm transition"
              :class="settings.theme === opt ? 'bg-primary text-white' : 'text-on-surface-muted hover:bg-surface-alt'"
              @click="settings.setTheme(opt)"
            >
              {{ t(`settings.theme${opt.charAt(0).toUpperCase() + opt.slice(1)}`) }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="mb-6">
      <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-on-surface-muted">
        {{ t('settings.data') }}
      </h2>
      <div class="space-y-3">
        <div class="rounded-xl border border-border bg-surface-raised p-4">
          <p class="font-medium text-on-surface">{{ t('settings.backup') }}</p>
          <p class="text-sm text-on-surface-muted">{{ t('settings.backupDesc') }}</p>
        </div>
        <div class="rounded-xl border border-border bg-surface-raised p-4">
          <p class="font-medium text-on-surface">{{ t('settings.restore') }}</p>
          <p class="text-sm text-on-surface-muted">{{ t('settings.restoreDesc') }}</p>
        </div>
      </div>
    </section>
  </div>
</template>
