<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { chartColors } from './chartTheme'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps<{
  labels: string[]
  values: number[]
  horizontal?: boolean
  color?: string
}>()

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

const barColor = computed(() => props.color ?? colors.value.primary)

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      data: props.values,
      backgroundColor: barColor.value,
      borderRadius: 4,
    },
  ],
}))

const chartOptions = computed(() => ({
  indexAxis: props.horizontal !== false ? ('y' as const) : ('x' as const),
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
  },
  scales: {
    x: {
      min: props.horizontal !== false ? 0 : undefined,
      max: props.horizontal !== false ? 100 : undefined,
      ticks: {
        color: colors.value.text,
        callback:
          props.horizontal !== false
            ? (v: number | string) => `${v}%`
            : undefined,
      },
      grid: { color: colors.value.grid },
    },
    y: {
      ticks: { color: colors.value.text, font: { size: 11 } },
      grid: { color: colors.value.grid },
    },
  },
}))
</script>

<template>
  <div class="h-64 w-full">
    <Bar v-if="labels.length > 0" :data="chartData" :options="chartOptions" />
    <p v-else class="flex h-full items-center justify-center text-sm text-on-surface-muted">
      —
    </p>
  </div>
</template>
