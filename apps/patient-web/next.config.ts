import type { NextConfig } from "next";
import { browserSecurityHeaders } from "@swasthyasetu/ui/security-headers";

const securityHeaders = browserSecurityHeaders(process.env.NODE_ENV === "production");

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1"],
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [...securityHeaders],
      },
      {
        source: "/sw.js",
        headers: [
          { key: "Cache-Control", value: "no-cache" },
          { key: "Service-Worker-Allowed", value: "/" },
        ],
      },
    ];
  },
  reactStrictMode: true,
  transpilePackages: ["@swasthyasetu/ui"],
};

export default nextConfig;
