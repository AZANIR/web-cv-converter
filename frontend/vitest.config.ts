import { defineVitestConfig } from '@nuxt/test-utils/config'

export default defineVitestConfig({
  test: {
    environment: 'nuxt',
    environmentOptions: {
      nuxt: {
        domEnvironment: 'happy-dom',
      },
    },
    reporters: ['default', 'json'],
    outputFile: {
      json: '../test-reports/frontend/results.json',
    },
  },
})
