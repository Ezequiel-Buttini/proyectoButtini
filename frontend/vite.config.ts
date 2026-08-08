import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      '/health': process.env.VITE_BACKEND_URL ?? 'http://localhost:8000',
    },
  },
})
