<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { db } from '@/db/index'

const { t } = useI18n()

const showHint = ref(false)
const deferredPrompt = ref<BeforeInstallPromptEvent | null>(null)

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

onMounted(async () => {
  const completedCount = await db.attempts
    .where('status')
    .equals('completed')
    .count()

  const dismissed = localStorage.getItem('installHintDismissed') === '1'
  const isStandalone =
    window.matchMedia('(display-mode: standalone)').matches ||
    (navigator as Navigator & { standalone?: boolean }).standalone === true

  if (completedCount >= 2 && !dismissed && !isStandalone) {
    showHint.value = true
  }

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferredPrompt.value = e as BeforeInstallPromptEvent
  })
})

async function install(): Promise<void> {
  if (deferredPrompt.value) {
    await deferredPrompt.value.prompt()
    await deferredPrompt.value.userChoice
    deferredPrompt.value = null
  }
  dismiss()
}

function dismiss(): void {
  showHint.value = false
  localStorage.setItem('installHintDismissed', '1')
}
</script>

<template>
  <Transition name="hint">
    <div
      v-if="showHint"
      class="glass-modal fixed bottom-24 left-4 right-4 z-40 mx-auto max-w-md p-4"
    >
      <p class="mb-3 text-sm text-on-surface">{{ t('install.hint') }}</p>
      <div class="flex gap-2">
        <button
          class="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition hover:bg-primary-dark"
          @click="install"
        >
          {{ t('common.install') }}
        </button>
        <button
          class="rounded-lg px-4 py-2 text-sm font-medium text-on-surface-muted transition hover:bg-surface-alt"
          @click="dismiss"
        >
          {{ t('install.dismiss') }}
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.hint-enter-active,
.hint-leave-active {
  transition: all 0.3s ease;
}
.hint-enter-from,
.hint-leave-to {
  opacity: 0;
  transform: translateY(1rem);
}
</style>
