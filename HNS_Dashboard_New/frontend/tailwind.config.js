/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#f0f2f5', // Light gray background
        surface: '#ffffff',    // Card and component backgrounds
        primary: '#0052cc',    // Main brand color (blue)
        secondary: '#5E6C84',   // Secondary text, icons
        textPrimary: '#172B4D', // Main text color
        textSecondary: '#5E6C84', // Lighter text
        accent: '#FFAB00',     // For highlights, warnings (amber)
        success: '#36B37E',     // Green for success states
        danger: '#FF5630',      // Red for error states
        border: '#DFE1E6',     // Borders and dividers
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'card-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      }
    },
  },
  plugins: [],
}
