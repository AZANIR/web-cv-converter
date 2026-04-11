<script setup lang="ts">
definePageMeta({ middleware: ['auth'] })

const api = useApiRequest()
const router = useRouter()
const toast = useToast()
const { statusLabel, statusClasses } = useStatusDisplay()

type HistoryItem = {
  id: string
  vacancy_id: string
  status: string
  pdf_filename: string | null
  created_at: string
  error_message: string | null
  vacancy_title: string
  input_type: string | null
}

const items = ref<HistoryItem[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const res = await api<{ items: HistoryItem[] }>('/api/generate/history')
    items.value = res.items
  }
  catch {
    error.value = 'Failed to load generated CV history. Please try again.'
  }
  finally {
    loading.value = false
  }
})

function formatDate(iso: string) {
  return new Date(iso).toLocaleString()
}

async function deleteCv(id: string) {
  try {
    await api(`/api/generate/${id}`, { method: 'DELETE' })
    items.value = items.value.filter(i => i.id !== id)
  }
  catch {
    toast.add({
      title: 'Delete failed',
      description: 'Could not delete the generated CV. Please try again.',
      color: 'red',
    })
  }
}
</script>

<template>
  <div class="max-w-[960px] mx-auto px-4 md:px-8 py-6 md:py-10 flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold text-cv-primary">
        Generated CVs
      </h1>
      <NuxtLink
        to="/generate"
        class="h-9 px-4 inline-flex items-center gap-1.5 rounded-lg bg-cv-teal text-white text-sm font-bold hover:brightness-95 transition-all"
      >
        + New CV
      </NuxtLink>
    </div>

    <UAlert
      v-if="error"
      color="red"
      variant="soft"
      :title="error"
      icon="i-heroicons-exclamation-circle"
      class="rounded-xl"
    />

    <div v-if="loading" class="text-sm text-cv-muted">
      Loading...
    </div>
    <div v-else-if="items.length === 0" class="rounded-xl border border-dashed border-cv-divider p-10 text-center flex flex-col gap-3 items-center">
      <p class="text-base text-cv-muted">
        No generated CVs yet
      </p>
      <NuxtLink
        to="/generate"
        class="text-sm font-bold text-cv-teal hover:underline underline-offset-2"
      >
        Generate your first CV &rarr;
      </NuxtLink>
    </div>

    <div v-else class="flex flex-col gap-3">
      <div
        v-for="item in items"
        :key="item.id"
        class="rounded-xl border border-cv-divider bg-cv-surface px-5 py-4 flex items-center justify-between gap-4 hover:shadow-sm transition-shadow"
      >
        <div class="flex flex-col gap-1.5 min-w-0 flex-1">
          <span class="text-sm font-bold text-cv-body truncate">
            {{ item.vacancy_title || 'Untitled' }}
          </span>
          <div class="flex items-center gap-3 flex-wrap">
            <span
              class="inline-flex items-center rounded-full text-[11px] font-bold px-2.5 py-0.5 border"
              :class="statusClasses(item.status)"
            >
              {{ statusLabel(item.status) }}
            </span>
            <span class="text-xs text-cv-muted">{{ formatDate(item.created_at) }}</span>
          </div>
        </div>

        <div class="flex items-center gap-2 shrink-0">
          <button
            v-if="item.status === 'draft' || item.status === 'completed'"
            type="button"
            class="h-8 px-4 rounded-lg border border-cv-primary text-xs font-bold text-cv-primary hover:bg-cv-teal-subtle transition-colors"
            @click="router.push(`/generate/${item.id}`)"
          >
            {{ item.status === 'draft' ? 'Edit' : 'View' }}
          </button>
          <button
            v-if="item.status === 'pending' || item.status === 'generating'"
            type="button"
            class="h-8 px-4 rounded-lg border border-amber-300 text-xs font-bold text-amber-700 bg-amber-50 cursor-default"
            disabled
          >
            <span class="inline-block w-3 h-3 border-2 border-amber-500 border-t-transparent rounded-full animate-spin mr-1.5 align-middle" />
            Generating...
          </button>
          <button
            type="button"
            class="h-8 px-3 rounded-lg text-xs text-cv-error hover:bg-red-50 transition-colors"
            @click="deleteCv(item.id)"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
