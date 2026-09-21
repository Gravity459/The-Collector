/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Allow overriding the build output dir (used to build while `next dev` holds .next).
  distDir: process.env.NEXT_DIST_DIR || ".next",
};

export default nextConfig;
