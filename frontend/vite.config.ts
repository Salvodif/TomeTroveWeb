// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // You can specify the port for the frontend dev server
    proxy: {
      // Proxy /api requests to the backend server running on port 5001
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true, // Needed for virtual hosted sites
        secure: false,      // If backend is not https
        // rewrite: (path) => path.replace(/^\/api/, '') // Use if your backend doesn't expect /api prefix
      }
    }
  }
})
