import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    strictPort: false,
    proxy: {
      '/api': {
        target: 'http://localhost:8976',
        changeOrigin: true,
        configure: (proxy, options) => {
          proxy.on('error', (err, req, res) => {
            console.log('[proxy error]', err.message)
            if (!res.headersSent) {
              res.writeHead(502, { 'Content-Type': 'application/json' })
              res.end(JSON.stringify({ status: 'error', message: 'Backend unavailable' }))
            }
          })
          proxy.on('proxyReq', (proxyReq, req, res) => {
            if (req.url) {
              console.log(`[proxy] ${req.method} ${req.url}`)
            }
          })
        }
      },
      '/ws': {
        target: 'ws://localhost:8976',
        ws: true,
        configure: (proxy) => {
          proxy.on('error', (err) => {
            console.log('[ws proxy] connection error:', err.message)
          })
        }
      }
    }
  }
})
