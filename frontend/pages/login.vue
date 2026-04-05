<script setup lang="ts">
definePageMeta({ layout: false })

const route = useRoute()
const { loggedIn, fetch } = useUserSession()
await fetch()
if (loggedIn.value) {
  await navigateTo('/dashboard')
}

const showError = computed(() => route.query.error === 'auth_failed')
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-[var(--cv-light-gray-bg)] p-4">
    <div
      class="w-full max-w-[400px] rounded-xl bg-[var(--cv-surface)] p-8 flex flex-col items-center gap-6"
      style="box-shadow: var(--cv-card-shadow)"
    >
      <div
        class="w-12 h-12 rounded-xl bg-[var(--cv-teal-accent)] flex items-center justify-center"
      >
        <span class="text-white text-base font-bold">CV</span>
      </div>
      <div class="text-center space-y-1">
        <h1 class="text-2xl font-bold text-[var(--cv-primary-dark)]">
          CV Converter
        </h1>
        <p class="text-base text-[var(--cv-muted-text)]">
          Sign in to access CV Converter
        </p>
      </div>

      <div
        v-if="showError"
        class="w-full rounded-lg border border-[var(--cv-error-red)] bg-[var(--cv-error-bg)] px-4 py-3 text-sm text-[var(--cv-error-red)]"
      >
        Access was denied or sign-in failed. If you were invited, contact an admin.
      </div>

      <UButton
        to="/api/auth/auth0"
        external
        block
        size="lg"
        class="h-12 justify-center gap-3 !rounded-lg border border-[var(--cv-divider-gray)] !bg-[var(--cv-surface)] !text-[15px] !text-[var(--cv-body-text)] !font-normal hover:!bg-[var(--cv-light-gray-bg)]"
      >
        <span
          class="text-[#4285F4] text-xl font-bold leading-none"
          aria-hidden="true"
        >G</span>
        Sign in with Google
      </UButton>

      <p class="text-xs italic text-[var(--cv-muted-text)]">
        Access by invitation only
      </p>
    </div>
  </div>
</template>
