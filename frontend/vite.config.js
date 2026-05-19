import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const isProduction = mode === 'production'

  return {
    plugins: [vue()],
    server: {
      port: 5173,
      strictPort: false,
      proxy: {
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8976',
          changeOrigin: true,
          configure: (proxy) => {
            proxy.on('error', (err) => {
              console.log('[proxy error]', err.message)
            })
          }
        },
        '/ws': {
          target: (env.VITE_API_URL || 'http://localhost:8976').replace('http', 'ws'),
          ws: true,
          configure: (proxy) => {
            proxy.on('error', (err) => {
              console.log('[ws proxy] connection error:', err.message)
            })
          }
        }
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: false
    }
  }
})
