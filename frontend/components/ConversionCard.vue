<script setup lang="ts">
const props = defineProps<{
  id: string
  filename: string
  status: 'completed' | 'processing' | 'failed' | 'pending'
  createdAt?: string
  serverError?: string
}>()

const config = useRuntimeConfig()
const { session } = useUserSession()

function apiHeaders(): Record<string, string> {
  const token = session.value?.accessToken as string | undefined
  const idToken = session.value?.idToken as string | undefined
  const h: Record<string, string> = {}
  if (token) {
    h.Authorization = `Bearer ${token}`
  }
  if (idToken) {
    h['X-Auth0-ID-Token'] = idToken
  }
  return h
}

const busy = ref(false)
const error = ref<string | null>(null)

const dateLabel = computed(() => {
  if (!props.createdAt) {
    return ''
  }
  try {
    const d = new Date(props.createdAt)
    const datePart = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    const timePart = d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: false })
    return `${datePart} · ${timePart}`
  }
  catch {
    return props.createdAt
  }
})

const cardBorderClass = computed(() =>
  props.status === 'failed'
    ? 'border-[var(--cv-divider-gray)] border-l-[var(--cv-error-red)]'
    : 'border-[var(--cv-divider-gray)] border-l-[var(--cv-teal-accent)]',
)

async function download() {
  error.value = null
  busy.value = true
  try {
    const res = await $fetch<{ download_url: string }>(
      `${config.public.apiBase}/api/history/${props.id}/download`,
      { headers: apiHeaders() },
    )
    if (res.download_url) {
      window.open(res.download_url, '_blank')
    }
  }
  catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err?.data?.detail || 'Download failed'
  }
  finally {
    busy.value = false
  }
}

const emit = defineEmits<{ regenerate: [id: string]; deleted: [id: string] }>()

async function removeFromHistory() {
  error.value = null
  if (!confirm(`Remove "${props.filename}" from your history? The PDF will be deleted from storage.`)) {
    return
  }
  busy.value = true
  try {
    await $fetch(`${config.public.apiBase}/api/history/${props.id}`, {
      method: 'DELETE',
      headers: apiHeaders(),
    })
    emit('deleted', props.id)
  }
  catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err?.data?.detail || 'Delete failed'
  }
  finally {
    busy.value = false
  }
}

async function regenerate() {
  error.value = null
  busy.value = true
  try {
    await $fetch(`${config.public.apiBase}/api/regenerate/${props.id}`, {
      method: 'POST',
      headers: apiHeaders(),
    })
    emit('regenerate', props.id)
  }
  catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err?.data?.detail || 'Regenerate failed'
  }
  finally {
    busy.value = false
  }
}
</script>

<template>
  <div
    class="rounded-xl bg-[var(--cv-surface)] p-4 border border-l-[3px] flex flex-col gap-2"
    :class="cardBorderClass"
  >
    <div class="flex flex-wrap items-center gap-3">
      <div class="flex items-center gap-3 min-w-0 flex-1">
        <span
          class="text-2xl shrink-0 leading-none"
          aria-hidden="true"
        >📄</span>
        <div class="min-w-0">
          <p class="text-base font-bold truncate text-[var(--cv-body-text)]">
            {{ filename }}
          </p>
          <p
            v-if="dateLabel"
            class="text-[13px] text-[var(--cv-muted-text)]"
          >
            {{ dateLabel }}
          </p>
        </div>
      </div>
      <div class="flex flex-wrap items-center gap-3 sm:justify-end">
        <StatusBadge :status="status" />
        <div class="flex flex-wrap gap-2">
          <UButton
            v-if="status === 'completed'"
            size="sm"
            :loading="busy"
            class="!rounded-md h-8 px-4 text-xs font-bold !bg-[var(--cv-primary-dark)] !text-white"
            @click="download"
          >
            Download PDF
          </UButton>
          <UButton
            v-if="status === 'failed'"
            variant="outline"
            size="sm"
            :loading="busy"
            class="!rounded-md h-8 px-4 text-xs font-bold !text-[var(--cv-primary-dark)] border-[var(--cv-primary-dark)]"
            @click="regenerate"
          >
            Retry
          </UButton>
          <UButton
            v-if="status !== 'failed'"
            variant="outline"
            size="sm"
            :loading="busy"
            class="!rounded-md h-8 px-4 text-xs font-bold !text-[var(--cv-primary-dark)] border-[var(--cv-primary-dark)]"
            @click="regenerate"
          >
            Regenerate
          </UButton>
          <UButton
            variant="outline"
            size="sm"
            color="red"
            :loading="busy"
            class="!rounded-md h-8 px-4 text-xs font-bold"
            @click="removeFromHistory"
          >
            Delete
          </UButton>
        </div>
      </div>
    </div>
    <p
      v-if="serverError && status === 'failed'"
      class="text-xs text-[var(--cv-error-red)]"
    >
      {{ serverError }}
    </p>
    <p
      v-if="error"
      class="text-xs text-[var(--cv-error-red)]"
    >
      {{ error }}
    </p>
  </div>
</template>
