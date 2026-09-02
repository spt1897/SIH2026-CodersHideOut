import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite' 

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    // Allows any tunnel host (recommended for active development)
    allowedHosts: true,
    
    // Alternatively, strictly allow only today's specific URL:
    // allowedHosts: ['chatty-knives-jump.loca.lt'],
  }
})