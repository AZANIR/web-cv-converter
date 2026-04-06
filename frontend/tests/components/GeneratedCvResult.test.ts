import { describe, it, expect, vi } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import GeneratedCvResult from '~/components/GeneratedCvResult.vue'

describe('GeneratedCvResult', () => {
  it('shows draft state with convert button', async () => {
    const wrapper = await mountSuspended(GeneratedCvResult, {
      props: { cvId: 'cv-1', status: 'draft' },
    })
    expect(wrapper.text()).toContain('ready to edit or convert')
    expect(wrapper.text()).toContain('Convert to PDF')
  })

  it('shows generating state', async () => {
    const wrapper = await mountSuspended(GeneratedCvResult, {
      props: { cvId: 'cv-1', status: 'generating' },
    })
    expect(wrapper.text()).toContain('Generating CV...')
  })

  it('shows converting state', async () => {
    const wrapper = await mountSuspended(GeneratedCvResult, {
      props: { cvId: 'cv-1', status: 'converting' },
    })
    expect(wrapper.text()).toContain('Converting to PDF...')
  })

  it('shows completed state with download', async () => {
    const wrapper = await mountSuspended(GeneratedCvResult, {
      props: { cvId: 'cv-1', status: 'completed', downloadUrl: 'https://example.com/cv.pdf' },
    })
    expect(wrapper.text()).toContain('PDF is ready!')
    expect(wrapper.text()).toContain('Download PDF')
  })

  it('shows failed state with error', async () => {
    const wrapper = await mountSuspended(GeneratedCvResult, {
      props: { cvId: 'cv-1', status: 'failed', errorMessage: 'Something went wrong' },
    })
    expect(wrapper.text()).toContain('Generation failed')
    expect(wrapper.text()).toContain('Something went wrong')
  })

  it('shows include header toggle', async () => {
    const wrapper = await mountSuspended(GeneratedCvResult, {
      props: { cvId: 'cv-1', status: 'draft' },
    })
    expect(wrapper.text()).toContain('Include header image')
    const toggle = wrapper.find('[role="switch"]')
    expect(toggle.exists()).toBe(true)
    expect(toggle.attributes('aria-checked')).toBe('true')
  })

  it('emits convert event on button click', async () => {
    const wrapper = await mountSuspended(GeneratedCvResult, {
      props: { cvId: 'cv-1', status: 'draft' },
    })
    const convertBtn = wrapper.findAll('button').find(b => b.text().includes('Convert to PDF'))
    await convertBtn!.trigger('click')
    expect(wrapper.emitted('convert')).toBeTruthy()
    expect(wrapper.emitted('convert')![0][0]).toBe(true)
  })

  it('does not show edit button in draft state (already in editor)', async () => {
    const wrapper = await mountSuspended(GeneratedCvResult, {
      props: { cvId: 'cv-1', status: 'draft' },
    })
    const editBtn = wrapper.findAll('button').find(b => b.text().includes('Edit Markdown'))
    expect(editBtn).toBeUndefined()
  })
})
