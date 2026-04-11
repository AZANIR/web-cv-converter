<script setup lang="ts">
const api = useApiRequest()

const fileInput = ref<HTMLInputElement | null>(null)
const file = ref<File | null>(null)
const dragOver = ref(false)
const includeHeader = ref(true)
const conversionId = ref<string | null>(null)
const remoteStatus = ref<string | null>(null)
const errorMessage = ref<string | null>(null)
const downloadUrl = ref<string | null>(null)
let pollTimer: ReturnType<typeof setInterval> | null = null

function stopPoll() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

onUnmounted(() => stopPoll())

function formatBytes(n: number) {
  if (n < 1024) {
    return `${n} B`
  }
  if (n < 1024 * 1024) {
    return `${(n / 1024).toFixed(1)} KB`
  }
  return `${(n / 1024 / 1024).toFixed(1)} MB`
}

function setFile(f: File | null) {
  if (!f) {
    file.value = null
    return
  }
  if (!f.name.toLowerCase().endsWith('.md')) {
    errorMessage.value = 'Please choose a .md file'
    return
  }
  errorMessage.value = null
  file.value = f
  conversionId.value = null
  remoteStatus.value = null
  downloadUrl.value = null
  stopPoll()
}

function resetConversion() {
  setFile(null)
  conversionId.value = null
  remoteStatus.value = null
  downloadUrl.value = null
  errorMessage.value = null
  stopPoll()
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) {
    setFile(f)
  }
}

async function convert() {
  if (!file.value) {
    return
  }
  errorMessage.value = null
  downloadUrl.value = null
  remoteStatus.value = null

  const form = new FormData()
  form.append('file', file.value)
  form.append('include_header', String(includeHeader.value))
  try {
    const res = await api<{ conversion_id: string }>('/api/convert', {
      method: 'POST',
      body: form,
    })
    conversionId.value = res.conversion_id
    remoteStatus.value = 'pending'
    startPoll()
  }
  catch (e: unknown) {
    remoteStatus.value = null
    const err = e as { data?: { detail?: string }; message?: string }
    errorMessage.value = err?.data?.detail || err?.message || 'Upload failed'
  }
}

function startPoll() {
  stopPoll()
  pollTimer = setInterval(async () => {
    if (!conversionId.value) {
      return
    }
    try {
      const st = await api<{
        status: string
        download_url?: string
        error_message?: string
      }>(`/api/conversions/${conversionId.value}`)
      remoteStatus.value = st.status
      if (st.status === 'completed' && st.download_url) {
        downloadUrl.value = st.download_url
        stopPoll()
      }
      if (st.status === 'failed') {
        errorMessage.value = st.error_message || 'Conversion failed'
        stopPoll()
      }
    }
    catch {
      stopPoll()
      errorMessage.value = 'Lost connection while checking status'
    }
  }, 2000)
}

const ctaDisabled = computed(() => {
  if (!file.value) {
    return true
  }
  if (remoteStatus.value === 'pending' || remoteStatus.value === 'processing') {
    return true
  }
  return false
})

const ctaBusy = computed(
  () => remoteStatus.value === 'pending' || remoteStatus.value === 'processing',
)

const ctaLabel = computed(() => (ctaBusy.value ? 'Converting…' : 'Convert to PDF'))

const ctaOpacityClass = computed(() => {
  if (!file.value) {
    return 'opacity-40'
  }
  if (remoteStatus.value === 'processing') {
    return 'opacity-70'
  }
  return ''
})

async function retryConversion() {
  if (!file.value) {
    return
  }
  errorMessage.value = null
  await convert()
}
</script>

