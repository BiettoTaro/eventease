import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "encrypted-tbn0.gstatic.com", // Google thumbnails
      },
      {
        protocol: "https",
        hostname: "s1.ticketm.net", // Ticketmaster
      },
    ],
  },
  
};

export default nextConfig;
