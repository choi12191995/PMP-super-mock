<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 pb-24 pt-6">
    <h1 class="mb-6 text-2xl font-bold text-on-surface">{{ t('mode.title') }}</h1>
    <div class="space-y-4">
      <div class="rounded-2xl border border-border bg-surface-raised p-5 transition hover:border-primary">
        <h2 class="text-lg font-semibold text-on-surface">{{ t('mode.realExam') }}</h2>
        <p class="mt-1 text-sm text-on-surface-muted">{{ t('mode.realExamDesc') }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-surface-raised p-5 transition hover:border-primary">
        <h2 class="text-lg font-semibold text-on-surface">{{ t('mode.fullUntimed') }}</h2>
        <p class="mt-1 text-sm text-on-surface-muted">{{ t('mode.fullUntimedDesc') }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-surface-raised p-5 transition hover:border-primary">
        <h2 class="text-lg font-semibold text-on-surface">{{ t('mode.free') }}</h2>
        <p class="mt-1 text-sm text-on-surface-muted">{{ t('mode.freeDesc') }}</p>
      </div>
      <div class="rounded-2xl border border-border bg-surface-raised p-5 transition hover:border-primary">
        <h2 class="text-lg font-semibold text-on-surface">{{ t('mode.custom') }}</h2>
        <p class="mt-1 text-sm text-on-surface-muted">{{ t('mode.customDesc') }}</p>
      </div>
    </div>
  </div>
</template>