<template>
  <div
    class="w-full max-w-[640px] mx-auto flex flex-col gap-6 px-4 md:px-8"
    :class="conversionId && remoteStatus !== 'failed' ? 'py-10' : 'py-6 md:py-10'"
  >
    <div class="text-center flex flex-col gap-2">
      <h1 class="text-[1.75rem] leading-tight font-bold text-cv-primary">
        Convert Your CV
      </h1>
      <p class="text-base text-cv-muted">
        Upload a Markdown file to generate a professional PDF
      </p>
    </div>

    <input
      ref="fileInput"
      type="file"
      accept=".md,text/markdown"
      aria-label="Upload Markdown file"
      class="hidden"
      @change="(e) => setFile((e.target as HTMLInputElement).files?.[0] || null)"
    >

    <div
      v-if="!file"
      class="rounded-xl border-2 border-cv-teal bg-cv-teal-subtle p-12 flex flex-col items-center gap-3 text-center cursor-pointer transition-shadow"
      :class="dragOver ? 'ring-2 ring-cv-teal ring-offset-2' : ''"
      role="button"
      tabindex="0"
      aria-label="File upload area"
      @click="fileInput?.click()"
      @keydown.enter="fileInput?.click()"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="onDrop"
    >
      <span
        class="text-[3rem] leading-none text-cv-divider select-none"
        aria-hidden="true"
      >⬆</span>
      <p class="text-base text-cv-body">
        Drag &amp; drop your .md file here
      </p>
      <p class="text-sm font-normal text-cv-teal">
        or click to browse
      </p>
      <p class="text-xs text-cv-muted">
        Accepted: .md files up to 5 MB
      </p>
    </div>

    <div
      v-else
      class="rounded-xl border border-cv-teal bg-cv-surface py-4 px-6 flex items-center justify-between gap-3"
    >
      <div class="flex items-center gap-3 min-w-0">
        <span
          class="text-2xl shrink-0"
          aria-hidden="true"
        >📄</span>
        <div class="flex flex-col gap-0.5 min-w-0">
          <span class="text-sm font-bold truncate text-cv-body">{{ file.name }}</span>
          <span class="text-xs text-cv-muted">{{ formatBytes(file.size) }}</span>
        </div>
      </div>
      <button
        type="button"
        class="shrink-0 text-sm font-bold text-cv-error hover:underline underline-offset-2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cv-error"
        @click="setFile(null)"
      >
        Remove
      </button>
    </div>

    <div class="flex items-center justify-between rounded-lg border border-cv-divider bg-cv-surface px-4 py-3">
      <div class="flex flex-col gap-0.5">
        <span class="text-sm font-bold text-cv-body">Include header image</span>
        <span class="text-xs text-cv-muted">Add the company banner to the top of the PDF</span>
      </div>
      <button
        type="button"
        role="switch"
        :aria-checked="includeHeader"
        aria-label="Include header image"
        class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cv-teal"
        :class="includeHeader ? 'bg-cv-teal' : 'bg-cv-divider'"
        @click="includeHeader = !includeHeader"
      >
        <span
          class="pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform transition-transform"
          :class="includeHeader ? 'translate-x-5' : 'translate-x-0'"
        />
      </button>
    </div>

    <UButton
      block
      size="lg"
      class="h-12 justify-center !rounded-lg !bg-cv-teal !text-white hover:!brightness-95 disabled:!opacity-100"
      :class="ctaOpacityClass"
      :disabled="ctaDisabled"
      @click="convert"
    >
      {{ ctaLabel }}
    </UButton>

    <div
      v-if="conversionId && remoteStatus && remoteStatus !== 'failed' && remoteStatus !== 'completed'"
      class="flex flex-col gap-1 pl-2 w-full"
    >
      <div class="flex items-center gap-3">
        <span class="text-sm font-bold text-cv-success w-5 shrink-0">✓</span>
        <span class="text-sm text-cv-success">File uploaded</span>
      </div>
      <div class="flex pl-[7px]">
        <div
          class="w-px h-6 shrink-0"
          :class="remoteStatus === 'pending' ? 'bg-cv-divider' : 'bg-cv-success'"
        />
      </div>
      <div class="flex items-center gap-3">
        <span
          class="text-sm w-5 shrink-0 text-center font-bold"
          :class="remoteStatus === 'pending' ? 'text-cv-body' : 'text-cv-success'"
        >{{ remoteStatus === 'pending' ? '⟳' : '✓' }}</span>
        <span
          class="text-sm"
          :class="remoteStatus === 'pending' ? 'text-cv-body' : 'text-cv-success'"
        >{{ remoteStatus === 'pending' ? 'AI is parsing your CV…' : 'AI parsed your CV' }}</span>
      </div>
      <div class="flex pl-[7px]">
        <div
          class="w-px h-6 shrink-0"
          :class="remoteStatus === 'pending' ? 'bg-cv-divider' : 'bg-cv-success'"
        />
      </div>
      <div class="flex items-center gap-3">
        <span
          class="text-sm w-5 shrink-0 text-center font-bold"
          :class="remoteStatus === 'processing' ? 'text-cv-body' : remoteStatus === 'pending' ? 'text-cv-divider' : 'text-cv-success'"
        >{{ remoteStatus === 'pending' ? '○' : remoteStatus === 'processing' ? '⟳' : '✓' }}</span>
        <span
          class="text-sm"
          :class="remoteStatus === 'processing' ? 'text-cv-body' : remoteStatus === 'pending' ? 'text-cv-divider' : 'text-cv-success'"
        >{{ remoteStatus === 'processing' ? 'Generating PDF…' : 'Generating PDF' }}</span>
      </div>
      <div class="flex pl-[7px]">
        <div class="w-px h-6 bg-cv-divider shrink-0" />
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm w-5 shrink-0 text-center text-cv-divider">○</span>
        <span class="text-sm text-cv-divider">Ready to download</span>
      </div>
    </div>

    <div
      v-if="remoteStatus === 'completed' && downloadUrl"
      class="rounded-xl border border-cv-success bg-cv-success-bg p-6 flex flex-col gap-4"
    >
      <div class="flex items-center gap-3">
        <span class="text-xl font-bold text-cv-success">✓</span>
        <p class="text-base font-bold text-cv-body">
          Your PDF is ready!
        </p>
      </div>
      <div class="flex flex-col sm:flex-row gap-3">
        <UButton
          :to="downloadUrl"
          target="_blank"
          external
          class="h-10 justify-center !rounded-lg !bg-cv-teal !text-white text-sm font-bold px-6 flex-1"
        >
          Download PDF
        </UButton>
        <button
          type="button"
          class="h-10 rounded-lg border border-cv-primary text-sm font-bold text-cv-primary px-6 flex-1 hover:bg-cv-teal-subtle transition-colors"
          @click="resetConversion"
        >
          Convert Another
        </button>
      </div>
    </div>

    <div
      v-if="errorMessage"
      class="rounded-xl border border-cv-error bg-cv-error-bg p-6 flex flex-col gap-3"
    >
      <div class="flex items-center gap-3">
        <span class="text-xl font-bold text-cv-error">✕</span>
        <p class="text-base font-bold text-cv-body">
          Conversion failed
        </p>
      </div>
      <p class="text-sm text-cv-error">
        {{ errorMessage }}
      </p>
      <div class="flex flex-col sm:flex-row gap-3 pt-1">
        <UButton
          v-if="file"
          class="h-10 justify-center !rounded-lg !bg-cv-primary !text-white text-sm font-bold px-6 flex-1"
          @click="retryConversion"
        >
          Retry
        </UButton>
        <button
          type="button"
          class="h-10 rounded-lg border border-cv-primary text-sm font-bold text-cv-primary px-6 flex-1 hover:bg-white/80 transition-colors"
          @click="resetConversion"
        >
          Upload New File
        </button>
      </div>
    </div>
  </div>
</template>
