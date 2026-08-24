/** @type {import('tailwindcss').Config} */
const config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: "#fbfaf7",
        surface: "#ffffff",
        subtle: "#f6f3eb",
        ink: {
          900: "#1c1917",
          700: "#44403c",
          500: "#78716c",
          300: "#d6d3d1",
          100: "#eae5d9",
        },
        academic: {
          DEFAULT: "#1e3a8a",
          hover: "#172554",
          light: "#eff6ff",
          border: "#bfdbfe",
        },
      },
      fontFamily: {
        serif: ["var(--font-serif)", "Newsreader", "Lora", "Georgia", "serif"],
        sans: ["var(--font-sans)", "Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "SF Mono", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
