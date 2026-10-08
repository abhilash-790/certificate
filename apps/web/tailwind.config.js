/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          800: '#1E293B',
          900: '#0F172A',
        },
        teal: {
          600: '#0D9488',
          700: '#0F766E',
        },
        verified: {
          DEFAULT: '#059669',
          bg: '#ECFDF5',
        },
        warning: {
          DEFAULT: '#D97706',
          bg: '#FFFBEB',
        },
        danger: {
          DEFAULT: '#DC2626',
          bg: '#FEF2F2',
        },
        revoked: {
          DEFAULT: '#991B1B',
          bg: '#FEE2E2',
        }
      },
    },
  },
  plugins: [],
}
