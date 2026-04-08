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
      return 'bg-cv-success-bg text-cv-success'
    case 'processing':
      return 'bg-cv-warning-bg text-cv-warning'
    case 'failed':
      return 'bg-cv-error-bg text-cv-error'
    default:
      return 'bg-cv-pending text-cv-muted'
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
