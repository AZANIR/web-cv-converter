<script setup lang="ts">
definePageMeta({ layout: false })

const route = useRoute()
const isAdminGate = computed(() => route.query.reason === 'admin')
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
      <div class="text-center w-full space-y-1">
        <h1 class="text-2xl font-bold text-[var(--cv-primary-dark)]">
          CV Converter
        </h1>
        <p class="text-base text-[var(--cv-muted-text)]">
          Sign in to access CV Converter
        </p>
      </div>

      <div
        class="w-full rounded-lg border border-[var(--cv-error-red)] bg-[var(--cv-error-bg)] px-4 py-3"
      >
        <p
          v-if="isAdminGate"
          class="text-sm text-[var(--cv-error-red)] text-left"
        >
          This area is for administrators only. Ask the operator to set
          <code class="text-xs bg-[var(--cv-surface)] px-1 rounded border border-[var(--cv-divider-gray)]">profiles.role = 'admin'</code>
          in Supabase, or add your email to
          <code class="text-xs bg-[var(--cv-surface)] px-1 rounded border border-[var(--cv-divider-gray)]">ADMIN_EMAILS</code>
          in the backend environment.
        </p>
        <p
          v-else
          class="text-sm text-[var(--cv-error-red)]"
        >
          Access not allowed. Contact admin to get access.
        </p>
      </div>

      <div class="w-full flex flex-col gap-3">
        <UButton
          v-if="isAdminGate"
          to="/dashboard"
          block
          class="h-12 !rounded-lg border border-[var(--cv-divider-gray)] !bg-[var(--cv-surface)] !text-[var(--cv-body-text)]"
        >
          Back to dashboard
        </UButton>
        <UButton
          to="/api/auth/logout"
          external
          block
          class="h-12 !rounded-lg border border-[var(--cv-divider-gray)] !bg-[var(--cv-surface)] !text-[var(--cv-body-text)]"
        >
          Sign out
        </UButton>
      </div>

      <p class="text-xs italic text-[var(--cv-muted-text)]">
        Access by invitation only
      </p>
    </div>
  </div>
</template>
