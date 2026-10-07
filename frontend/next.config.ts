import type { NextConfig } from "next";

const API = process.env.API_URL ?? "http://127.0.0.1:8000";
const isDev = process.env.NODE_ENV !== "production";

// Dev: proxy /api to the local FastAPI server.
// Production (Vercel): frontend calls NEXT_PUBLIC_API_URL directly via api.ts
const config: NextConfig = isDev
  ? {
      async rewrites() {
        return [
          { source: "/api/:path*", destination: `${API}/api/:path*` },
          { source: "/docs", destination: `${API}/docs` },
          { source: "/openapi.json", destination: `${API}/openapi.json` },
        ];
      },
    }
  : {};

export default config;
