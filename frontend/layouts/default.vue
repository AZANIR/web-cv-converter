<script setup lang="ts">
const route = useRoute()
const hideNav = computed(() => route.path === '/login' || route.path === '/access-denied')
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <AppNav v-if="!hideNav" />
    <main class="flex-1">
      <slot />
    </main>
  </div>
</template>
