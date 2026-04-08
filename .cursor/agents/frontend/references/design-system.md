# Design System

## UI Library

@nuxt/ui (Tailwind CSS-based). Use `UButton`, `UCard`, `UInput`, `UBadge`, `UModal` etc. from the library before creating custom components.

## Spacing Scale (Tailwind)

Use Tailwind spacing classes only. Do NOT use arbitrary values like `p-[13px]`.

| Purpose | Class |
|---|---|
| Page padding | `p-6` or `px-6 py-4` |
| Card padding | `p-4` |
| Section gap | `gap-4` or `gap-6` |
| Inline gap | `gap-2` |
| Form field gap | `space-y-4` |

## Color Usage

Use Tailwind semantic colors via @nuxt/ui tokens. Avoid hardcoded hex values.

| Semantic | Class |
|---|---|
| Primary action | `bg-primary` / `text-primary` |
| Destructive | `bg-red-500` / `text-red-600` |
| Success | `text-green-600` |
| Muted text | `text-gray-500` |
| Card background | `bg-white dark:bg-gray-900` |

## Typography

| Element | Class |
|---|---|
| Page title | `text-2xl font-bold` |
| Section heading | `text-lg font-semibold` |
| Body text | `text-sm` or `text-base` |
| Muted/helper text | `text-sm text-gray-500` |

## WCAG 2.2 Requirements

**Color contrast:** Normal text must have >= 4.5:1 contrast ratio. Large text (>= 18pt or 14pt bold) must have >= 3:1.

**Keyboard navigation:**
- All interactive elements (buttons, links, inputs) must be focusable with Tab
- Focus indicators must be visible — do NOT `outline-none` without replacement
- Custom interactive elements must have `tabindex="0"` and keyboard event handlers

**ARIA:**
- All `<img>` tags require `alt` attribute (empty string `alt=""` for decorative images)
- Icon-only buttons require `aria-label`
- Form inputs require associated `<label>` or `aria-label`
- Loading states: use `aria-busy="true"` on container
- Error messages: use `role="alert"` or `aria-live="polite"`

**Forms:**
- Each input has a visible label or `aria-label`
- Validation errors are announced (use `role="alert"` on error container)
- Required fields marked with `aria-required="true"` or `required` attribute

## Existing Component Conventions

Before creating a new component, check if one of these existing components covers the need:
- `ConversionCard.vue` — card for displaying conversion results
- `StatusBadge.vue` — status indicator badge
- `UploadForm.vue` — file/markdown upload form
- `VacancyInputForm.vue` — vacancy URL/text input
- `MdEditor.vue` — Markdown editor
- `GeneratedCvResult.vue` — CV generation result display
- `AppNav.vue` — navigation bar
