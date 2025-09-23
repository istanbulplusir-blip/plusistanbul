'use client'

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { useTranslations } from 'next-intl';
import { getCTASection, CTASection as CTASectionType } from '@/lib/api/shared';

export default function CTASection() {
  const router = useRouter();
  const t = useTranslations('home.cta');

  // API state
  const [ctaData, setCtaData] = useState<CTASectionType | null>(null);
  const [, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null); // eslint-disable-line @typescript-eslint/no-unused-vars

  // Fetch CTA data from API
  useEffect(() => {
    const fetchCTAData = async () => {
      try {
        setLoading(true);
        const data = await getCTASection();
        setCtaData(data);
      } catch (err) {
        console.error('Error fetching CTA data:', err);
        setError('Failed to load CTA section data');
      } finally {
        setLoading(false);
      }
    };

    fetchCTAData();
  }, []);

  return (
    <section className="relative py-12 sm:py-16 lg:py-20 overflow-hidden">
      {/* Background - Modern gradient matching hero */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-900 via-secondary-900 to-accent-900" />

      {/* Floating particles effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => {
          // Deterministic positions for SSR consistency
          const positions = [
            { left: 31.97, top: 25.25 },
            { left: 62.85, top: 2.98 },
            { left: 30.00, top: 33.69 },
            { left: 81.79, top: 63.78 },
            { left: 38.35, top: 35.85 },
            { left: 53.84, top: 82.93 },
            { left: 41.56, top: 45.41 },
            { left: 5.58, top: 16.84 },
            { left: 39.19, top: 42.81 },
            { left: 89.22, top: 42.26 },
            { left: 64.93, top: 39.59 },
            { left: 47.60, top: 66.83 },
            { left: 35.83, top: 83.84 },
            { left: 80.49, top: 27.22 },
            { left: 2.25, top: 67.52 },
            { left: 31.57, top: 87.34 },
            { left: 34.65, top: 13.88 },
            { left: 70.31, top: 73.14 },
            { left: 84.12, top: 46.63 },
            { left: 55.50, top: 50.63 },
          ];

          const pos = positions[i] || { left: 50, top: 50 };

          return (
            <div
              key={i}
              className="absolute w-3 h-3 bg-white/20 rounded-full animate-pulse"
              style={{
                left: `${pos.left}%`,
                top: `${pos.top}%`,
                animationDelay: `${(i * 0.3) % 6}s`,
                animationDuration: `${6 + (i * 0.15) % 3}s`,
              }}
            />
          );
        })}
      </div>

      {/* Background overlay with glassmorphism */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent" />

      <div className="section-container text-center relative">
        <div className="space-y-8">
          {/* Badge with modern styling */}
          <div className="inline-flex items-center px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20 mb-4">
            <span className="text-sm uppercase tracking-wider text-white font-semibold">
              {t('readyToStart') || 'Ready to Start Your Journey'}
            </span>
          </div>

          {/* Main Heading */}
          <h1 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold text-white mb-6 leading-tight">
            {ctaData?.title || t('title') || 'Ready to Explore'}
            <span className="block text-2xl sm:text-3xl lg:text-4xl xl:text-5xl font-medium text-gray-200 dark:text-gray-300 mt-2">
              {ctaData?.subtitle || t('titleHighlight') || 'Amazing Destinations'}
            </span>
          </h1>

          {/* Subheading */}
          <p className="text-xl text-gray-200 max-w-3xl mx-auto leading-relaxed mb-8">
            {ctaData?.description || t('description') || 'Discover amazing tours, events, and transfers with our comprehensive booking platform. Your next adventure awaits!'}
          </p>

          {/* CTA Buttons */}
          <div className="pt-8 flex flex-col sm:flex-row items-center justify-center gap-6">
            {ctaData?.buttons?.map((button, index) => (
              <Button
                key={button.id}
                variant="default"
                size="lg"
                className={`px-8 py-4 text-lg font-semibold rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border-0 ${
                  button.button_type === 'primary'
                    ? 'bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600'
                    : button.button_type === 'secondary'
                    ? 'bg-gradient-to-r from-secondary-500 to-primary-500 hover:from-secondary-600 hover:to-primary-600'
                    : 'bg-gradient-to-r from-accent-500 to-primary-500 hover:from-accent-600 hover:to-primary-600'
                } text-white`}
                onClick={() => router.push(button.url)}
              >
                <span className="mr-2">
                  {index === 0 ? '✈️' : index === 1 ? '🎭' : '🚗'}
                </span>
                {button.text}
              </Button>
            )) || (
              <>
                <Button
                  variant="default"
                  size="lg"
                  className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-8 py-4 text-lg font-semibold rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border-0"
                  onClick={() => router.push('/tours')}
                >
                  <span className="mr-2">✈️</span>
                  {t('exploreTours') || 'Explore Tours'}
                </Button>
                <Button
                  variant="default"
                  size="lg"
                  className="bg-gradient-to-r from-secondary-500 to-primary-500 hover:from-secondary-600 hover:to-primary-600 text-white px-8 py-4 text-lg font-semibold rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border-0"
                  onClick={() => router.push('/events')}
                >
                  <span className="mr-2">🎭</span>
                  {t('discoverEvents') || 'Discover Events'}
                </Button>
                <Button
                  variant="default"
                  size="lg"
                  className="bg-gradient-to-r from-accent-500 to-primary-500 hover:from-accent-600 hover:to-primary-600 text-white px-8 py-4 text-lg font-semibold rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border-0"
                  onClick={() => router.push('/transfers/booking')}
                >
                  <span className="mr-2">🚗</span>
                  Book Transfers
                </Button>
              </>
            )}
          </div>

          {/* Additional Info */}
          <div className="pt-8 flex flex-col sm:flex-row items-center justify-center gap-8 text-gray-200">
            {ctaData?.features?.map((feature, index) => (
              <div key={feature.id} className="flex items-center gap-3 rtl:gap-3 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0 animate-pulse"
                  style={{
                    backgroundColor: index === 0 ? '#60a5fa' : index === 1 ? '#fbbf24' : '#10b981'
                  }}
                ></div>
                <span className="font-medium">{feature.text}</span>
              </div>
            )) || (
              <>
                <div className="flex items-center gap-3 rtl:gap-3 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
                  <div className="w-3 h-3 bg-primary-400 rounded-full flex-shrink-0 animate-pulse"></div>
                  <span className="font-medium">24/7 Support</span>
                </div>
                <div className="flex items-center gap-3 rtl:gap-3 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
                  <div className="w-3 h-3 bg-secondary-400 rounded-full flex-shrink-0 animate-pulse"></div>
                  <span className="font-medium">Best Price Guarantee</span>
                </div>
                <div className="flex items-center gap-3 rtl:gap-3 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
                  <div className="w-3 h-3 bg-accent-400 rounded-full flex-shrink-0 animate-pulse"></div>
                  <span className="font-medium">Secure Payment</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  )
} 