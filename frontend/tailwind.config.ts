import type { Config } from "tailwindcss";

// Every colour resolves to a CSS variable in app/globals.css (light on :root,
// dark on .dark). Use these token classes; never raw zinc/blue palettes.
const token = (name: string) => `rgb(var(--${name}) / <alpha-value>)`;

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: token("bg"),
        surface: { DEFAULT: token("surface"), 2: token("surface-2") },
        border: { DEFAULT: token("border"), strong: token("border-strong") },
        fg: {
          DEFAULT: token("fg"),
          muted: token("fg-muted"),
          subtle: token("fg-subtle"),
        },
        "on-fg": token("on-fg"),
        success: { DEFAULT: token("success"), bg: token("success-bg") },
        pending: { DEFAULT: token("pending"), bg: token("pending-bg") },
        danger: { DEFAULT: token("danger"), bg: token("danger-bg") },
        "role-admin": { DEFAULT: token("role-admin"), bg: token("role-admin-bg") },
        "role-collector": {
          DEFAULT: token("role-collector"),
          bg: token("role-collector-bg"),
        },
        "role-user": { DEFAULT: token("role-user"), bg: token("role-user-bg") },
        // Reserved for upcoming charts; not used by any component yet.
        chart: { 1: token("chart-1") },
      },
      fontFamily: {
        sans: ["var(--font-geist)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1rem" }],
        sm: ["0.8125rem", { lineHeight: "1.25rem" }],
        base: ["0.875rem", { lineHeight: "1.375rem" }],
        md: ["1rem", { lineHeight: "1.5rem" }],
        lg: ["1.25rem", { lineHeight: "1.75rem" }],
        kpi: ["1.75rem", { lineHeight: "2.125rem" }],
      },
      borderRadius: {
        control: "6px",
        panel: "8px",
        dialog: "12px",
      },
    },
  },
  plugins: [],
};

export default config;
