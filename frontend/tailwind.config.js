/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // A calm clinical palette -- deep teal for trust/focus, warm sand
        // for warmth (this is a wellness tool, not a hospital chart),
        // and dedicated risk colors so low/moderate/high always read the
        // same way anywhere in the app.
        ink: '#12241F',
        teal: {
          50: '#EEF6F4',
          100: '#D5E9E4',
          400: '#3E8A7C',
          600: '#1F6357',
          700: '#164A41',
          900: '#0B2B26',
        },
        sand: {
          50: '#FBF8F3',
          100: '#F3EDE1',
        },
        risk: {
          low: '#2F9E6E',
          moderate: '#D98E2F',
          high: '#C4472C',
        },
      },
      fontFamily: {
        display: ['"Fraunces"', 'Georgia', 'serif'],
        body: ['"Inter"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
