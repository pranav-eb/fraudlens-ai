/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        navy:  { 900: '#020B18', 800: '#061224', 700: '#0A1F3A', 600: '#0E2847', 500: '#163360' },
        gold:  { 400: '#F5C842', 500: '#E2AF1E', 600: '#B8891A' },
        cyan:  { 400: '#22D3EE' },
        emerald: { 400: '#34D399' },
        rose:  { 400: '#FB7185', 500: '#F43F5E' },
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up':   'slideUp 0.5s ease forwards',
        'fade-in':    'fadeIn 0.4s ease forwards',
        'shimmer':    'shimmer 2s linear infinite',
      },
      keyframes: {
        slideUp:  { from: { opacity: 0, transform: 'translateY(24px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        fadeIn:   { from: { opacity: 0 }, to: { opacity: 1 } },
        shimmer:  { '0%': { backgroundPosition: '-1000px 0' }, '100%': { backgroundPosition: '1000px 0' } },
      },
    },
  },
  plugins: [],
}
