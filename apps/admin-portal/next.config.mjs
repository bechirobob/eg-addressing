const internalApiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? 'http://api:8100';

const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: `${internalApiBaseUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
