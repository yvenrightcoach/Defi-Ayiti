import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Identite visuelle Defi Ayiti
        haiti: {
          blue: "#0057B8",
          blueDark: "#003D82",
          blueLight: "#EAF3FF",
          red: "#D21034",
          redDark: "#A10D28",
          yellow: "#FFD447",
          yellowDark: "#E5A100",
          green: "#4CAF50",
          greenDark: "#357A38",
          white: "#FFFFFF",
          cream: "#FFF8E7",
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
        card: "1.75rem",
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
        float: {
          "0%, 100%": { transform: "translateY(0) rotate(-2deg)" },
          "50%": { transform: "translateY(-10px) rotate(2deg)" },
        },
        wiggle: {
          "0%, 100%": { transform: "rotate(-4deg)" },
          "50%": { transform: "rotate(4deg)" },
        },
        "bounce-in": {
          "0%": { transform: "scale(0.3) translateY(40px)", opacity: "0" },
          "60%": { transform: "scale(1.08) translateY(-6px)", opacity: "1" },
          "80%": { transform: "scale(0.96) translateY(2px)" },
          "100%": { transform: "scale(1) translateY(0)" },
        },
        "wave-slide": {
          "0%": { backgroundPositionX: "0" },
          "100%": { backgroundPositionX: "-200px" },
        },
      },
      animation: {
        "pop-in": "pop-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)",
        "coin-bounce": "coin-bounce 1.2s ease-in-out infinite",
        float: "float 3.5s ease-in-out infinite",
        wiggle: "wiggle 0.6s ease-in-out infinite",
        "bounce-in": "bounce-in 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)",
      },
    },
  },
  plugins: [],
} satisfies Config;
