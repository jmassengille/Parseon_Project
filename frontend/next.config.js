const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost'],
    unoptimized: process.env.NODE_ENV === 'production', // For static exports
  },
  env: {
    // Environment variables here will be available on both server and client
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || "http://localhost:8000",
    
    // Redis Configuration
    REDIS_HOST: process.env.REDIS_HOST,
    REDIS_PORT: process.env.REDIS_PORT,
    REDIS_PASSWORD: process.env.REDIS_PASSWORD,

    // Security Settings
    NEXT_PUBLIC_MAX_REQUESTS_PER_MIN: process.env.NEXT_PUBLIC_MAX_REQUESTS_PER_MIN,
    NEXT_PUBLIC_MAX_TOKENS_PER_REQUEST: process.env.NEXT_PUBLIC_MAX_TOKENS_PER_REQUEST,

    // OpenAI Configuration
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
    OPENAI_ORG_ID: process.env.OPENAI_ORG_ID,

    // Feature Flags - Setting defaults for production
    NEXT_PUBLIC_ENABLE_TEST_MODE: process.env.NEXT_PUBLIC_ENABLE_TEST_MODE || "false",
    NEXT_PUBLIC_ENABLE_MOCK_API: process.env.NEXT_PUBLIC_ENABLE_MOCK_API || "true", // Default to true to ensure the app works even without backend
    NEXT_PUBLIC_ENABLE_ANALYTICS: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS || "false",
    NEXT_PUBLIC_ENABLE_ERROR_REPORTING: process.env.NEXT_PUBLIC_ENABLE_ERROR_REPORTING || "false",
  },
  // For API route handling
  async rewrites() {
    return [
      // Proxy API requests to backend in development (not needed in production)
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_PROXY_API === 'true' 
          ? `${process.env.NEXT_PUBLIC_API_URL}/api/:path*` 
          : '/api/:path*',
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET,DELETE,PATCH,POST,PUT' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version' },
        ],
      },
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: `
              default-src 'self';
              script-src 'self' 'unsafe-inline' 'unsafe-eval';
              style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
              font-src 'self' https://fonts.gstatic.com data:;
              img-src 'self' data: https:;
              connect-src 'self' ${process.env.NEXT_PUBLIC_API_URL || ''} https://fonts.googleapis.com https://fonts.gstatic.com;
              frame-src 'self';
              object-src 'none';
              base-uri 'self';
              form-action 'self';
            `.replace(/\s+/g, ' ').trim()
          }
        ]
      }
    ];
  },
  // Add experimental features for better performance
  experimental: {
    scrollRestoration: true,
  },
  // Add webpack configuration for better bundle optimization
  webpack: (config, { dev, isServer }) => {
    // Ensure consistent path resolution
    config.resolve = {
      ...config.resolve,
      alias: {
        ...config.resolve.alias,
        '@': path.join(__dirname, 'src'),
      },
    };
    
    // Optimize bundle size
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        minSize: 20000,
        maxSize: 244000,
        minChunks: 1,
        maxAsyncRequests: 30,
        maxInitialRequests: 30,
        cacheGroups: {
          defaultVendors: {
            test: /[\\/]node_modules[\\/]/,
            priority: -10,
            reuseExistingChunk: true,
          },
          default: {
            minChunks: 2,
            priority: -20,
            reuseExistingChunk: true,
          },
        },
      };
    }
    return config;
  },
};

module.exports = nextConfig; 