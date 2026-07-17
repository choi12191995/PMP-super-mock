<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { chartColors } from './chartTheme'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
)

export interface ScoreTrendPoint {
  date: string
  score: number
}

const props = withDefaults(
  defineProps<{
    data: ScoreTrendPoint[]
    passLine?: number
  }>(),
  { passLine: 65 },
)

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

const chartData = computed(() => ({
  labels: props.data.map((d) => d.date),
  datasets: [
    {
      label: 'Score',
      data: props.data.map((d) => d.score),
      borderColor: colors.value.primary,
      backgroundColor: `${colors.value.primary}33`,
      fill: true,
      tension: 0.3,
      pointRadius: 4,
      pointHoverRadius: 6,
    },
    {
      label: 'Pass proxy',
      data: props.data.map(() => props.passLine),
      borderColor: colors.value.warning,
      borderDash: [6, 4],
      pointRadius: 0,
      fill: false,
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
    x: {
      ticks: { color: colors.value.text, maxRotation: 45 },
      grid: { color: colors.value.grid },
    },
    y: {
      min: 0,
      max: 100,
      ticks: { color: colors.value.text, callback: (v: number | string) => `${v}%` },
      grid: { color: colors.value.grid },
    },
  },
}))
</script>

<template>
  <div class="h-56 w-full">
    <Line v-if="data.length > 0" :data="chartData" :options="chartOptions" />
    <p v-else class="flex h-full items-center justify-center text-sm text-on-surface-muted">
      —
    </p>
  </div>
</template>
