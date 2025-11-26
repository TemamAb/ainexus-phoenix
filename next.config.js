/** @type {import('next').NextConfig} */
const nextConfig = {
  // output: "standalone", <-- DISABLED FOR STABILITY
  reactStrictMode: true,
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },
};
module.exports = nextConfig;
