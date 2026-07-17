<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '@/stores/settings'
import { useAiStore } from '@/stores/ai'
import { exportData, importData, downloadJson } from '@/db/exportImport'
import { warmQuestionBankCache, isBankCached } from '@/core/bank/warmCache'
import { loadManifest } from '@/core/bank/loader'

const { t } = useI18n()
const settings = useSettingsStore()
const ai = useAiStore()

const showKey = ref(false)
const testing = ref(false)
const testResult = ref<{ ok: boolean; message: string } | null>(null)
const fetchingModels = ref(false)
const modelsError = ref<string | null>(null)
const includeApiKey = ref(false)
const backupStatus = ref<string | null>(null)
const bankVersion = ref('')
const bankCached = ref(false)
const downloading = ref(false)
const downloadPct = ref(0)
const downloadError = ref<string | null>(null)

function persistAi(): void {
  ai.saveConfig()
}

onMounted(async () => {
  try {
    const manifest = await loadManifest()
    bankVersion.value = manifest.version
  } catch {
    bankVersion.value = '—'
  }
  bankCached.value = await isBankCached()
})

async function onTestConnection(): Promise<void> {
  testing.value = true
  testResult.value = null
  ai.saveConfig()
  const result = await ai.runTestConnection()
  testResult.value = {
    ok: result.ok,
    message: result.ok ? t('settings.testSuccess') : t('settings.testFailed', { error: result.error }),
  }
  testing.value = false
}

async function onFetchModels(): Promise<void> {
  fetchingModels.value = true
  modelsError.value = null
  ai.saveConfig()
  try {
    const models = await ai.loadModels()
    if (models.length && !models.includes(ai.model)) {
      ai.model = models[0]
    }
    persistAi()
  } catch (err) {
    modelsError.value = err instanceof Error ? err.message : String(err)
  } finally {
    fetchingModels.value = false
  }
}

async function onBackup(): Promise<void> {
  backupStatus.value = null
  try {
    const data = await exportData(includeApiKey.value)
    downloadJson(data, `pmp-super-mock-backup-${new Date().toISOString().slice(0, 10)}.json`)
    backupStatus.value = t('settings.backupSuccess')
  } catch (err) {
    backupStatus.value = err instanceof Error ? err.message : String(err)
  }
}

async function onRestore(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  backupStatus.value = null
  try {
    const text = await file.text()
    const data = JSON.parse(text)
    await importData(data)
    backupStatus.value = t('settings.restoreSuccess')
  } catch (err) {
    backupStatus.value = err instanceof Error ? err.message : String(err)
  }
  input.value = ''
}

