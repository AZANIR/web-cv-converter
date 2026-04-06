import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import StatusBadge from '~/components/StatusBadge.vue'

describe('StatusBadge', () => {
  const cases = [
    { status: 'completed' as const, label: 'Done', cssFragment: 'cv-success' },
    { status: 'processing' as const, label: 'Processing...', cssFragment: 'cv-warning' },
    { status: 'failed' as const, label: 'Failed', cssFragment: 'cv-error' },
    { status: 'pending' as const, label: 'Pending', cssFragment: 'cv-muted' },
  ]

  for (const { status, label, cssFragment } of cases) {
    it(`renders "${label}" for status="${status}"`, async () => {
      const wrapper = await mountSuspended(StatusBadge, { props: { status } })

      expect(wrapper.text()).toContain(label)
      const span = wrapper.find('.cv-badge')
      expect(span.exists()).toBe(true)
      expect(span.classes().join(' ')).toContain(cssFragment)
    })
  }

  it('renders the correct icon for completed', async () => {
    const wrapper = await mountSuspended(StatusBadge, { props: { status: 'completed' } })
    expect(wrapper.text()).toContain('✅')
  })

  it('renders the correct icon for failed', async () => {
    const wrapper = await mountSuspended(StatusBadge, { props: { status: 'failed' } })
    expect(wrapper.text()).toContain('❌')
  })
})
