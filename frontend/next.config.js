/** @type {import('next').NextConfig} */
const nextConfig = {
  // App Router is now stable in Next.js 14, no experimental config needed
  webpack: (config, { isServer }) => {
    // Handle canvas module for PDF.js
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        canvas: false,
        fs: false,
      };
    }
    
    // Handle PDF.js worker
    config.resolve.alias = {
      ...config.resolve.alias,
      canvas: false,
    };

    return config;
  },
  async rewrites() {
    return [
      // Proxy API calls to backend server
      {
        source: '/api/folder-watcher/:path*',
        destination: 'http://localhost:8000/api/folder-watcher/:path*',
      },
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/invoices/:path*',
        destination: 'http://localhost:8000/invoices/:path*',
      },
      {
        source: '/ocr/:path*',
        destination: 'http://localhost:8000/ocr/:path*',
      },
      {
        source: '/upload/:path*',
        destination: 'http://localhost:8000/upload/:path*',
      },
    ];
  },
}

module.exports = nextConfig
