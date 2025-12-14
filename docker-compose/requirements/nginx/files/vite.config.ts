import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      '/api': {
        target: 'http://server_flask:8000',
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'http://server_flask:8000',
        changeOrigin: true,
        ws: true,
      }
    }
  }
})
