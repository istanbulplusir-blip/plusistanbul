import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./i18n/request.js');
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/** @type {import('next').NextConfig} */
const nextConfig = {
  outputFileTracingRoot: __dirname,
  // Disable ESLint during build
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Disable experimental features that might cause ReactDOM.preload warnings
  experimental: {
    // Disable scroll behavior warning
    scrollRestoration: false,
  },

  images: {
    // Image optimization settings
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days
    qualities: [25, 50, 75, 85, 90, 100], // Add quality options for Next.js 15
    
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'picsum.photos',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'peykantravelistanbul.com',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'www.peykantravelistanbul.com',
        port: '',
        pathname: '/**',
      },
      // Media files from Django backend
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/media/**',
      },
      {
        protocol: 'https',
        hostname: 'peykantravelistanbul.com',
        port: '',
        pathname: '/media/**',
      },
      {
        protocol: 'https',
        hostname: 'www.peykantravelistanbul.com',
        port: '',
        pathname: '/media/**',
      },
    ],
    
    // Image optimization settings
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  
  async rewrites() {
    // Use environment variable to determine API URL
    const apiUrl = process.env.NODE_ENV === 'production' 
      ? 'https://peykantravelistanbul.com'  // دامنه اصلی
      : 'http://localhost:8000'; // Local development
    
    console.log('Next.js API URL:', apiUrl);
    
    return [
      // Specific API routes first (more specific routes should come first)
      {
        source: '/api/v1/shared/contact-info',
        destination: `${apiUrl}/api/v1/shared/contact-info`,
      },
      {
        source: '/api/v1/shared/contact-info/',
        destination: `${apiUrl}/api/v1/shared/contact-info/`,
      },
      {
        source: '/api/v1/shared/support-faqs',
        destination: `${apiUrl}/api/v1/shared/support-faqs`,
      },
      {
        source: '/api/v1/shared/support-faqs/',
        destination: `${apiUrl}/api/v1/shared/support-faqs/`,
      },
      {
        source: '/api/v1/shared/whatsapp-info',
        destination: `${apiUrl}/api/v1/shared/whatsapp-info`,
      },
      {
        source: '/api/v1/shared/whatsapp-info/',
        destination: `${apiUrl}/api/v1/shared/whatsapp-info/`,
      },
      // General API routes - preserve trailing slash
      {
        source: '/api/v1/:path*/',
        destination: `${apiUrl}/api/v1/:path*/`,
      },
      {
        source: '/api/v1/:path*',
        destination: `${apiUrl}/api/v1/:path*`,
      },
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
      // Add specific rewrites for events and tours
      {
        source: '/api/v1/events/:path*',
        destination: `${apiUrl}/api/v1/events/:path*`,
      },
      {
        source: '/api/v1/tours/:path*',
        destination: `${apiUrl}/api/v1/tours/:path*`,
      },
      // Proxy media files (served by Django) so <img src="/media/..."> works in Next
      {
        source: '/media/:path*',
        destination: `${apiUrl}/media/:path*`,
      },
    ];
  },
  
  // Enable trailing slash for API routes to match Django expectations
  trailingSlash: true,
};

export default withNextIntl(nextConfig); 