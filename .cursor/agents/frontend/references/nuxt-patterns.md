# Nuxt 3 Patterns

## Page Structure

```vue
<!-- frontend/pages/example.vue -->
<template>
  <div>
    <h1>Page Title</h1>
    <!-- content -->
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: ['auth'],  // add if page requires login
})

const { data, error } = await useApi('/api/resource')
</script>
```

## Component Structure

```vue
<!-- frontend/components/ExampleCard.vue -->
<template>
  <div class="...">
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  status?: 'pending' | 'done' | 'error'
}
const props = withDefaults(defineProps<Props>(), {
  status: 'pending',
})
const emit = defineEmits<{
  (e: 'action', id: string): void
}>()
</script>
```

## Composable Pattern

```typescript
// frontend/composables/useResourceName.ts
export function useResourceName() {
  const state = ref<ResourceType | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchResource(id: string) {
    loading.value = true
    error.value = null
    try {
      const { data } = await useApi(`/api/resource/${id}`)
      state.value = data
    } catch (e) {
      error.value = 'Failed to load resource'
    } finally {
      loading.value = false
    }
  }

  return { state, loading, error, fetchResource }
}
```

## Auth Check Pattern

```vue
<script setup lang="ts">
const { user, loggedIn } = useUserSession()

// Redirect if not logged in (alternative to middleware for inline checks)
if (!loggedIn.value) {
  await navigateTo('/login')
}
</script>
```

## API Call Pattern

```typescript
// Always use useApi composable — never $fetch directly in components
const { data, error, refresh } = await useApi('/api/convert', {
  method: 'POST',
  body: { markdown, vacancy },
})
```

## Auth Middleware (`frontend/middleware/auth.ts`)

```typescript
export default defineNuxtRouteMiddleware(() => {
  const { loggedIn } = useUserSession()
  if (!loggedIn.value) {
    return navigateTo('/login')
  }
})
```

## Server Route Pattern (`frontend/server/api/`)

```typescript
// frontend/server/api/resource.get.ts
export default defineEventHandler(async (event) => {
  const session = await getUserSession(event)
  if (!session.user) {
    throw createError({ statusCode: 401, message: 'Unauthenticated' })
  }
  // proxy to backend...
})
```
