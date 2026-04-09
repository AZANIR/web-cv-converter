<script setup lang="ts">
const { loggedIn, fetch } = useUserSession()
await fetch()
if (loggedIn.value) {
  await navigateTo('/dashboard')
}
else {
  await navigateTo('/login')
}
</script>

<template>
  <div class="p-8 text-center text-cv-muted">
    Redirecting…
  </div>
</template>
