import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  base: '/the_path_of_all_things/',
  plugins: [tailwindcss()],
})
