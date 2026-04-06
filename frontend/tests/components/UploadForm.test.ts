import { describe, it, expect, vi } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import UploadForm from '~/components/UploadForm.vue'

describe('UploadForm', () => {
  it('renders the heading', async () => {
    const wrapper = await mountSuspended(UploadForm)
    expect(wrapper.text()).toContain('Convert Your CV')
  })

  it('renders the drop zone when no file is selected', async () => {
    const wrapper = await mountSuspended(UploadForm)
    expect(wrapper.text()).toContain('Drag & drop your .md file here')
  })

  it('shows the include header toggle', async () => {
    const wrapper = await mountSuspended(UploadForm)
    expect(wrapper.text()).toContain('Include header image')
    const toggle = wrapper.find('[role="switch"]')
    expect(toggle.exists()).toBe(true)
    expect(toggle.attributes('aria-checked')).toBe('true')
  })

  it('toggles include header on click', async () => {
    const wrapper = await mountSuspended(UploadForm)
    const toggle = wrapper.find('[role="switch"]')
    await toggle.trigger('click')
    expect(toggle.attributes('aria-checked')).toBe('false')
  })

  it('shows convert button text', async () => {
    const wrapper = await mountSuspended(UploadForm)
    expect(wrapper.text()).toContain('Convert to PDF')
  })
})
