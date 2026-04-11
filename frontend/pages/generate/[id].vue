<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const api = useApiRequest()

const cvId = computed(() => route.params.id as string)

type CvData = {
  id: string
  vacancy_id: string
  md_content: string | null
  status: string
  include_header: boolean
  error_message: string | null
  download_url?: string | null
}

const cv = ref<CvData | null>(null)
const mdContent = ref('')
const loading = ref(true)
const converting = ref(false)
const conversionId = ref<string | null>(null)
const errorMessage = ref<string | null>(null)
let pollTimer: ReturnType<typeof setInterval> | null = null

async function load() {
  loading.value = true
  try {
    const data = await api<CvData>(`/api/generate/${cvId.value}`)
    cv.value = data
    mdContent.value = data.md_content || ''
  }
  catch {
    errorMessage.value = 'Could not load CV'
  }
  finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
  startStatusPoll()
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

function startStatusPoll() {
  pollTimer = setInterval(async () => {
    if (!cvId.value) return
    try {
      const data = await api<CvData>(`/api/generate/${cvId.value}`)
      cv.value = data
      if (data.md_content && !mdContent.value) {
        mdContent.value = data.md_content
      }
      if (data.status === 'draft' || data.status === 'completed' || data.status === 'failed') {
        if (pollTimer) clearInterval(pollTimer)
        pollTimer = null
      }
    }
    catch { /* ignore */ }
  }, 3000)
}

async function saveMd(content: string) {
  try {
    const form = new FormData()
    form.append('md_content', content)
    await api(`/api/generate/${cvId.value}`, { method: 'PUT', body: form })
  }
  catch {
    useToast().add({ title: 'Failed to save', color: 'red' })
  }
}

async function convertToPdf(includeHeader: boolean) {
  converting.value = true
  errorMessage.value = null
  try {
    const form = new FormData()
    form.append('include_header', String(includeHeader))
    const res = await api<{ conversion_id: string }>(`/api/generate/${cvId.value}/convert`, {
      method: 'POST',
      body: form,
    })
    conversionId.value = res.conversion_id
    if (cv.value) cv.value.status = 'converting'
    startConversionPoll()
  }
  catch (e: unknown) {
    const err = e as { data?: { detail?: string }; message?: string }
    errorMessage.value = err?.data?.detail || err?.message || 'Conversion failed'
    converting.value = false
  }
}

function startConversionPoll() {
  const timer = setInterval(async () => {
    if (!conversionId.value) { clearInterval(timer); return }
    try {
      const st = await api<{ status: string; download_url?: string }>(`/api/conversions/${conversionId.value}`)
      if (st.status === 'completed' && st.download_url) {
        if (cv.value) {
          cv.value.status = 'completed'
          cv.value.download_url = st.download_url
        }
        converting.value = false
        clearInterval(timer)
      }
      if (st.status === 'failed') {
        errorMessage.value = 'PDF conversion failed'
        converting.value = false
        if (cv.value) cv.value.status = 'draft'
        clearInterval(timer)
      }
    }
    catch {
      clearInterval(timer)
      converting.value = false
    }
  }, 2500)
}
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-3.5rem)]">
    <!-- Loading state -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <span class="text-sm text-cv-muted">Loading...</span>
    </div>

    <!-- Generating state (waiting for AI) -->
    <div
      v-else-if="cv && (cv.status === 'pending' || cv.status === 'generating')"
      class="flex-1 flex flex-col items-center justify-center gap-5 px-4"
    >
      <span class="inline-block w-10 h-10 border-3 border-cv-teal border-t-transparent rounded-full animate-spin" />
      <div class="text-center flex flex-col gap-2">
        <p class="text-lg font-bold text-cv-primary">
          Generating your CV...
        </p>
        <p class="text-sm text-cv-muted">
          AI is analyzing the vacancy and building a tailored CV. This usually takes 15–30 seconds.
        </p>
      </div>
      <button
        type="button"
        class="text-sm text-cv-muted hover:text-cv-body underline underline-offset-2 mt-4"
        @click="router.push('/generate-history')"
      >
        &larr; Back to Generated CVs
      </button>
    </div>

    <!-- Failed state -->
    <div
      v-else-if="cv && cv.status === 'failed'"
      class="flex-1 flex flex-col items-center justify-center gap-5 px-4"
    >
      <div class="max-w-md w-full rounded-xl border border-cv-error bg-cv-error-bg p-6 flex flex-col gap-4">
        <div class="flex items-center gap-3">
          <span class="text-2xl font-bold text-cv-error">&#10007;</span>
          <p class="text-base font-bold text-cv-body">
            Generation failed
          </p>
        </div>
        <p v-if="cv.error_message" class="text-sm text-cv-error">
          {{ cv.error_message }}
        </p>
        <div class="flex gap-3 mt-2">
          <NuxtLink
            to="/generate"
            class="h-10 px-5 inline-flex items-center justify-center rounded-lg bg-cv-teal text-white text-sm font-bold hover:brightness-95 transition-all"
          >
            Try Again
          </NuxtLink>
          <NuxtLink
            to="/generate-history"
            class="h-10 px-5 inline-flex items-center justify-center rounded-lg border border-cv-primary text-sm font-bold text-cv-primary hover:bg-cv-teal-subtle transition-colors"
          >
            Back to History
          </NuxtLink>
        </div>
      </div>
    </div>

    <!-- Error loading -->
    <div
      v-else-if="errorMessage && !cv"
      class="flex-1 flex items-center justify-center px-4"
    >
      <div class="max-w-md w-full text-center flex flex-col gap-4 items-center">
        <p class="text-base text-cv-error">
          {{ errorMessage }}
        </p>
        <NuxtLink
          to="/generate-history"
          class="text-sm font-bold text-cv-teal hover:underline underline-offset-2"
        >
          &larr; Back to Generated CVs
        </NuxtLink>
      </div>
    </div>

    <!-- Editor + Actions -->
    <template v-else-if="cv">
      <!-- Top bar -->
      <div class="flex items-center justify-between px-4 md:px-8 py-2 border-b border-cv-divider bg-cv-surface">
        <NuxtLink
          to="/generate-history"
          class="text-sm text-cv-muted hover:text-cv-body underline-offset-2 hover:underline"
        >
          &larr; Back
        </NuxtLink>
        <div class="flex items-center gap-3">
          <span
            v-if="cv.status === 'converting'"
            class="inline-flex items-center gap-1.5 rounded-full text-[11px] font-bold px-2.5 py-0.5 border bg-amber-50 text-amber-700 border-amber-200"
          >
            <span class="inline-block w-3 h-3 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
            Converting...
          </span>
          <span
            v-else-if="cv.status === 'completed'"
            class="inline-flex items-center rounded-full text-[11px] font-bold px-2.5 py-0.5 border bg-emerald-50 text-emerald-700 border-emerald-200"
          >
            &#10003; PDF Ready
          </span>
          <span
            v-else
            class="inline-flex items-center rounded-full text-[11px] font-bold px-2.5 py-0.5 border bg-sky-50 text-sky-700 border-sky-200"
          >
            Draft
          </span>
        </div>
      </div>

      <!-- Editor -->
      <div class="flex-1 min-h-0">
        <MdEditor
          v-model="mdContent"
          :readonly="cv.status === 'converting'"
          @save="saveMd"
        />
      </div>

      <!-- Bottom actions -->
      <div class="px-4 md:px-8 py-3 border-t border-cv-divider bg-cv-surface">
        <GeneratedCvResult
          :cv-id="cv.id"
          :status="cv.status"
          :error-message="errorMessage || cv.error_message"
          :download-url="cv.download_url"
          @convert="convertToPdf"
        />
      </div>
    </template>
  </div>
</template>
