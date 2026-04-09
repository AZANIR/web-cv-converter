# Component Checklist

Run this checklist before returning a frontend handoff object.

## Structure
- [ ] File is in the correct directory (`pages/`, `components/`, `composables/`, `layouts/`, `middleware/`)
- [ ] Component file uses `<script setup lang="ts">` — no Options API
- [ ] No manual imports of Vue primitives (Nuxt auto-imports `ref`, `computed`, `watch`, etc.)
- [ ] Props typed with TypeScript interface and `defineProps<Props>()`
- [ ] Emits typed with `defineEmits<{...}>()`

## Auth & API
- [ ] Auth state uses `useUserSession()` — not hardcoded checks
- [ ] All API calls go through `useApi.ts` — no direct `$fetch()` in components
- [ ] Protected pages have `definePageMeta({ middleware: ['auth'] })`

## Security
- [ ] No `v-html` with user-provided content
- [ ] No secrets or API keys in component code
- [ ] No `localStorage` usage for auth tokens

## Accessibility (WCAG 2.2)
- [ ] All `<img>` have `alt` attribute
- [ ] Icon-only buttons have `aria-label`
- [ ] All form inputs have visible label or `aria-label`
- [ ] Focus outline is visible (no bare `outline-none`)
- [ ] Interactive elements are keyboard-accessible (Tab + Enter/Space)
- [ ] Error messages use `role="alert"` or `aria-live`

## Design System
- [ ] Uses @nuxt/ui components (`UButton`, `UCard`, `UInput`, etc.) where applicable
- [ ] Spacing uses Tailwind scale — no arbitrary values
- [ ] Colors use semantic Tailwind/nuxt-ui tokens — no hardcoded hex
