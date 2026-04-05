<script setup lang="ts">
const props = defineProps<{
  status: 'completed' | 'processing' | 'failed' | 'pending'
}>()

const label = computed(() => {
  switch (props.status) {
    case 'completed':
      return 'Done'
    case 'processing':
      return 'Processing...'
    case 'failed':
      return 'Failed'
    default:
      return 'Pending'
  }
})

const cls = computed(() => {
  switch (props.status) {
    case 'completed':
      return 'bg-[var(--cv-success-bg)] text-[var(--cv-success-green)]'
    case 'processing':
      return 'bg-[var(--cv-warning-bg)] text-[var(--cv-warning-amber)]'
    case 'failed':
      return 'bg-[var(--cv-error-bg)] text-[var(--cv-error-red)]'
    default:
      return 'bg-[var(--cv-pending-badge-bg)] text-[var(--cv-muted-text)]'
  }
})
</script>

<template>
  <span
    class="cv-badge inline-flex items-center gap-1"
    :class="cls"
  >
    <template v-if="status === 'completed'">✅</template>
    <template v-else-if="status === 'processing'">⟳</template>
    <template v-else-if="status === 'failed'">❌</template>
    <template v-else>○</template>
    {{ label }}
  </span>
</template>
