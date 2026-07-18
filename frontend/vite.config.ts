import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  base: process.env.GITHUB_PAGES === "true" ? "/sentinel/" : "/",
  plugins: [react()],
  server: { port: 5173 },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test.setup.ts",
    include: ["src/**/*.test.{ts,tsx}"],
    pool: "forks",
    poolOptions: {
      forks: {
        singleFork: true
      }
    }
  }
});
