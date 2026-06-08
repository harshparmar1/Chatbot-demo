/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        hospital: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae2fd',
          300: '#7cc8fc',
          400: '#38a9f8',
          500: '#0e8ee9',
          600: '#0270c5',
          700: '#03599f',
          800: '#074c83',
          900: '#0c406e',
          950: '#082949',
        }
      }
    },
  },
  plugins: [],
}
