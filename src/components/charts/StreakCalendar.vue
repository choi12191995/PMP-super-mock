<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

export interface DailyDataPoint {
  date: string
  answered: number
}

const props = defineProps<{
  dailyData: DailyDataPoint[]
}>()

const { t } = useI18n()

const WEEKS = 26

const dataMap = computed(() => {
  const map = new Map<string, number>()
  for (const d of props.dailyData) {
    map.set(d.date, d.answered)
  }
  return map
})

const grid = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const start = new Date(today)
  start.setDate(start.getDate() - WEEKS * 7 + 1)

  const cells: { date: string; count: number; day: number }[] = []
  const cursor = new Date(start)

  while (cursor <= today) {
    const date = cursor.toISOString().slice(0, 10)
    cells.push({
      date,
      count: dataMap.value.get(date) ?? 0,
      day: cursor.getDay(),
    })
    cursor.setDate(cursor.getDate() + 1)
  }

  return cells
})

function level(count: number): string {
  if (count === 0) return 'bg-border/30'
  if (count <= 5) return 'bg-primary/30'
  if (count <= 15) return 'bg-primary/55'
  if (count <= 30) return 'bg-primary/75'
  return 'bg-primary'
}

function cellTitle(date: string, count: number): string {
  return count === 0
    ? t('dashboard.streakNoActivity', { date })
    : t('dashboard.streakAnswered', { date, count })
}
</script>

<template>
  <div class="overflow-x-auto">
    <div
      class="inline-grid gap-[3px]"
      style="grid-template-rows: repeat(7, 12px); grid-auto-flow: column; grid-auto-columns: 12px"
    >
      <div
        v-for="cell in grid"
        :key="cell.date"
        class="rounded-sm transition"
        :class="level(cell.count)"
        :title="cellTitle(cell.date, cell.count)"
      />
    </div>
  </div>
</template>
