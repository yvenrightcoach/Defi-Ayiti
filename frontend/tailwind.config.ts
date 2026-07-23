import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Identite visuelle Defi Ayiti
        haiti: {
          blue: "#0057B8",
          red: "#D21034",
          yellow: "#FFD447",
          green: "#4CAF50",
          white: "#FFFFFF",
        },
        // Ligues (Bronze -> Champion National)
        league: {
          bronze: "#B0723C",
          silver: "#B9C1CC",
          gold: "#F2B705",
          platinum: "#7FD8DE",
          diamond: "#5AC8FA",
          master: "#8E44AD",
          champion: "#D21034",
        },
      },
      fontFamily: {
        display: ["Baloo 2", "Nunito", "system-ui", "sans-serif"],
        body: ["Nunito", "system-ui", "sans-serif"],
      },
      borderRadius: {
        card: "1.5rem",
        pill: "9999px",
      },
      boxShadow: {
        card: "0 8px 24px rgba(0, 87, 184, 0.15)",
        "card-hover": "0 12px 32px rgba(0, 87, 184, 0.25)",
        glow: "0 0 24px rgba(255, 212, 71, 0.6)",
      },
      keyframes: {
        "pop-in": {
          "0%": { transform: "scale(0.7)", opacity: "0" },
          "70%": { transform: "scale(1.05)", opacity: "1" },
          "100%": { transform: "scale(1)" },
        },
        "coin-bounce": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" },
        },
      },
      animation: {
        "pop-in": "pop-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)",
        "coin-bounce": "coin-bounce 1.2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
