<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { useI18n } from 'vue-i18n'
import { chartColors } from './chartTheme'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

export interface DomainRadarPoint {
  domain: string
  latest: number
  best: number
  target: number
}

const props = defineProps<{
  data: DomainRadarPoint[]
}>()

const { t } = useI18n()
const colors = ref(chartColors())

onMounted(() => {
  colors.value = chartColors()
})

watch(
  () => document.documentElement.getAttribute('data-theme'),
  () => {
    colors.value = chartColors()
  },
)

function domainLabel(domain: string): string {
  const map: Record<string, string> = {
    people: t('common.people'),
    process: t('common.process'),
    business: t('common.business'),
  }
  return map[domain] ?? domain
}

const chartData = computed(() => ({
  labels: props.data.map((d) => domainLabel(d.domain)),
  datasets: [
    {
      label: t('dashboard.chartLatest'),
      data: props.data.map((d) => d.latest),
      borderColor: colors.value.primary,
      backgroundColor: `${colors.value.primary}44`,
      pointBackgroundColor: colors.value.primary,
    },
    {
      label: t('dashboard.chartBest'),
      data: props.data.map((d) => d.best),
      borderColor: colors.value.success,
      backgroundColor: `${colors.value.success}33`,
      pointBackgroundColor: colors.value.success,
    },
    {
      label: t('dashboard.chartTarget'),
      data: props.data.map((d) => d.target),
      borderColor: colors.value.warning,
      backgroundColor: 'transparent',
      borderDash: [4, 4],
      pointRadius: 0,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: colors.value.text },
    },
  },
  scales: {
    r: {
      min: 0,
      max: 100,
      ticks: {
        color: colors.value.text,
        stepSize: 25,
        backdropColor: 'transparent',
      },
      grid: { color: colors.value.grid },
      pointLabels: {
        color: colors.value.text,
        font: { size: 11 },
      },
    },
  },
}))
</script>

<template>
  <div class="h-64 w-full">
    <Radar v-if="data.length > 0" :data="chartData" :options="chartOptions" />
    <p v-else class="flex h-full items-center justify-center text-sm text-on-surface-muted">
      {{ t('common.noData') }}
    </p>
  </div>
</template>
