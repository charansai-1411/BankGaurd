/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#060709',
        surface: '#0b0d11',
        borderCustom: '#1a2030',
        gold: '#e8c547',
        teal: '#4fc9a4',
        red: '#e05c5c',
        blue: '#7eb8f7',
      },
      fontFamily: {
        mono: ['"IBM Plex Mono"', 'monospace'],
        sans: ['"IBM Plex Sans"', 'sans-serif'],
        serif: ['"DM Serif Display"', 'serif'],
      },
      borderRadius: {
        sm: '2px',
        md: '2px',
        lg: '2px',
      },
    },
  },
  plugins: [],
}
