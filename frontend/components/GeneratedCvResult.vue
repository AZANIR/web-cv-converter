<script setup lang="ts">
const props = defineProps<{
  cvId: string
  status: string
  errorMessage?: string | null
  downloadUrl?: string | null
}>()

const emit = defineEmits<{
  convert: [includeHeader: boolean]
}>()

const includeHeader = ref(true)
</script>

<template>
  <div class="rounded-xl border bg-[var(--cv-surface)] p-6 flex flex-col gap-4"
    :class="status === 'failed'
      ? 'border-[var(--cv-error-red)]'
      : status === 'completed'
        ? 'border-[var(--cv-success-green)]'
        : 'border-[var(--cv-divider-gray)]'"
  >
    <!-- Status indicator -->
    <div class="flex items-center gap-3">
      <span v-if="status === 'draft'" class="text-xl font-bold text-[var(--cv-teal-accent)]">&#9998;</span>
      <span v-else-if="status === 'pending' || status === 'generating'" class="text-xl text-[var(--cv-body-text)]">&#8987;</span>
      <span v-else-if="status === 'converting'" class="text-xl text-[var(--cv-body-text)]">&#8987;</span>
      <span v-else-if="status === 'completed'" class="text-xl font-bold text-[var(--cv-success-green)]">&#10003;</span>
      <span v-else-if="status === 'failed'" class="text-xl font-bold text-[var(--cv-error-red)]">&#10007;</span>
      <p class="text-base font-bold text-[var(--cv-body-text)]">
        <template v-if="status === 'draft'">CV generated — ready to edit or convert</template>
        <template v-else-if="status === 'pending' || status === 'generating'">Generating CV...</template>
        <template v-else-if="status === 'converting'">Converting to PDF...</template>
        <template v-else-if="status === 'completed'">PDF is ready!</template>
        <template v-else-if="status === 'failed'">Generation failed</template>
      </p>
    </div>

    <!-- Error -->
    <p v-if="status === 'failed' && errorMessage" class="text-sm text-[var(--cv-error-red)]">
      {{ errorMessage }}
    </p>

    <!-- Header toggle -->
    <div
      v-if="status === 'draft' || status === 'completed'"
      class="flex items-center justify-between rounded-lg border border-[var(--cv-divider-gray)] px-4 py-3"
    >
      <div class="flex flex-col gap-0.5">
        <span class="text-sm font-bold text-[var(--cv-body-text)]">Include header image</span>
        <span class="text-xs text-[var(--cv-muted-text)]">Add the company banner to the PDF</span>
      </div>
      <button
        type="button"
        role="switch"
        :aria-checked="includeHeader"
        class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors"
        :class="includeHeader ? 'bg-[var(--cv-teal-accent)]' : 'bg-[var(--cv-divider-gray)]'"
        @click="includeHeader = !includeHeader"
      >
        <span
          class="pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transform transition-transform"
          :class="includeHeader ? 'translate-x-5' : 'translate-x-0'"
        />
      </button>
    </div>

    <!-- Actions -->
    <div class="flex flex-col sm:flex-row gap-3">
      <UButton
        v-if="status === 'draft'"
        class="h-10 justify-center !rounded-lg !bg-[var(--cv-teal-accent)] !text-white text-sm font-bold px-6 flex-1"
        @click="emit('convert', includeHeader)"
      >
        Convert to PDF
      </UButton>
      <UButton
        v-if="status === 'completed' && downloadUrl"
        :to="downloadUrl"
        target="_blank"
        external
        class="h-10 justify-center !rounded-lg !bg-[var(--cv-teal-accent)] !text-white text-sm font-bold px-6 flex-1"
      >
        Download PDF
      </UButton>
    </div>
  </div>
</template>
