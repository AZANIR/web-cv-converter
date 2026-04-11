<script setup lang="ts">
definePageMeta({ middleware: ['auth'] })

type Row = {
  id: string
  original_filename: string
  status: string
  created_at?: string
  error_message?: string
}

const api = useApiRequest()
const items = ref<Row[]>([])
const loading = ref(true)
const pollingIds = ref<Set<string>>(new Set())
let timers: Record<string, ReturnType<typeof setTimeout>> = {}

const POLL_BASE_MS = 2000
const POLL_MAX_MS = 30000
const POLL_MAX_ATTEMPTS = 30

async function load() {
  loading.value = true
  try {
    const res = await api<{ items: Row[] }>('/api/history')
    items.value = res.items || []
    for (const row of items.value) {
      if (row.status === 'pending' || row.status === 'processing') {
        startRowPoll(row.id)
      }
    }
  }
  finally {
    loading.value = false
  }
}

onMounted(() => load())
onUnmounted(() => {
  Object.values(timers).forEach(clearTimeout)
  timers = {}
})

function mapStatus(s: string): 'completed' | 'processing' | 'failed' | 'pending' {
  if (s === 'completed' || s === 'processing' || s === 'failed' || s === 'pending') {
    return s
  }
  return 'pending'
}

function startRowPoll(id: string) {
  if (timers[id]) {
    return
  }
  pollingIds.value.add(id)
  pollWithBackoff(id, 0)
}

function pollWithBackoff(id: string, attempt: number) {
  if (attempt >= POLL_MAX_ATTEMPTS) {
    const idx = items.value.findIndex((r) => r.id === id)
    if (idx >= 0) {
      items.value[idx] = { ...items.value[idx], status: 'failed' }
    }
    delete timers[id]
    pollingIds.value.delete(id)
    return
  }

  const delay = Math.min(POLL_BASE_MS * Math.pow(2, attempt), POLL_MAX_MS)

  timers[id] = setTimeout(async () => {
    try {
      const st = await api<{ status: string }>(`/api/conversions/${id}`)
      const idx = items.value.findIndex((r) => r.id === id)
      if (idx >= 0) {
        items.value[idx] = { ...items.value[idx], status: st.status }
      }
      if (st.status === 'completed' || st.status === 'failed') {
        delete timers[id]
        pollingIds.value.delete(id)
      }
      else {
        pollWithBackoff(id, attempt + 1)
      }
    }
    catch {
      delete timers[id]
      pollingIds.value.delete(id)
    }
  }, delay)
}

async function onRegenerate(id: string) {
  const idx = items.value.findIndex((r) => r.id === id)
  if (idx >= 0) {
    items.value[idx] = { ...items.value[idx], status: 'pending' }
  }
  startRowPoll(id)
  await load()
}

function onDeleted(id: string) {
  items.value = items.value.filter((r) => r.id !== id)
  if (timers[id]) {
    clearTimeout(timers[id])
    delete timers[id]
  }
  pollingIds.value.delete(id)
}

const clearOpen = ref(false)
const clearing = ref(false)

async function confirmClearAll() {
  clearing.value = true
  try {
    await api('/api/history', { method: 'DELETE' })
    Object.values(timers).forEach(clearTimeout)
    timers = {}
    pollingIds.value.clear()
    items.value = []
    clearOpen.value = false
  }
  catch (e: unknown) {
    const err = e as { data?: { detail?: string }; message?: string }
    alert(err?.data?.detail || err?.message || 'Could not clear history')
  }
  finally {
    clearing.value = false
  }
}
</script>

<template>
  <div class="max-w-[800px] mx-auto px-4 md:px-8 py-10 space-y-6">
    <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div class="flex flex-col gap-1">
        <h1 class="text-[1.75rem] font-bold text-cv-primary leading-tight">
          Conversion History
        </h1>
        <p class="text-base text-cv-muted">
          Your past CV conversions
        </p>
      </div>
      <UButton
        v-if="items.length"
        variant="outline"
        color="red"
        class="shrink-0 self-start"
        @click="clearOpen = true"
      >
        Clear all history
      </UButton>
    </div>

    <div
      v-if="loading"
      class="space-y-3"
    >
      <USkeleton class="h-24 w-full rounded-lg" />
      <USkeleton class="h-24 w-full rounded-lg" />
    </div>

    <div
      v-else-if="!items.length"
      class="rounded-2xl border border-cv-teal bg-cv-teal-subtle p-12 flex flex-col items-center gap-4 text-center max-w-[400px] mx-auto"
    >
      <span
        class="text-[3rem] leading-none text-cv-body"
        aria-hidden="true"
      >📭</span>
      <p class="text-cv-body text-lg font-bold">
        No conversions yet
      </p>
      <p class="text-sm text-cv-muted max-w-[300px]">
        Upload your first CV to get started
      </p>
      <NuxtLink
        to="/dashboard"
        class="mt-2 h-10 w-[200px] rounded-lg bg-cv-teal text-white text-sm font-bold flex items-center justify-center hover:brightness-95 transition-[filter]"
      >
        Go to Dashboard →
      </NuxtLink>
    </div>

    <div
      v-else
      class="space-y-3"
    >
      <ConversionCard
        v-for="row in items"
        :key="row.id"
        :id="row.id"
        :filename="row.original_filename"
        :status="mapStatus(row.status)"
        :created-at="row.created_at"
        :server-error="row.error_message"
        @regenerate="onRegenerate"
        @deleted="onDeleted"
      />
    </div>

    <UModal
      v-model="clearOpen"
      :ui="{ width: 'sm:max-w-md' }"
    >
      <div class="p-6 space-y-4 w-full max-w-[420px]">
        <h2 class="text-lg font-semibold text-cv-primary">
          Clear all history
        </h2>
        <p class="text-sm text-cv-body">
          This removes every conversion and deletes stored PDFs for your account. This cannot be undone.
        </p>
        <div class="flex justify-end gap-2 pt-2">
          <UButton
            variant="ghost"
            @click="clearOpen = false"
          >
            Cancel
          </UButton>
          <UButton
            color="red"
            :loading="clearing"
            @click="confirmClearAll"
          >
            Clear all
          </UButton>
        </div>
      </div>
    </UModal>
  </div>
</template>
