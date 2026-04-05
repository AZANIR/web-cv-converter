<script setup lang="ts">
definePageMeta({ middleware: ['admin'] })

type AllowedRow = {
  id: string
  email: string
  note?: string
  created_at?: string
}

type ConvRow = {
  id: string
  user_id: string
  original_filename: string
  status: string
  created_at?: string
  user_email?: string
  user_full_name?: string
}

const api = useApiRequest()
const tab = ref<'access' | 'conversions'>('access')

const emails = ref<AllowedRow[]>([])
const newEmail = ref('')
const newNote = ref('')
const loadingUsers = ref(false)
const deleteTarget = ref<AllowedRow | null>(null)
const deleteOpen = ref(false)
const busy = ref(false)

const conversions = ref<ConvRow[]>([])
const loadingConv = ref(false)

async function loadUsers() {
  loadingUsers.value = true
  try {
    const res = await api<{ items: AllowedRow[] }>('/api/admin/users')
    emails.value = res.items || []
  }
  finally {
    loadingUsers.value = false
  }
}

async function loadConversions() {
  loadingConv.value = true
  try {
    const res = await api<{ items: ConvRow[] }>('/api/admin/conversions')
    conversions.value = res.items || []
  }
  finally {
    loadingConv.value = false
  }
}

onMounted(async () => {
  await loadUsers()
  await loadConversions()
})

watch(tab, async (t) => {
  if (t === 'conversions') {
    await loadConversions()
  }
})

async function addEmail() {
  if (!newEmail.value.trim()) {
    return
  }
  busy.value = true
  try {
    await api('/api/admin/users', {
      method: 'POST',
      body: { email: newEmail.value.trim(), note: newNote.value || null },
    })
    newEmail.value = ''
    newNote.value = ''
    await loadUsers()
  }
  finally {
    busy.value = false
  }
}

function mapStatus(s: string): 'completed' | 'processing' | 'failed' | 'pending' {
  if (s === 'completed' || s === 'processing' || s === 'failed' || s === 'pending') {
    return s
  }
  return 'pending'
}

