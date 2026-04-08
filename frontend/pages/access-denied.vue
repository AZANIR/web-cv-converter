<script setup lang="ts">
definePageMeta({ layout: false })

const route = useRoute()
const isAdminGate = computed(() => route.query.reason === 'admin')
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
      <div class="text-center w-full space-y-1">
        <h1 class="text-2xl font-bold text-cv-primary">
          CV Converter
        </h1>
        <p class="text-base text-cv-muted">
          Sign in to access CV Converter
        </p>
      </div>

      <div
        class="w-full rounded-lg border border-cv-error bg-cv-error-bg px-4 py-3"
      >
        <p
          v-if="isAdminGate"
          class="text-sm text-cv-error text-left"
        >
          This area is for administrators only. Ask the operator to set
          <code class="text-xs bg-cv-surface px-1 rounded border border-cv-divider">profiles.role = 'admin'</code>
          in Supabase, or add your email to
          <code class="text-xs bg-cv-surface px-1 rounded border border-cv-divider">ADMIN_EMAILS</code>
          in the backend environment.
        </p>
        <p
          v-else
          class="text-sm text-cv-error"
        >
          Access not allowed. Contact admin to get access.
        </p>
      </div>

      <div class="w-full flex flex-col gap-3">
        <UButton
          v-if="isAdminGate"
          to="/dashboard"
          block
          class="h-12 !rounded-lg border border-cv-divider !bg-cv-surface !text-cv-body"
        >
          Back to dashboard
        </UButton>
        <UButton
          to="/api/auth/logout"
          external
          block
          class="h-12 !rounded-lg border border-cv-divider !bg-cv-surface !text-cv-body"
        >
          Sign out
        </UButton>
      </div>

      <p class="text-xs italic text-cv-muted">
        Access by invitation only
      </p>
    </div>
  </div>
</template>
