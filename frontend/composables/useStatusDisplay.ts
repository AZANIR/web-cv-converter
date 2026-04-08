/**
 * Shared status display logic for both conversion history (history.vue)
 * and generated CV history (generate-history.vue).
 */
export function useStatusDisplay() {
  function statusLabel(status: string): string {
    const map: Record<string, string> = {
      pending: 'Pending',
      processing: 'Processing...',
      generating: 'Generating',
      converting: 'Converting',
      draft: 'Draft',
      completed: 'Completed',
      failed: 'Failed',
    }
    return map[status] ?? status
  }

  function statusClasses(status: string): string {
    if (status === 'completed') return 'bg-emerald-50 text-emerald-700 border-emerald-200'
    if (status === 'failed') return 'bg-red-50 text-red-600 border-red-200'
    if (status === 'draft') return 'bg-sky-50 text-sky-700 border-sky-200'
    if (status === 'pending' || status === 'processing' || status === 'generating' || status === 'converting')
      return 'bg-amber-50 text-amber-700 border-amber-200'
    return 'bg-gray-50 text-gray-500 border-gray-200'
  }

  return { statusLabel, statusClasses }
}
