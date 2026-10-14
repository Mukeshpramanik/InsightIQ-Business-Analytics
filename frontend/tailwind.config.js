/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          800: '#1a2234',
          900: '#0f172a',
          950: '#090d16',
        },
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        accent: {
          teal: '#0d9488',
          cyan: '#06b6d4',
          indigo: '#4f46e5',
          amber: '#d97706',
          emerald: '#059669',
          rose: '#e11d48'
        }
      }
    },
  },
  plugins: [],
}
