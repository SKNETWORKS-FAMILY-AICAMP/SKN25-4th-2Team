import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

const djangoTarget = "http://arxplore-django:8001";

export default defineConfig(({ command }) => ({
  base: command === "serve" ? "/" : "/static/frontend/",
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/bootstrap.json": djangoTarget,
      "/auth/": djangoTarget,
      "/settings/": djangoTarget,
      "/favorites/": djangoTarget,
      "/papers/list.json": djangoTarget,
      "/papers/assistant/chat/": djangoTarget,
      "^/papers/[^/]+/detail\\.json$": djangoTarget,
      "^/papers/[^/]+/analyze/$": djangoTarget,
      "^/papers/[^/]+/summary/$": djangoTarget,
      "^/papers/[^/]+/chat/$": djangoTarget,
      "/admin/": djangoTarget,
      "/static/": djangoTarget
    }
  }
}));
