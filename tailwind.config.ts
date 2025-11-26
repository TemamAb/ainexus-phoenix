import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // THE GRAFANA PALETTE
        grafana: {
          bg: "#111217",       // Deep Background
          panel: "#181b1f",    // Card Background
          border: "#22252b",   // Subtle Borders
          blue: "#5794F2",     // Primary Action
          green: "#00FF9D",    // Success/Live
          red: "#F2495C",      // Alert/Security
          amber: "#FF9900"     // Warning/Speed
        }
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      },
      animation: {
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
};
export default config;
