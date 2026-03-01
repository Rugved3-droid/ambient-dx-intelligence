/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        clinical: {
          bg: '#0a0e17',
          surface: '#111827',
          border: '#1e293b',
          'border-light': '#334155',
          critical: '#ef4444',
          warning: '#f59e0b',
          normal: '#22c55e',
          info: '#3b82f6',
          text: '#f8fafc',
          'text-muted': '#94a3b8',
        },
      },
      animation: {
        'pulse-alert': 'pulse-alert 1.5s ease-in-out infinite',
        'slide-in': 'slide-in 0.4s ease-out',
        'fade-in': 'fade-in 0.3s ease-out',
      },
      keyframes: {
        'pulse-alert': {
          '0%, 100%': { borderColor: '#ef4444', boxShadow: '0 0 20px rgba(239, 68, 68, 0.3)' },
          '50%': { borderColor: '#fbbf24', boxShadow: '0 0 40px rgba(239, 68, 68, 0.6)' },
        },
        'slide-in': {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
