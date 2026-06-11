export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#071019",
        surface: "#101c2a",
        panel: "#152437",
        primary: "#4fc3f7",
        positive: "#62c48a",
        negative: "#de6b73",
        warning: "#d9a441",
        neutral: "#94a3b8",
        ai: "#a78bfa"
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
        mono: ["JetBrains Mono", "ui-monospace", "SFMono-Regular"]
      }
    }
  },
  plugins: []
};

