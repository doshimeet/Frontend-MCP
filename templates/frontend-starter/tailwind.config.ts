import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./packages/recipes/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        nexus: {
          primary: "var(--nexus-color-primary)",
          "primary-hover": "var(--nexus-color-primary-hover)",
          secondary: "var(--nexus-color-secondary)",
          "secondary-hover": "var(--nexus-color-secondary-hover)",
          surface: "var(--nexus-color-surface)",
          "surface-subtle": "var(--nexus-color-surface-subtle)",
          canvas: "var(--nexus-color-canvas)",
          border: "var(--nexus-color-border-subtle)",
          "border-strong": "var(--nexus-color-border-strong)",
          danger: "var(--nexus-color-danger)",
          success: "var(--nexus-color-success)",
          warning: "var(--nexus-color-warning)",
        },
      },
      boxShadow: {
        subtle: "var(--nexus-elevation-subtle)",
        raised: "var(--nexus-elevation-raised)",
        floating: "var(--nexus-elevation-floating)",
      },
      fontFamily: {
        sans: ["var(--nexus-font-sans)", "Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["var(--nexus-font-mono)", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
