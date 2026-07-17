<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'
import type { HotspotQ, LText } from '@/core/types'

const props = defineProps<{
  question: HotspotQ
  modelValue: string[]
  showFeedback: boolean
  correctAnswer: string[]
  disabled: boolean
  lang: 'en' | 'zh-TW'
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

const { t } = useI18n()
const svgContainer = ref<HTMLElement | null>(null)
const svgHtml = ref('')
const regionStyles = ref<Record<string, { left: string; top: string; width: string; height: string }>>({})

function ltext(text: LText): string {
  return props.lang === 'zh-TW' ? text.zh : text.en
}

function isSelected(regionId: string): boolean {
  return props.modelValue.includes(regionId)
}

function isCorrectRegion(regionId: string): boolean {
  return props.showFeedback && props.correctAnswer.includes(regionId)
}

function isWrongRegion(regionId: string): boolean {
  return props.showFeedback && isSelected(regionId) && !props.correctAnswer.includes(regionId)
}

function regionClasses(regionId: string): string[] {
  const classes = [
    'absolute min-h-[44px] min-w-[44px] cursor-pointer rounded border-2 transition touch-manipulation',
  ]

  if (isCorrectRegion(regionId)) {
    classes.push('border-success bg-success/25')
  } else if (isWrongRegion(regionId)) {
    classes.push('border-danger bg-danger/25')
  } else if (isSelected(regionId)) {
    classes.push('border-primary bg-primary/20 ring-2 ring-primary/40')
  } else {
    classes.push('border-transparent bg-primary/5 hover:border-primary/50 hover:bg-primary/15')
  }

  if (props.disabled && !props.showFeedback) {
    classes.push('pointer-events-none opacity-70')
  }

  return classes
}

function toggleRegion(regionId: string): void {
  if (props.disabled) return

  const selected = isSelected(regionId)
  const next = selected
    ? props.modelValue.filter((id) => id !== regionId)
    : [...props.modelValue, regionId]

  emit('update:modelValue', next)
}

async function loadSvg(): Promise<void> {
  const res = await fetch(`/questions/media/${props.question.media}`)
  if (!res.ok) return
  const raw = await res.text()
  svgHtml.value = DOMPurify.sanitize(raw, { USE_PROFILES: { svg: true, svgFilters: true } })
  await nextTick()
  computeRegionPositions()
}

function computeRegionPositions(): void {
  const container = svgContainer.value
  if (!container) return

  const svg = container.querySelector('svg')
  if (!svg) return

  const viewBox = svg.viewBox.baseVal
  const positions: Record<string, { left: string; top: string; width: string; height: string }> = {}

  for (const region of props.question.regions) {
    const el = svg.querySelector(`#${CSS.escape(region.id)}`) as SVGGraphicsElement | null
    if (!el) continue

    let bbox: DOMRect
    try {
      bbox = el.getBBox()
    } catch {
      continue
    }

    positions[region.id] = {
      left: `${(bbox.x / viewBox.width) * 100}%`,
      top: `${(bbox.y / viewBox.height) * 100}%`,
      width: `${(bbox.width / viewBox.width) * 100}%`,
      height: `${(bbox.height / viewBox.height) * 100}%`,
    }
  }

  regionStyles.value = positions
}

watch(
  () => props.question.media,
  () => loadSvg(),
  { immediate: true },
)

onMounted(() => {
  window.addEventListener('resize', computeRegionPositions)
})

onUnmounted(() => {
  window.removeEventListener('resize', computeRegionPositions)
})

watch(svgHtml, () => nextTick(computeRegionPositions))
</script>

<template>
  <div class="space-y-5">
    <p
      class="inline-flex rounded-lg bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary"
    >
      {{ t('exam.hotspotInstruction') }}
    </p>

    <p class="text-base leading-relaxed text-on-surface whitespace-pre-wrap">
      {{ ltext(question.stem) }}
    </p>

    <div class="relative mx-auto max-w-lg overflow-hidden rounded-xl border border-border bg-surface-alt">
      <div ref="svgContainer" class="pointer-events-none w-full [&>svg]:h-auto [&>svg]:w-full" v-html="svgHtml" />

      <button
        v-for="region in question.regions"
        :key="region.id"
        type="button"
        :class="regionClasses(region.id)"
        :style="regionStyles[region.id]"
        :aria-label="ltext(region.label)"
        :aria-pressed="isSelected(region.id)"
        @click="toggleRegion(region.id)"
      />
    </div>

    <!-- Region legend for a11y / mobile fallback -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="region in question.regions"
        :key="'legend-' + region.id"
        type="button"
        class="min-h-[44px] rounded-lg border-2 px-3 py-2 text-sm transition touch-manipulation"
        :class="
          isCorrectRegion(region.id)
            ? 'border-success bg-success/10 text-success'
            : isWrongRegion(region.id)
              ? 'border-danger bg-danger/10 text-danger'
              : isSelected(region.id)
                ? 'border-primary bg-primary/5 text-primary'
                : 'border-border bg-surface-raised text-on-surface hover:border-primary/50'
        "
        :disabled="disabled && !showFeedback"
        @click="toggleRegion(region.id)"
      >
        {{ ltext(region.label) }}
      </button>
    </div>
  </div>
</template>
