/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./bet/templates/**/*.{html,js}"],
  theme: {
<<<<<<< HEAD
    colors: {
      'blue': '#1fb6ff',
      'purple': '#7e5bef',
      'pink': '#ff49db',
      'orange': '#ff7849',
      'green': '#13ce66',
      'yellow': '#ffc82c',
      'gray-dark': '#273444',
      'gray': '#8492a6',
      'gray-light': '#d3dce6',
    },
    fontFamily: {
      sans: ['Graphik', 'sans-serif'],
      serif: ['Merriweather', 'serif'],
    },
    screens: {
      sm: { min: "50px", max: "767px" },
      md: { min: "441px", max: "1023px" },
      lg: { min: "1024px", max: "1279px" },
      xl: { min: "1280px" },
    },
    extend: {
      spacing: {
        '8xl': '96rem',
        '9xl': '128rem',
      },
      borderRadius: {
        '4xl': '2rem',
      }
    }
=======
    extend: {},
>>>>>>> 8261e138f1bd5ec7960e0e14359e59ef58932367
  },
  plugins: [],
}

