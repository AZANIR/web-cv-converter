import type { Config } from 'tailwindcss'

export default {
  theme: {
    extend: {
      colors: {
        // CV design tokens – mapped from CSS variables defined in assets/css/main.css
        'cv-primary':     'var(--cv-primary-dark)',
        'cv-teal':        'var(--cv-teal-accent)',
        'cv-teal-subtle': 'var(--cv-teal-subtle-bg)',
        'cv-body':        'var(--cv-body-text)',
        'cv-muted':       'var(--cv-muted-text)',
        'cv-light-gray':  'var(--cv-light-gray-bg)',
        'cv-surface':     'var(--cv-surface)',
        'cv-divider':     'var(--cv-divider-gray)',
        'cv-success':     'var(--cv-success-green)',
        'cv-success-bg':  'var(--cv-success-bg)',
        'cv-error':       'var(--cv-error-red)',
        'cv-error-bg':    'var(--cv-error-bg)',
        'cv-warning':     'var(--cv-warning-amber)',
        'cv-warning-bg':  'var(--cv-warning-bg)',
        'cv-pending':     'var(--cv-pending-badge-bg)',
        // Additional tokens (not yet used as Tailwind classes but defined in :root)
        'cv-primary-dark-90':       'var(--cv-primary-dark-90)',
        'cv-teal-light-bg':         'var(--cv-teal-light-bg)',
        'cv-tag-bg':                'var(--cv-tag-bg)',
        'cv-tag-text':              'var(--cv-tag-text)',
        'cv-header-title-light':    'var(--cv-header-title-light)',
        'cv-header-contacts-light': 'var(--cv-header-contacts-light)',
      },
    },
  },
} satisfies Config
