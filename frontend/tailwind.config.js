/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-dark': '#0F0F1A',
        'card-bg': '#1A1A2E',
        'primary-start': '#6C63FF',
        'primary-end': '#3B82F6',
      },
    },
  },
  plugins: [],
}
