import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import ConversionCard from '~/components/ConversionCard.vue'

describe('ConversionCard', () => {
  const baseProps = {
    id: 'conv-1',
    filename: 'resume.md',
    status: 'completed' as const,
    createdAt: '2025-01-15T10:30:00Z',
  }

  it('renders the filename', async () => {
    const wrapper = await mountSuspended(ConversionCard, { props: baseProps })
    expect(wrapper.text()).toContain('resume.md')
  })

  it('renders formatted date', async () => {
    const wrapper = await mountSuspended(ConversionCard, { props: baseProps })
    expect(wrapper.text()).toContain('Jan')
    expect(wrapper.text()).toContain('15')
    expect(wrapper.text()).toContain('2025')
  })

  it('shows Download PDF button for completed status', async () => {
    const wrapper = await mountSuspended(ConversionCard, { props: baseProps })
    expect(wrapper.text()).toContain('Download PDF')
  })

  it('shows Retry button for failed status', async () => {
    const wrapper = await mountSuspended(ConversionCard, {
      props: { ...baseProps, status: 'failed', serverError: 'AI error' },
    })
    expect(wrapper.text()).toContain('Retry')
    expect(wrapper.text()).toContain('AI error')
  })

  it('shows Regenerate button for non-failed statuses', async () => {
    const wrapper = await mountSuspended(ConversionCard, { props: baseProps })
    expect(wrapper.text()).toContain('Regenerate')
  })

  it('always shows Delete button', async () => {
    const wrapper = await mountSuspended(ConversionCard, { props: baseProps })
    expect(wrapper.text()).toContain('Delete')
  })

  it('uses teal border for non-failed status', async () => {
    const wrapper = await mountSuspended(ConversionCard, { props: baseProps })
    const card = wrapper.find('div')
    expect(card.classes().join(' ')).toContain('border-l-cv-teal')
  })

  it('uses red border for failed status', async () => {
    const wrapper = await mountSuspended(ConversionCard, {
      props: { ...baseProps, status: 'failed' },
    })
    const card = wrapper.find('div')
    expect(card.classes().join(' ')).toContain('border-l-cv-error')
  })
})
