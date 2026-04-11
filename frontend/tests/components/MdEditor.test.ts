import { describe, it, expect, vi } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import MdEditor from '~/components/MdEditor.vue'

describe('MdEditor', () => {
  it('renders split view with two panels', async () => {
    const wrapper = await mountSuspended(MdEditor, {
      props: { modelValue: '# Hello' },
    })
    expect(wrapper.text()).toContain('Markdown')
    expect(wrapper.text()).toContain('Preview')
    const textarea = wrapper.find('textarea')
    expect(textarea.exists()).toBe(true)
  })

  it('shows initial content in textarea', async () => {
    const wrapper = await mountSuspended(MdEditor, {
      props: { modelValue: '# My CV' },
    })
    const textarea = wrapper.find('textarea')
    expect((textarea.element as HTMLTextAreaElement).value).toBe('# My CV')
  })

  it('renders markdown preview', async () => {
    const wrapper = await mountSuspended(MdEditor, {
      props: { modelValue: '**bold text**' },
    })
    const preview = wrapper.find('.prose')
    expect(preview.exists()).toBe(true)
    expect(preview.html()).toContain('<strong>bold text</strong>')
  })

  it('emits save on button click', async () => {
    const wrapper = await mountSuspended(MdEditor, {
      props: { modelValue: '# Test' },
    })
    const saveBtn = wrapper.findAll('button').find(b => b.text() === 'Save')
    expect(saveBtn).toBeTruthy()
    await saveBtn!.trigger('click')
    expect(wrapper.emitted('save')).toBeTruthy()
    expect(wrapper.emitted('save')![0][0]).toBe('# Test')
  })

  it('hides save button in readonly mode', async () => {
    const wrapper = await mountSuspended(MdEditor, {
      props: { modelValue: '# Test', readonly: true },
    })
    const saveBtn = wrapper.findAll('button').find(b => b.text() === 'Save')
    expect(saveBtn).toBeUndefined()
  })

  describe('XSS sanitization', () => {
    it('strips script tags from rendered markdown', async () => {
      const wrapper = await mountSuspended(MdEditor, {
        props: { modelValue: '<script>alert("XSS")</script>' },
      })
      const preview = wrapper.find('.prose')
      // MarkdownIt escapes HTML by default; DOMPurify provides defense-in-depth
      expect(preview.html()).not.toContain('<script>')
    })

    it('strips onerror from img tags', async () => {
      const wrapper = await mountSuspended(MdEditor, {
        props: { modelValue: '<img onerror=alert("XSS") src=x>' },
      })
      const preview = wrapper.find('.prose')
      // Verify no raw onerror attribute is present in actual DOM elements
      const imgs = preview.findAll('img')
      imgs.forEach((img) => {
        expect(img.attributes('onerror')).toBeUndefined()
      })
    })

    it('preserves safe markdown links', async () => {
      const wrapper = await mountSuspended(MdEditor, {
        props: { modelValue: '[Example](https://example.com)' },
      })
      const preview = wrapper.find('.prose')
      expect(preview.html()).toContain('href="https://example.com"')
      expect(preview.html()).toContain('Example')
    })

    it('does not render javascript: protocol as link href', async () => {
      const wrapper = await mountSuspended(MdEditor, {
        props: { modelValue: '[click me](javascript:alert("XSS"))' },
      })
      const preview = wrapper.find('.prose')
      const links = preview.findAll('a')
      links.forEach((link) => {
        expect(link.attributes('href') ?? '').not.toContain('javascript:')
      })
    })
  })
})
