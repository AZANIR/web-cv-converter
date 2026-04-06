import { describe, it, expect, vi } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import VacancyInputForm from '~/components/VacancyInputForm.vue'

describe('VacancyInputForm', () => {
  it('renders three tabs', async () => {
    const wrapper = await mountSuspended(VacancyInputForm)
    const text = wrapper.text()
    expect(text).toContain('Text')
    expect(text).toContain('URL')
    expect(text).toContain('File')
  })

  it('shows textarea on text tab by default', async () => {
    const wrapper = await mountSuspended(VacancyInputForm)
    const textarea = wrapper.find('textarea')
    expect(textarea.exists()).toBe(true)
    expect(textarea.attributes('placeholder')).toContain('Paste the vacancy')
  })

  it('switches to URL tab', async () => {
    const wrapper = await mountSuspended(VacancyInputForm)
    const tabs = wrapper.findAll('button')
    const urlTab = tabs.find(t => t.text() === 'URL')
    expect(urlTab).toBeTruthy()
    await urlTab!.trigger('click')
    const input = wrapper.find('input[type="url"]')
    expect(input.exists()).toBe(true)
  })

  it('switches to File tab', async () => {
    const wrapper = await mountSuspended(VacancyInputForm)
    const tabs = wrapper.findAll('button')
    const fileTab = tabs.find(t => t.text() === 'File')
    expect(fileTab).toBeTruthy()
    await fileTab!.trigger('click')
    expect(wrapper.text()).toContain('Drop your file here')
  })

  it('submit is disabled without input', async () => {
    const wrapper = await mountSuspended(VacancyInputForm)
    const submitBtn = wrapper.findAll('button').find(b => b.text() === 'Generate CV')
    expect(submitBtn).toBeTruthy()
    expect(submitBtn!.attributes('disabled')).toBeDefined()
  })

  it('emits submit event with text data', async () => {
    const wrapper = await mountSuspended(VacancyInputForm)
    const textarea = wrapper.find('textarea')
    await textarea.setValue('Senior QA Engineer needed')
    const submitBtn = wrapper.findAll('button').find(b => b.text() === 'Generate CV')
    await submitBtn!.trigger('click')
    expect(wrapper.emitted('submit')).toBeTruthy()
    const payload = wrapper.emitted('submit')![0][0] as { type: string; text: string }
    expect(payload.type).toBe('text')
    expect(payload.text).toBe('Senior QA Engineer needed')
  })
})
