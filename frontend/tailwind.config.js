/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#333333',
        secondary: '#4472C4',
        accent: '#666666',
        muted: '#999999',
        border: '#E0E0E0',
        background: '#F5F5F5',
      }
    },
  },
  plugins: [],
}
