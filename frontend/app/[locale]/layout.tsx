import '../globals.css';
import { ReactNode } from 'react';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { Metadata } from 'next';
import { AuthProvider } from '../../lib/contexts/AuthContext';
import { UnifiedCartProvider } from '../../lib/contexts/UnifiedCartContext';
import { ThemeProvider } from '../../lib/contexts/ThemeContext';
import { ToastProvider } from '../../components/Toast';
import { UnifiedCurrencyProvider } from '../../lib/contexts/UnifiedCurrencyContext';
import { UnifiedLanguageProvider } from '../../lib/contexts/UnifiedLanguageContext';
import AppWrapper from '../../components/layout/AppWrapper';


interface LayoutProps {
  children: ReactNode;
  params: Promise<{ locale: string }>;
}

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: 'Peykan Tourism Platform',
    description: 'Book tours, events, and transfers with ease',
    metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
    icons: {
      icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🎭</text></svg>',
    },
    robots: {
      index: true,
      follow: true,
    },
    openGraph: {
      title: 'Peykan Tourism Platform',
      description: 'Book tours, events, and transfers with ease',
      type: 'website',
    },
  };
}

export const viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default async function LocaleLayout({ children, params }: LayoutProps) {
  const { locale } = await params;
  const messages = await getMessages({ locale });

  return (
    <html lang={locale} dir={locale === 'fa' ? 'rtl' : 'ltr'} data-scroll-behavior="smooth">
      <body className="bg-white text-gray-900 dark:bg-gray-900 dark:text-white min-h-screen">
        <NextIntlClientProvider locale={locale} messages={messages}>
          <ThemeProvider>
            <AuthProvider>
              <UnifiedCurrencyProvider>
                <UnifiedLanguageProvider>
                  <UnifiedCartProvider>
                    <ToastProvider>
                      <AppWrapper>
                        {children}
                      </AppWrapper>
                    </ToastProvider>
                  </UnifiedCartProvider>
                </UnifiedLanguageProvider>
              </UnifiedCurrencyProvider>
            </AuthProvider>
          </ThemeProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
} 