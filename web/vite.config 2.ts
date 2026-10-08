import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// W1 web — static SPA, deployed to Vercel.
export default defineConfig({
  plugins: [react()],
});
