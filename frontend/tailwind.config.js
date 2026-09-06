/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#0F1115",
        surface: "#171A21",
        surfaceRaised: "#1D212B",
        border: "#262B36",
        textPrimary: "#E4E7EC",
        textMuted: "#8B93A7",
        accent: "#5B8DEF",
        accentMuted: "#3A5FA8",
        success: "#3FB950",
        fail: "#F85149",
        warning: "#D29922",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      borderRadius: {
        DEFAULT: "4px",
      },
    },
  },
  plugins: [],
};
