<script setup lang="ts">
const route = useRoute()
const { user, fetch } = useUserSession()
const api = useApiRequest()

const isAdmin = ref(false)
const menuOpen = ref(false)

onMounted(async () => {
  await fetch()
  try {
    const me = await api<{ role?: string }>('/api/me')
    isAdmin.value = me?.role === 'admin'
  }
  catch {
    isAdmin.value = false
  }
})

function linkClass(path: string) {
  const active = route.path === path || route.path.startsWith(`${path}/`)
  return active
    ? 'text-[var(--cv-teal-accent)] font-bold'
    : 'text-[var(--cv-muted-text)] font-normal'
}

function mobileLinkClass(path: string) {
  const active = route.path === path || route.path.startsWith(`${path}/`)
  return active
    ? 'flex items-center h-12 px-4 bg-[var(--cv-teal-subtle-bg)] text-[var(--cv-teal-accent)] font-bold text-sm'
    : 'flex items-center h-12 px-4 text-sm text-[var(--cv-muted-text)]'
}

async function logout() {
  menuOpen.value = false
  await navigateTo('/api/auth/logout', { external: true })
}
</script>

<template>
  <header
    class="cv-nav-border sticky top-0 z-40 bg-[var(--cv-surface)] h-14 px-4 md:px-8 flex items-center justify-between"
  >
    <div class="flex items-center gap-1">
      <NuxtLink
        to="/dashboard"
        class="text-[var(--cv-primary-dark)] font-bold text-lg leading-none"
      >
        CV Converter
      </NuxtLink>
    </div>

    <!-- Desktop: gap 24px per wcc2 NavBar -->
    <nav class="hidden md:flex items-center gap-6">
      <NuxtLink
        to="/dashboard"
        :class="linkClass('/dashboard')"
        class="text-sm"
      >
        Dashboard
      </NuxtLink>
      <NuxtLink
        to="/generate"
        :class="linkClass('/generate')"
        class="text-sm"
      >
        Generate CV
      </NuxtLink>
      <NuxtLink
        to="/history"
        :class="linkClass('/history')"
        class="text-sm"
      >
        History
      </NuxtLink>
      <NuxtLink
        to="/generate-history"
        :class="linkClass('/generate-history')"
        class="text-sm"
      >
        Generated
      </NuxtLink>
      <NuxtLink
        v-if="isAdmin"
        to="/admin"
        :class="linkClass('/admin')"
        class="text-sm"
      >
        Admin
      </NuxtLink>
      <NuxtLink
        v-if="isAdmin"
        to="/admin/prompts"
        :class="linkClass('/admin/prompts')"
        class="text-sm"
      >
        Prompts
      </NuxtLink>
      <div class="w-px h-6 bg-[var(--cv-divider-gray)] shrink-0" aria-hidden="true" />
      <div class="flex items-center gap-2">
        <img
          v-if="user?.picture"
          :src="user.picture"
          alt=""
          class="w-8 h-8 rounded-full object-cover"
        >
        <span
          v-else
          class="w-8 h-8 rounded-full bg-[var(--cv-teal-accent)] shrink-0"
        />
        <span class="text-[var(--cv-muted-text)] text-sm">▾</span>
      </div>
      <button
        type="button"
        class="text-sm font-medium text-[var(--cv-primary-dark)] hover:underline underline-offset-2 px-1"
        @click="logout"
      >
        Log out
      </button>
    </nav>

    <!-- Mobile -->
    <button
      type="button"
      class="md:hidden p-2 -mr-2 text-[var(--cv-body-text)]"
      aria-label="Menu"
      @click="menuOpen = !menuOpen"
    >
      <UIcon
        :name="menuOpen ? 'i-heroicons-x-mark-20-solid' : 'i-heroicons-bars-3-20-solid'"
        class="w-6 h-6"
      />
    </button>
  </header>

  <!-- Mobile drawer -->
  <div
    v-if="menuOpen"
    class="md:hidden fixed inset-0 top-14 z-30 bg-[var(--cv-surface)] border-t border-[var(--cv-divider-gray)] flex flex-col"
  >
    <NuxtLink
      to="/dashboard"
      :class="mobileLinkClass('/dashboard')"
      @click="menuOpen = false"
    >
      Dashboard
    </NuxtLink>
    <NuxtLink
      to="/generate"
      :class="mobileLinkClass('/generate')"
      @click="menuOpen = false"
    >
      Generate CV
    </NuxtLink>
    <NuxtLink
      to="/history"
      :class="mobileLinkClass('/history')"
      @click="menuOpen = false"
    >
      History
    </NuxtLink>
    <NuxtLink
      to="/generate-history"
      :class="mobileLinkClass('/generate-history')"
      @click="menuOpen = false"
    >
      Generated
    </NuxtLink>
    <NuxtLink
      v-if="isAdmin"
      to="/admin"
      :class="mobileLinkClass('/admin')"
      @click="menuOpen = false"
    >
      Admin
    </NuxtLink>
    <NuxtLink
      v-if="isAdmin"
      to="/admin/prompts"
      :class="mobileLinkClass('/admin/prompts')"
      @click="menuOpen = false"
    >
      Prompts
    </NuxtLink>
    <div class="h-px bg-[var(--cv-divider-gray)] my-2" />
    <div class="px-4 py-3 flex flex-col gap-2">
      <div class="flex items-center gap-2 text-sm text-[var(--cv-muted-text)]">
        <img
          v-if="user?.picture"
          :src="user.picture"
          alt=""
          class="w-8 h-8 rounded-full"
        >
        <span>{{ user?.name || user?.email }}</span>
      </div>
      <UButton
        variant="soft"
        color="gray"
        block
        @click="logout"
      >
        Log out
      </UButton>
    </div>
  </div>
</template>
