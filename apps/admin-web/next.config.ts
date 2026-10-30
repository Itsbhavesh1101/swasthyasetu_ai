import type { NextConfig } from "next";
import { browserSecurityHeaders } from "@swasthyasetu/ui/security-headers";

const securityHeaders = browserSecurityHeaders(process.env.NODE_ENV === "production");

const nextConfig: NextConfig = {
  async headers() {
    return [{ source: "/:path*", headers: [...securityHeaders] }];
  },
  reactStrictMode: true,
  transpilePackages: ["@swasthyasetu/ui"],
};

export default nextConfig;
