import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        grafana: {
          bg: "#111217",
          panel: "#181b1f",
          border: "#22252b",
          blue: "#5794F2",
          green: "#73BF69",
          amber: "#F2CC0C",
          red: "#F2495C",
          neon: "#00FF9D"
        }
      },
      fontFamily: {
        mono: ["monospace", "ui-monospace", "SFMono-Regular"]
      }
    },
  },
  plugins: [],
};
export default config;
