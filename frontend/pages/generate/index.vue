<script setup lang="ts">
definePageMeta({ middleware: ['auth'] })

const api = useApiRequest()
const router = useRouter()

const loading = ref(false)
const errorMessage = ref<string | null>(null)
const step = ref(0)
let stepTimer: ReturnType<typeof setInterval> | null = null

const steps = [
  'Parsing vacancy...',
  'Analyzing content with AI...',
  'Searching relevant case studies...',
  'Generating tailored CV...',
]

function startSteps() {
  step.value = 0
  stepTimer = setInterval(() => {
    if (step.value < steps.length - 1) {
      step.value++
    }
  }, 5000)
}

function stopSteps() {
  if (stepTimer) {
    clearInterval(stepTimer)
    stepTimer = null
  }
}

type VacancyInput = {
  type: 'text' | 'url' | 'file'
  text?: string
  url?: string
  file?: File
}

async function onSubmit(data: VacancyInput) {
  loading.value = true
  errorMessage.value = null
  startSteps()

  try {
    const form = new FormData()
    if (data.type === 'text' && data.text) {
      form.append('vacancy_text', data.text)
    }
    else if (data.type === 'url' && data.url) {
      form.append('vacancy_url', data.url)
    }
    else if (data.type === 'file' && data.file) {
      form.append('file', data.file)
    }

    const res = await api<{ vacancy_id: string; cv_id: string }>('/api/generate', {
      method: 'POST',
      body: form,
    })

    await router.push(`/generate/${res.cv_id}`)
  }
  catch (e: unknown) {
    const err = e as { data?: { detail?: string }; message?: string }
    errorMessage.value = err?.data?.detail || err?.message || 'Generation failed'
  }
  finally {
    loading.value = false
    stopSteps()
  }
}

onUnmounted(() => stopSteps())
</script>

<template>
  <div class="max-w-[640px] mx-auto px-4 md:px-8 py-6 md:py-10 flex flex-col gap-6">
    <div class="text-center flex flex-col gap-2">
      <h1 class="text-[1.75rem] leading-tight font-bold text-cv-primary">
        Generate CV
      </h1>
      <p class="text-base text-cv-muted">
        Paste a vacancy and get a tailored QA CV
      </p>
    </div>

    <VacancyInputForm :loading="loading" @submit="onSubmit" />

    <!-- Progress steps -->
    <div v-if="loading" class="rounded-xl border border-cv-teal bg-cv-teal-subtle p-6 flex flex-col gap-4">
      <div class="flex items-center gap-3">
        <span class="inline-block w-5 h-5 border-2 border-cv-teal border-t-transparent rounded-full animate-spin" />
        <p class="text-base font-bold text-cv-primary">
          Generating your CV...
        </p>
      </div>
      <div class="flex flex-col gap-2 pl-8">
        <div
          v-for="(label, i) in steps"
          :key="i"
          class="flex items-center gap-2 text-sm transition-colors"
          :class="i <= step ? 'text-cv-body' : 'text-cv-muted opacity-40'"
        >
          <span v-if="i < step" class="text-cv-teal font-bold">&#10003;</span>
          <span v-else-if="i === step" class="inline-block w-3 h-3 border-2 border-cv-teal border-t-transparent rounded-full animate-spin" />
          <span v-else class="w-3 h-3 rounded-full border border-cv-divider" />
          <span>{{ label }}</span>
        </div>
      </div>
      <p class="text-xs text-cv-muted pl-8">
        This usually takes 15–30 seconds
      </p>
    </div>

    <div
      v-if="errorMessage"
      class="rounded-xl border border-cv-error bg-cv-error-bg p-6 flex flex-col gap-3"
    >
      <div class="flex items-center gap-3">
        <span class="text-xl font-bold text-cv-error">&#10007;</span>
        <p class="text-base font-bold text-cv-body">
          Generation failed
        </p>
      </div>
      <p class="text-sm text-cv-error">
        {{ errorMessage }}
      </p>
    </div>
  </div>
</template>
