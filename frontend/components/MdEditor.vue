<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'

const props = defineProps<{
  modelValue: string
  readonly?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  save: [value: string]
}>()

const md = new MarkdownIt({ html: false, linkify: true, typographer: false })

const localContent = ref(props.modelValue)
const renderedHtml = ref('')
const showSaved = ref(false)
let savedTimer: ReturnType<typeof setTimeout> | null = null
let debounceTimer: ReturnType<typeof setTimeout> | null = null

function flashSaved() {
  showSaved.value = true
  if (savedTimer) clearTimeout(savedTimer)
  savedTimer = setTimeout(() => { showSaved.value = false }, 2000)
}

watch(() => props.modelValue, (val) => {
  if (val !== localContent.value) {
    localContent.value = val
  }
})

watch(localContent, (val) => {
  renderedHtml.value = DOMPurify.sanitize(md.render(val || ''))
  emit('update:modelValue', val)
}, { immediate: true })

function onInput(e: Event) {
  const target = e.target as HTMLTextAreaElement
  localContent.value = target.value
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  debounceTimer = setTimeout(() => {
    emit('save', localContent.value)
    flashSaved()
  }, 2000)
}

function saveNow() {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
    debounceTimer = null
  }
  emit('save', localContent.value)
  flashSaved()
}

onUnmounted(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
  if (savedTimer) clearTimeout(savedTimer)
})
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="flex items-center justify-between px-4 py-2 border-b border-cv-divider bg-cv-surface">
      <div class="flex items-center gap-4 text-sm text-cv-muted">
        <span class="font-bold text-cv-body">Markdown</span>
        <span class="hidden sm:inline">|</span>
        <span class="hidden sm:inline font-bold text-cv-body">Preview</span>
      </div>
      <div class="flex items-center gap-3">
        <Transition
          enter-active-class="transition-opacity duration-200"
          leave-active-class="transition-opacity duration-500"
          enter-from-class="opacity-0"
          leave-to-class="opacity-0"
        >
          <span
            v-if="showSaved"
            class="text-xs font-bold text-emerald-600 bg-emerald-50 border border-emerald-200 rounded-full px-2.5 py-0.5"
          >
            &#10003; Saved
          </span>
        </Transition>
        <button
          v-if="!readonly"
          type="button"
          class="text-sm font-bold text-cv-teal hover:underline underline-offset-2"
          @click="saveNow"
        >
          Save
        </button>
      </div>
    </div>

    <div class="flex flex-1 min-h-0">
      <div class="w-1/2 border-r border-cv-divider flex flex-col">
        <textarea
          :value="localContent"
          :readonly="readonly"
          aria-label="Markdown editor"
          class="flex-1 p-4 resize-none font-mono text-sm leading-relaxed text-cv-body bg-cv-surface outline-none"
          placeholder="Markdown content..."
          @input="onInput"
        />
      </div>
      <div class="w-1/2 flex flex-col">
        <div
          class="flex-1 p-4 overflow-y-auto text-sm leading-relaxed text-cv-body prose prose-sm max-w-none"
          v-html="renderedHtml"
        />
      </div>
    </div>
  </div>
</template>
