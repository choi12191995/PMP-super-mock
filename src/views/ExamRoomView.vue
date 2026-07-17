<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 pb-24 pt-6">
    <h1 class="text-xl font-bold text-on-surface">{{ t('exam.question') }}</h1>
    <p class="mt-4 text-on-surface-muted">{{ t('common.loading') }}</p>
  </div>
</template>
