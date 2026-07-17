import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        // Backend único: puerto 8001
        destination: "http://127.0.0.1:8001/api/:path*",
      },
    ]
  },
}

export default nextConfig