async function onDownloadBank(): Promise<void> {
  downloading.value = true
  downloadError.value = null
  downloadPct.value = 0
  try {
    await warmQuestionBankCache((p) => {
      downloadPct.value = p.pct
    })
    bankCached.value = true
  } catch (err) {
    downloadError.value = err instanceof Error ? err.message : String(err)
  } finally {
    downloading.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 pb-24 pt-6">
    <h1 class="mb-6 text-2xl font-bold text-on-surface">{{ t('settings.title') }}</h1>

    <section class="mb-6">
      <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-on-surface-muted">
        {{ t('settings.appearance') }}
      </h2>
      <div class="space-y-3">
        <div class="flex items-center justify-between glass-card p-4">
          <span class="text-on-surface">{{ t('settings.theme') }}</span>
          <div class="flex gap-1">
            <button
              v-for="opt in (['light', 'dark', 'system'] as const)"
              :key="opt"
              class="rounded-lg px-3 py-1.5 text-sm transition"
              :class="settings.theme === opt ? 'bg-primary text-white' : 'text-on-surface-muted hover:bg-surface-alt'"
              @click="settings.setTheme(opt)"
            >
              {{ t(`settings.theme${opt.charAt(0).toUpperCase() + opt.slice(1)}`) }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="mb-6">
      <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-on-surface-muted">
        {{ t('settings.exam') }}
      </h2>
      <div class="space-y-3 glass-card p-4">
        <div>
          <label class="mb-1 block text-sm font-medium text-on-surface">{{ t('settings.examDate') }}</label>
          <input
            :value="settings.examDate ?? ''"
            type="date"
            class="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-on-surface outline-none focus:border-primary"
            @input="settings.setExamDate(($event.target as HTMLInputElement).value || null)"
          />
        </div>
        <label class="flex cursor-pointer items-center gap-3">
          <input
            :checked="settings.sounds"
            type="checkbox"
            class="h-5 w-5 accent-primary"
            @change="settings.toggleSounds()"
          />
          <span class="text-sm text-on-surface">{{ t('settings.sounds') }}</span>
        </label>
        <label class="flex cursor-pointer items-center gap-3">
          <input
            :checked="settings.haptics"
            type="checkbox"
            class="h-5 w-5 accent-primary"
            @change="settings.toggleHaptics()"
          />
          <span class="text-sm text-on-surface">{{ t('settings.haptics') }}</span>
        </label>
        <label class="flex cursor-pointer items-center gap-3">
          <input
            :checked="settings.swipeNav"
            type="checkbox"
            class="h-5 w-5 accent-primary"
            @change="settings.toggleSwipeNav()"
          />
          <span class="text-sm text-on-surface">{{ t('settings.swipeNav') }}</span>
        </label>
      </div>
    </section>

    <section class="mb-6">
      <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-on-surface-muted">
        {{ t('settings.ai') }}
      </h2>
      <div class="space-y-4 glass-card p-4">
        <label class="flex cursor-pointer items-center gap-3">
          <input
            v-model="ai.enabled"
            type="checkbox"
            class="h-5 w-5 accent-primary"
            @change="persistAi"
          />
          <span class="text-sm font-medium text-on-surface">{{ t('settings.aiEnable') }}</span>
        </label>

        <div>
          <label class="mb-1 block text-sm font-medium text-on-surface">{{ t('settings.aiEndpoint') }}</label>
          <input
            v-model="ai.baseURL"
            type="url"
            placeholder="https://api.openai.com/v1"
            class="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-on-surface outline-none focus:border-primary"
            @change="persistAi"
          />
        </div>

        <div>
          <label class="mb-1 block text-sm font-medium text-on-surface">{{ t('settings.aiKey') }}</label>
          <div class="relative">
            <input
              v-model="ai.apiKey"
              :type="showKey ? 'text' : 'password'"
              autocomplete="off"
              class="w-full rounded-xl border border-border bg-surface px-3 py-2 pr-16 text-sm text-on-surface outline-none focus:border-primary"
              @change="persistAi"
            />
            <button
              type="button"
              class="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg px-2 py-1 text-xs text-on-surface-muted hover:bg-surface-alt"
              @click="showKey = !showKey"
            >
              {{ showKey ? 'Hide' : 'Show' }}
            </button>
          </div>
          <p class="mt-1 text-xs text-warning">{{ t('settings.aiKeyWarning') }}</p>
        </div>

        <div>
          <label class="mb-1 block text-sm font-medium text-on-surface">{{ t('settings.aiModel') }}</label>
          <div class="flex gap-2">
            <input
              v-model="ai.model"
              type="text"
              placeholder="gpt-4o-mini"
              class="min-h-[44px] flex-1 rounded-xl border border-border bg-surface px-3 py-2 text-sm text-on-surface outline-none focus:border-primary"
              @change="persistAi"
            />
            <button
              type="button"
              class="shrink-0 rounded-xl border border-border px-4 py-2 text-sm font-medium text-on-surface transition hover:border-primary disabled:opacity-50"
              :disabled="fetchingModels || !ai.isConfigured"
              @click="onFetchModels"
            >
              {{ fetchingModels ? t('common.loading') : t('settings.fetchModels') }}
            </button>
          </div>
          <p v-if="modelsError" class="mt-1 text-xs text-danger">{{ modelsError }}</p>
        </div>

        <div>
          <label class="mb-1 block text-sm font-medium text-on-surface">
            {{ t('settings.aiTemp') }}: {{ ai.temperature.toFixed(1) }}
          </label>
          <input
            v-model.number="ai.temperature"
            type="range"
            min="0"
            max="2"
            step="0.1"
            class="w-full accent-primary"
            @change="persistAi"
          />
        </div>

        <div>
          <label class="mb-1 block text-sm font-medium text-on-surface">{{ t('settings.aiLang') }}</label>
          <select
            v-model="ai.replyLanguage"
            class="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm text-on-surface outline-none focus:border-primary"
            @change="persistAi"
          >
            <option value="auto">{{ t('settings.aiLangAuto') }}</option>
            <option value="en">English</option>
            <option value="zh-TW">繁體中文</option>
          </select>
        </div>

        <div>
          <button
            type="button"
            class="rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary-dark disabled:opacity-50"
            :disabled="testing || !ai.isConfigured"
            @click="onTestConnection"
          >
            {{ testing ? t('common.loading') : t('settings.testConnection') }}
          </button>
          <p
            v-if="testResult"
            class="mt-2 text-sm"
            :class="testResult.ok ? 'text-success' : 'text-danger'"
          >
            {{ testResult.message }}
          </p>
        </div>
      </div>
    </section>

    <section class="mb-6">
      <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-on-surface-muted">
        {{ t('settings.data') }}
      </h2>
      <div class="space-y-3">
        <div class="glass-card p-4">
          <p class="font-medium text-on-surface">{{ t('settings.backup') }}</p>
          <p class="mb-3 text-sm text-on-surface-muted">{{ t('settings.backupDesc') }}</p>
          <label class="mb-3 flex cursor-pointer items-center gap-2">
            <input v-model="includeApiKey" type="checkbox" class="h-4 w-4 accent-primary" />
            <span class="text-sm text-on-surface-muted">{{ t('settings.includeApiKey') }}</span>
          </label>
          <button
            type="button"
            class="rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary-dark"
            @click="onBackup"
          >
            {{ t('settings.backup') }}
          </button>
        </div>
        <div class="glass-card p-4">
          <p class="font-medium text-on-surface">{{ t('settings.restore') }}</p>
          <p class="mb-3 text-sm text-on-surface-muted">{{ t('settings.restoreDesc') }}</p>
          <label class="inline-block cursor-pointer rounded-xl border border-border px-4 py-2 text-sm font-medium text-on-surface transition hover:border-primary">
            {{ t('settings.restore') }}
            <input type="file" accept="application/json,.json" class="hidden" @change="onRestore" />
          </label>
        </div>
        <div class="glass-card p-4">
          <p class="font-medium text-on-surface">{{ t('settings.downloadOffline') }}</p>
          <p class="mb-1 text-sm text-on-surface-muted">
            {{ t('settings.bankVersion') }}: {{ bankVersion }}
          </p>
          <p v-if="bankCached" class="mb-3 text-sm text-success">{{ t('settings.downloadDone') }}</p>
          <button
            type="button"
            class="rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-primary-dark disabled:opacity-50"
            :disabled="downloading"
            @click="onDownloadBank"
          >
            {{ downloading ? t('settings.downloadProgress', { pct: downloadPct }) : t('settings.downloadOffline') }}
          </button>
          <div v-if="downloading" class="mt-2 h-2 overflow-hidden rounded-full bg-surface-alt">
            <div class="h-full bg-primary transition-all" :style="{ width: `${downloadPct}%` }" />
          </div>
          <p v-if="downloadError" class="mt-2 text-sm text-danger">{{ downloadError }}</p>
        </div>
        <p v-if="backupStatus" class="text-sm text-on-surface-muted">{{ backupStatus }}</p>
      </div>
    </section>
  </div>
</template>
