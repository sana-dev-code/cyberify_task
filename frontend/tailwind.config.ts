import type { Config } from 'tailwindcss'
import forms from '@tailwindcss/forms'

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        chat: {
          bg: '#212121',
          sidebar: '#171717',
          panel: '#2f2f2f',
          border: '#424242',
          muted: '#9b9b9b',
        },
      },
    },
  },
  plugins: [forms],
}

export default config
