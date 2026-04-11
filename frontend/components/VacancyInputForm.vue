<script setup lang="ts">
const props = defineProps<{
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [data: { type: 'text' | 'url' | 'file'; text?: string; url?: string; file?: File }]
}>()

const activeTab = ref<'text' | 'url' | 'file'>('text')
const vacancyText = ref('')
const vacancyUrl = ref('')
const vacancyFile = ref<File | null>(null)
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const canSubmit = computed(() => {
  if (activeTab.value === 'text') return vacancyText.value.trim().length > 0
  if (activeTab.value === 'url') return vacancyUrl.value.trim().length > 0
  if (activeTab.value === 'file') return vacancyFile.value !== null
  return false
})

function setFile(f: File | null) {
  if (!f) {
    vacancyFile.value = null
    return
  }
  const name = f.name.toLowerCase()
  if (!name.endsWith('.md') && !name.endsWith('.txt') && !name.endsWith('.pdf')) {
    return
  }
  vacancyFile.value = f
}

function onDrop(e: DragEvent) {
  dragOver.value = false
  const f = e.dataTransfer?.files?.[0]
  if (f) setFile(f)
}

function submit() {
  if (!canSubmit.value || props.loading) return
  if (activeTab.value === 'text') {
    emit('submit', { type: 'text', text: vacancyText.value.trim() })
  }
  else if (activeTab.value === 'url') {
    emit('submit', { type: 'url', url: vacancyUrl.value.trim() })
  }
  else if (activeTab.value === 'file' && vacancyFile.value) {
    emit('submit', { type: 'file', file: vacancyFile.value })
  }
}
</script>

<template>
  <div class="flex flex-col gap-5">
    <!-- Tabs -->
    <div class="flex gap-1 rounded-lg bg-cv-teal-subtle p-1">
      <button
        v-for="tab in (['text', 'url', 'file'] as const)"
        :key="tab"
        type="button"
        class="flex-1 py-2 text-sm font-bold rounded-md transition-colors"
        :class="activeTab === tab
          ? 'bg-white text-cv-primary shadow-sm'
          : 'text-cv-muted hover:text-cv-body'"
        @click="activeTab = tab"
      >
        {{ tab === 'text' ? 'Text' : tab === 'url' ? 'URL' : 'File' }}
      </button>
    </div>

    <!-- Text tab -->
    <div v-if="activeTab === 'text'">
      <textarea
        v-model="vacancyText"
        rows="10"
        aria-label="Vacancy text"
        class="w-full rounded-lg border border-cv-divider bg-cv-surface p-4 text-sm text-cv-body resize-none outline-none focus:border-cv-teal transition-colors"
        placeholder="Paste the vacancy text here..."
      />
    </div>

    <!-- URL tab -->
    <div v-if="activeTab === 'url'">
      <input
        v-model="vacancyUrl"
        type="url"
        aria-label="Vacancy URL"
        class="w-full rounded-lg border border-cv-divider bg-cv-surface px-4 py-3 text-sm text-cv-body outline-none focus:border-cv-teal transition-colors"
        placeholder="https://example.com/job/..."
      >
    </div>

    <!-- File tab -->
    <div v-if="activeTab === 'file'">
      <input
        ref="fileInput"
        type="file"
        accept=".md,.txt,.pdf"
        aria-label="Upload vacancy file"
        class="hidden"
        @change="(e) => setFile((e.target as HTMLInputElement).files?.[0] || null)"
      >

      <div
        v-if="!vacancyFile"
        class="rounded-xl border-2 border-dashed border-cv-teal bg-cv-teal-subtle p-10 flex flex-col items-center gap-3 text-center cursor-pointer transition-shadow"
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
        <p class="text-base text-cv-body">
          Drop your file here
        </p>
        <p class="text-sm text-cv-teal">
          or click to browse
        </p>
        <p class="text-xs text-cv-muted">
          .md, .txt, .pdf
        </p>
      </div>

      <div
        v-else
        class="rounded-xl border border-cv-teal bg-cv-surface py-3 px-5 flex items-center justify-between gap-3"
      >
        <span class="text-sm font-bold text-cv-body truncate">{{ vacancyFile.name }}</span>
        <button
          type="button"
          class="text-sm font-bold text-cv-error hover:underline"
          @click="vacancyFile = null"
        >
          Remove
        </button>
      </div>
    </div>

    <!-- Submit -->
    <UButton
      block
      size="lg"
      class="h-12 justify-center !rounded-lg !bg-cv-teal !text-white hover:!brightness-95"
      :class="(!canSubmit || loading) ? 'opacity-40' : ''"
      :disabled="!canSubmit || loading"
      :loading="loading"
      @click="submit"
    >
      {{ loading ? 'Generating...' : 'Generate CV' }}
    </UButton>
  </div>
</template>
