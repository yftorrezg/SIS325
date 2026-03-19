/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        usfx: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#1e40af',
          600: '#1d4ed8',
          700: '#1e3a8a',
          800: '#1e3a8a',
          900: '#172554',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
