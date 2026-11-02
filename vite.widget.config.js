import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist/widget',
    lib: {
      entry: 'src/widget-entry.jsx',
      formats: ['es'],
      fileName: 'support-widget',
      cssFileName: 'support-widget',
    },
    rollupOptions: {
      external: ['react', 'react-dom', 'react/jsx-runtime', 'lucide-react'],
    },
  },
});
