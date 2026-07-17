<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { Badge } from '@/core/badges'

defineProps<{
  badges: Badge[]
}>()

const { t } = useI18n()

const icons: Record<string, string> = {
  first180: '🎯',
  streak7: '🔥',
  businessPro: '💼',
  nightOwl: '🦉',
  perfectDomain: '⭐',
}
</script>

<template>
  <section v-if="badges.some((b) => b.earned)" class="mb-6">
    <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-on-surface-muted">
      {{ t('badges.title') }}
    </h2>
    <div class="flex flex-wrap gap-2">
      <div
        v-for="badge in badges.filter((b) => b.earned)"
        :key="badge.id"
        class="flex items-center gap-2 rounded-xl border border-border bg-surface-raised px-3 py-2"
        :title="t(`badges.${badge.id}`)"
      >
        <span class="text-lg">{{ icons[badge.id] ?? '🏅' }}</span>
        <span class="text-sm font-medium text-on-surface">{{ t(`badges.${badge.id}`) }}</span>
      </div>
    </div>
  </section>
</template>
