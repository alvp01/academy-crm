/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#F3EEFF',
          100: '#E7E7F4',
          200: '#CFCFFF',
          300: '#C2A1FD',
          400: '#A67BF9',
          500: '#9154FD',
          600: '#7C42E8',
          700: '#6E39CB',
          800: '#5A2DA8',
          900: '#4A2488',
        },
        surface: {
          DEFAULT: '#FFFFFF',
          neutral: '#FFFFFF',
          background: '#F4F5F9',
          background2: '#E7E7F4',
          border: '#DBDCDE',
        },
        text: {
          DEFAULT: '#3A3541',
          light: '#89868D',
          disable: '#B4B2B7',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
      },
      boxShadow: {
        'card': '0 2px 8px rgba(0, 0, 0, 0.04)',
        'elevated': '0 4px 16px rgba(0, 0, 0, 0.08)',
      },
    },
  },
  plugins: [],
};
