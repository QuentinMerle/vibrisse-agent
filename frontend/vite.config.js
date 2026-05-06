import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: [
            'react', 
            'react-dom', 
            'lucide-react', 
            'react-markdown', 
            'remark-gfm', 
            'i18next', 
            'react-i18next',
            'i18next-browser-languagedetector'
          ],
        },
      },
    },
    chunkSizeWarningLimit: 1000, // On augmente un peu la limite car on assume nos dépendances
  },
})
