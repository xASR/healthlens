/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#12241F',
        teal: {
          50: '#EEF6F4',
          100: '#D5E9E4',
          400: '#3E8A7C',
          600: '#1F6357',
          700: '#164A41',
          900: '#0B2B26',
        },
        // Kept so any page still using sand classes doesn't break.
        sand: {
          50: '#FBF8F3',
          100: '#F3EDE1',
        },
        // Cool, faintly teal page canvas. Glass needs a background with
        // some color variation behind it to read as glass at all.
        canvas: '#EEF3F2',
        risk: {
          low: '#2F9E6E',
          moderate: '#D98E2F',
          high: '#C4472C',
        },
      },
      fontFamily: {
        // System stack first: SF Pro on Apple devices, Inter elsewhere.
        display: [
          '-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"',
          '"Inter"', 'system-ui', 'sans-serif',
        ],
        body: [
          '-apple-system', 'BlinkMacSystemFont', '"SF Pro Text"',
          '"Inter"', 'system-ui', 'sans-serif',
        ],
      },
      boxShadow: {
        // 1px inner top highlight + soft, low-contrast drop.
        glass:
          'inset 0 1px 0 0 rgba(255,255,255,0.75), 0 1px 2px rgba(18,36,31,0.04), 0 12px 32px -16px rgba(18,36,31,0.22)',
        thumb: '0 3px 8px rgba(0,0,0,0.15), 0 1px 1px rgba(0,0,0,0.16)',
        segment: '0 1px 3px rgba(18,36,31,0.12), 0 0 0 0.5px rgba(18,36,31,0.06)',
      },
      transitionTimingFunction: {
        apple: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
        spring: 'cubic-bezier(0.32, 0.72, 0, 1)',
      },
    },
  },
  plugins: [],
}