async function confirmRemove() {
  if (!deleteTarget.value) {
    return
  }
  busy.value = true
  try {
    const e = encodeURIComponent(deleteTarget.value.email)
    await api(`/api/admin/users?email=${e}`, { method: 'DELETE' })
    deleteTarget.value = null
    deleteOpen.value = false
    await loadUsers()
  }
  finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="max-w-[800px] mx-auto px-4 md:px-8 py-8 md:py-10 space-y-6">
    <h1 class="text-[1.75rem] font-bold text-[var(--cv-primary-dark)] leading-tight">
      Admin Panel
    </h1>

    <div class="flex gap-0 border-b border-[var(--cv-divider-gray)]">
      <button
        type="button"
        class="px-5 py-2.5 text-sm -mb-px transition-colors"
        :class="tab === 'access'
          ? 'border-b-2 border-[var(--cv-teal-accent)] text-[var(--cv-teal-accent)] font-bold'
          : 'text-[var(--cv-muted-text)] font-normal'"
        @click="tab = 'access'"
      >
        Access Management
      </button>
      <button
        type="button"
        class="px-5 py-2.5 text-sm -mb-px transition-colors"
        :class="tab === 'conversions'
          ? 'border-b-2 border-[var(--cv-teal-accent)] text-[var(--cv-teal-accent)] font-bold'
          : 'text-[var(--cv-muted-text)] font-normal'"
        @click="tab = 'conversions'"
      >
        All Conversions
      </button>
    </div>

    <div v-if="tab === 'access'">
      <div class="space-y-3 mb-6">
        <p class="text-base font-bold text-[var(--cv-body-text)]">
          Add New Access
        </p>
        <div class="flex flex-col lg:flex-row gap-2">
          <UInput
            v-model="newEmail"
            type="email"
            placeholder="email@example.com"
            size="md"
            class="flex-1"
            :ui="{ rounded: 'rounded-md' }"
          />
          <UInput
            v-model="newNote"
            placeholder="Note (optional)"
            size="md"
            class="w-full lg:w-[200px]"
            :ui="{ rounded: 'rounded-md' }"
          />
          <UButton
            :loading="busy"
            class="!bg-[var(--cv-teal-accent)] !text-white shrink-0 h-10 px-6 !rounded-lg text-sm font-bold justify-center"
            @click="addEmail"
          >
            Add
          </UButton>
        </div>
      </div>

      <div class="space-y-2">
        <div class="flex items-center gap-2 flex-wrap">
          <p class="text-base font-bold text-[var(--cv-body-text)]">
            Allowed Users
          </p>
          <span
            class="inline-flex items-center rounded-full bg-[var(--cv-teal-accent)] text-white text-xs font-bold px-2 py-0.5 min-w-[1.5rem] justify-center"
          >{{ emails.length }}</span>
        </div>

        <div
          v-if="loadingUsers"
          class="space-y-2"
        >
          <USkeleton class="h-12 w-full rounded-lg" />
          <USkeleton class="h-12 w-full rounded-lg" />
        </div>

        <div
          v-else
          class="rounded-lg border border-[var(--cv-divider-gray)] overflow-hidden bg-[var(--cv-surface)]"
        >
          <table class="w-full text-sm">
            <thead class="bg-[var(--cv-primary-dark)] text-left text-white">
              <tr>
                <th class="px-4 py-2.5 font-medium">
                  Email
                </th>
                <th class="px-4 py-2.5 font-medium">
                  Note
                </th>
                <th class="px-4 py-2.5 w-24" />
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in emails"
                :key="row.id"
                class="border-t border-[var(--cv-divider-gray)]"
              >
                <td class="px-4 py-3 text-[var(--cv-body-text)]">
                  {{ row.email }}
                </td>
                <td class="px-4 py-3 text-[var(--cv-muted-text)]">
                  {{ row.note || '—' }}
                </td>
                <td class="px-4 py-3">
                  <button
                    type="button"
                    class="text-xs font-bold text-[var(--cv-error-red)] hover:underline"
                    @click="deleteTarget = row; deleteOpen = true"
                  >
                    Remove
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-else>
      <p class="text-sm text-[var(--cv-muted-text)] mb-4">
        Audit log of every conversion
      </p>
      <div
        v-if="loadingConv"
        class="space-y-2"
      >
        <USkeleton class="h-10 w-full rounded-lg" />
        <USkeleton class="h-10 w-full rounded-lg" />
      </div>
      <div
        v-else
        class="rounded-lg border border-[var(--cv-divider-gray)] overflow-x-auto bg-[var(--cv-surface)]"
      >
        <table class="w-full text-sm min-w-[640px]">
          <thead class="bg-[var(--cv-primary-dark)] text-left text-white">
            <tr>
              <th class="px-4 py-2.5 font-medium">
                User
              </th>
              <th class="px-4 py-2.5 font-medium">
                File
              </th>
              <th class="px-4 py-2.5 font-medium">
                Status
              </th>
              <th class="px-4 py-2.5 font-medium">
                When
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="c in conversions"
              :key="c.id"
              class="border-t border-[var(--cv-divider-gray)]"
            >
              <td class="px-4 py-3 text-[var(--cv-body-text)]">
                {{ c.user_email || c.user_id }}
              </td>
              <td class="px-4 py-3">
                {{ c.original_filename }}
              </td>
              <td class="px-4 py-3">
                <StatusBadge :status="mapStatus(c.status)" />
              </td>
              <td class="px-4 py-3 text-[var(--cv-muted-text)] text-xs">
                {{ c.created_at ? new Date(c.created_at).toLocaleString() : '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <UModal
      v-model="deleteOpen"
      :ui="{ width: 'sm:max-w-md' }"
    >
      <div
        v-if="deleteTarget"
        class="p-6 space-y-4 w-full max-w-[420px]"
      >
        <h2 class="text-lg font-semibold text-[var(--cv-primary-dark)]">
          Remove access
        </h2>
        <p class="text-sm text-[var(--cv-body-text)]">
          Remove <strong>{{ deleteTarget.email }}</strong> from the allow list?
        </p>
        <div class="flex justify-end gap-2 pt-2">
          <UButton
            variant="ghost"
            @click="deleteOpen = false; deleteTarget = null"
          >
            Cancel
          </UButton>
          <UButton
            color="red"
            :loading="busy"
            @click="confirmRemove"
          >
            Remove
          </UButton>
        </div>
      </div>
    </UModal>
  </div>
</template>
