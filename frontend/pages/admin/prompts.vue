<script setup lang="ts">
definePageMeta({ middleware: ['admin'] })

const api = useApiRequest()

type PromptItem = {
  id: string
  slug: string
  name: string
  description: string
  version: number
  updated_by: string | null
  updated_at: string | null
}

type PromptFull = PromptItem & { content: string }

const items = ref<PromptItem[]>([])
const loading = ref(true)
const editingSlug = ref<string | null>(null)
const editContent = ref('')
const saving = ref(false)
const currentPrompt = ref<PromptFull | null>(null)

onMounted(async () => {
  try {
    const res = await api<{ items: PromptItem[] }>('/api/prompts')
    items.value = res.items
  }
  catch { /* ignore */ }
  finally {
    loading.value = false
  }
})

async function openEditor(slug: string) {
  editingSlug.value = slug
  editContent.value = ''
  try {
    const data = await api<PromptFull>(`/api/prompts/${slug}`)
    currentPrompt.value = data
    editContent.value = data.content
  }
  catch { /* ignore */ }
}

function closeEditor() {
  editingSlug.value = null
  currentPrompt.value = null
}

async function savePrompt(content: string) {
  if (!editingSlug.value) return
  saving.value = true
  try {
    const updated = await api<PromptFull>(`/api/prompts/${editingSlug.value}`, {
      method: 'PUT',
      body: { content },
      headers: { 'Content-Type': 'application/json' },
    })
    if (currentPrompt.value) {
      currentPrompt.value.version = updated.version
    }
    const idx = items.value.findIndex(i => i.slug === editingSlug.value)
    if (idx >= 0 && updated) {
      items.value[idx] = { ...items.value[idx], version: updated.version, updated_at: updated.updated_at }
    }
  }
  catch { /* ignore */ }
  finally {
    saving.value = false
  }
}
</script>

<template>
  <div v-if="!editingSlug" class="max-w-[960px] mx-auto px-4 md:px-8 py-6 md:py-10 flex flex-col gap-6">
    <h1 class="text-xl font-bold text-[var(--cv-primary-dark)]">
      Prompts
    </h1>

    <div v-if="loading" class="text-sm text-[var(--cv-muted-text)]">
      Loading...
    </div>

    <div v-else class="flex flex-col gap-3">
      <div
        v-for="item in items"
        :key="item.slug"
        class="rounded-xl border border-[var(--cv-divider-gray)] bg-[var(--cv-surface)] px-5 py-4 flex items-center justify-between gap-4 cursor-pointer hover:shadow-sm transition-shadow"
        @click="openEditor(item.slug)"
      >
        <div class="flex flex-col gap-1 min-w-0">
          <span class="text-sm font-bold text-[var(--cv-body-text)]">{{ item.name }}</span>
          <span class="text-xs text-[var(--cv-muted-text)]">{{ item.slug }} &middot; v{{ item.version }}</span>
          <span v-if="item.description" class="text-xs text-[var(--cv-muted-text)]">{{ item.description }}</span>
        </div>
        <span class="text-sm font-bold text-[var(--cv-teal-accent)]">Edit</span>
      </div>
    </div>
  </div>

  <!-- Full-screen editor -->
  <div v-else class="flex flex-col h-[calc(100vh-3.5rem)]">
    <div class="flex items-center justify-between px-4 md:px-8 py-3 border-b border-[var(--cv-divider-gray)] bg-[var(--cv-surface)]">
      <div class="flex items-center gap-4">
        <button
          type="button"
          class="text-sm font-bold text-[var(--cv-primary-dark)] hover:underline underline-offset-2"
          @click="closeEditor"
        >
          &larr; Back
        </button>
        <span class="text-sm font-bold text-[var(--cv-body-text)]">{{ currentPrompt?.name || editingSlug }}</span>
        <span v-if="currentPrompt" class="text-xs text-[var(--cv-muted-text)]">v{{ currentPrompt.version }}</span>
      </div>
    </div>
    <div class="flex-1 min-h-0">
      <MdEditor
        v-model="editContent"
        @save="savePrompt"
      />
    </div>
  </div>
</template>
