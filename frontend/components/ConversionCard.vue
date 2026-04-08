<script setup lang="ts">
const props = defineProps<{
  id: string
  filename: string
  status: 'completed' | 'processing' | 'failed' | 'pending'
  createdAt?: string
  serverError?: string
}>()

const apiRequest = useApiRequest()

const busy = ref(false)
const error = ref<string | null>(null)
const isConfirmModalOpen = ref(false)

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
    ? 'border-cv-divider border-l-cv-error'
    : 'border-cv-divider border-l-cv-teal',
)

async function download() {
  error.value = null
  busy.value = true
  try {
    const res = await apiRequest<{ download_url: string }>(
      `/api/history/${props.id}/download`,
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

function removeFromHistory() {
  error.value = null
  isConfirmModalOpen.value = true
}

async function confirmDelete() {
  isConfirmModalOpen.value = false
  busy.value = true
  try {
    await apiRequest(`/api/history/${props.id}`, { method: 'DELETE' })
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
    await apiRequest(`/api/regenerate/${props.id}`, { method: 'POST' })
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
    class="rounded-xl bg-cv-surface p-4 border border-l-[3px] flex flex-col gap-2"
    :class="cardBorderClass"
  >
    <div class="flex flex-wrap items-center gap-3">
      <div class="flex items-center gap-3 min-w-0 flex-1">
        <span
          class="text-2xl shrink-0 leading-none"
          aria-hidden="true"
        >📄</span>
        <div class="min-w-0">
          <p class="text-base font-bold truncate text-cv-body">
            {{ filename }}
          </p>
          <p
            v-if="dateLabel"
            class="text-[13px] text-cv-muted"
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
            class="!rounded-md h-8 px-4 text-xs font-bold !bg-cv-primary !text-white"
            @click="download"
          >
            Download PDF
          </UButton>
          <UButton
            v-if="status === 'failed'"
            variant="outline"
            size="sm"
            :loading="busy"
            class="!rounded-md h-8 px-4 text-xs font-bold !text-cv-primary border-cv-primary"
            @click="regenerate"
          >
            Retry
          </UButton>
          <UButton
            v-if="status !== 'failed'"
            variant="outline"
            size="sm"
            :loading="busy"
            class="!rounded-md h-8 px-4 text-xs font-bold !text-cv-primary border-cv-primary"
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
      class="text-xs text-cv-error"
    >
      {{ serverError }}
    </p>
    <p
      v-if="error"
      class="text-xs text-cv-error"
    >
      {{ error }}
    </p>
  </div>

  <!-- Delete confirmation modal -->
  <UModal v-model="isConfirmModalOpen">
    <UCard>
      <template #header>
        <p class="text-base font-bold text-cv-body">
          Remove from history?
        </p>
      </template>

      <p class="text-sm text-cv-body">
        Remove <span class="font-semibold">{{ filename }}</span> from your history? The PDF will be deleted from storage.
      </p>

      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton
            variant="outline"
            size="sm"
            class="!rounded-md h-8 px-4 text-xs font-bold"
            @click="isConfirmModalOpen = false"
          >
            Cancel
          </UButton>
          <UButton
            size="sm"
            color="red"
            class="!rounded-md h-8 px-4 text-xs font-bold"
            @click="confirmDelete"
          >
            Delete
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>
