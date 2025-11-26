import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone", // CRITICAL FOR DOCKER
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
