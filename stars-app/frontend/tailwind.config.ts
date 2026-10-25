import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          red: "#F26722",
          teal: "#1D9E75",
          amber: "#d97706",
          navy: "#1e293b",
          dark: "#0f172a",
          card: "#1e2a3a",
          border: "#2d3e52",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
