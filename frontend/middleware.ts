import createMiddleware from 'next-intl/middleware';
import { locales, defaultLocale } from './i18n/config';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const intlMiddleware = createMiddleware({
  // A list of all locales that are supported
  locales,

  // Used when no locale matches
  defaultLocale,

  // Always show the locale prefix to avoid redirect issues
  localePrefix: 'always'
});

export default function middleware(request: NextRequest) {
  const response = intlMiddleware(request);

  // Add CSP headers - Allow connections to backend and Google OAuth
  const cspHeader = `
    default-src 'self';
    script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://accounts.google.com https://apis.google.com;
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://accounts.google.com;
    img-src 'self' blob: data: https: http:;
    font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net data:;
    connect-src 'self' http://localhost:8000 https://peykantravelistanbul.com https://www.peykantravelistanbul.com https://accounts.google.com https://oauth2.googleapis.com https://www.googleapis.com wss://peykantravelistanbul.com ws://localhost:3000;
    media-src 'self' blob: data: http://localhost:8000 https://peykantravelistanbul.com https://www.peykantravelistanbul.com;
    frame-src 'self' https://accounts.google.com;
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
  `.replace(/\s{2,}/g, ' ').trim();

  response.headers.set('Content-Security-Policy', cspHeader);

  return response;
}

export const config = {
  // Match all pathnames except for
  // - /api (API routes)
  // - /_next (Next.js internals)
  // - /_vercel (Vercel internals)
  // - /static (static files)
  matcher: ['/((?!api|_next|_vercel|static|.*\\..*).*)']
}; 