<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 pb-24 pt-6">
    <h1 class="mb-4 text-2xl font-bold text-on-surface">{{ t('about.title') }}</h1>
    <p class="mb-4 text-on-surface">{{ t('about.description') }}</p>
    <p class="mb-4 text-sm text-on-surface-muted">{{ t('about.version', { version: '0.1.0' }) }}</p>
    <div class="rounded-xl border border-warning/30 bg-warning/5 p-4">
      <p class="text-sm text-on-surface">{{ t('about.disclaimer') }}</p>
    </div>
    <div class="mt-6 space-y-2 text-sm text-on-surface-muted">
      <p>{{ t('about.license') }}</p>
      <a
        href="https://github.com/choi12191995/PMP-super-mock"
        target="_blank"
        rel="noopener"
        class="text-primary hover:underline"
      >
        {{ t('about.github') }}
      </a>
    </div>
  </div>
</template>
