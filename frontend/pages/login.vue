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
  <div class="min-h-screen flex items-center justify-center bg-cv-light-gray p-4">
    <div
      class="w-full max-w-[400px] rounded-xl bg-cv-surface p-8 flex flex-col items-center gap-6"
      style="box-shadow: var(--cv-card-shadow)"
    >
      <div
        class="w-12 h-12 rounded-xl bg-cv-teal flex items-center justify-center"
      >
        <span class="text-white text-base font-bold">CV</span>
      </div>
      <div class="text-center space-y-1">
        <h1 class="text-2xl font-bold text-cv-primary">
          CV Converter
        </h1>
        <p class="text-base text-cv-muted">
          Sign in to access CV Converter
        </p>
      </div>

      <div
        v-if="showError"
        class="w-full rounded-lg border border-cv-error bg-cv-error-bg px-4 py-3 text-sm text-cv-error"
      >
        Access was denied or sign-in failed. If you were invited, contact an admin.
      </div>

      <UButton
        to="/api/auth/auth0"
        external
        block
        size="lg"
        class="h-12 justify-center gap-3 !rounded-lg border border-cv-divider !bg-cv-surface !text-[15px] !text-cv-body !font-normal hover:!bg-cv-light-gray"
      >
        <span
          class="text-[#4285F4] text-xl font-bold leading-none"
          aria-hidden="true"
        >G</span>
        Sign in with Google
      </UButton>

      <p class="text-xs italic text-cv-muted">
        Access by invitation only
      </p>
    </div>
  </div>
</template>
