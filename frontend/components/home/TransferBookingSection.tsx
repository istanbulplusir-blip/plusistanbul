'use client'
import React, { useEffect, useState, useRef, useCallback } from 'react';

import { useRouter } from 'next/navigation';
import OptimizedImage from '@/components/common/OptimizedImage';
import { Button } from '@/components/ui/Button';
import { getTransferBookingSection, TransferBookingSection as TransferBookingSectionType } from '@/lib/api/shared';

export default function TransferBookingSection() {
  const router = useRouter();
  const [carIn, setCarIn] = useState(false);
  const [isRTL, setIsRTL] = useState(false);

  // API state
  const [transferData, setTransferData] = useState<TransferBookingSectionType | null>(null);

  const sectionRef = useRef<HTMLElement>(null);
  const carRef = useRef<HTMLDivElement>(null);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isScrollingRef = useRef(false);
  
  // Optimized scroll handling with throttling and CSS variables
  const handleScroll = useCallback(() => {
    if (!sectionRef.current || !carRef.current || isScrollingRef.current) return;
    
    isScrollingRef.current = true;
    
    // Use requestAnimationFrame for smooth performance
    requestAnimationFrame(() => {
      const rect = sectionRef.current!.getBoundingClientRect();
      const sectionTop = rect.top;
      const sectionHeight = rect.height;
      const windowHeight = window.innerHeight;
      
      // Calculate scroll progress within the section
      const scrollProgress = Math.max(0, Math.min(1, (windowHeight - sectionTop) / (windowHeight + sectionHeight)));
      
      // Move car horizontally based on scroll (left-right for LTR, right-left for RTL)
      if (scrollProgress > 0) {
        // Calculate available space for movement based on screen size
        const isMobile = window.innerWidth < 768;
        const isTablet = window.innerWidth < 1024;
        
        let maxMoveDistance;
        if (isMobile) {
          maxMoveDistance = window.innerWidth * 0.4;
        } else if (isTablet) {
          maxMoveDistance = window.innerWidth * 0.3;
        } else {
          maxMoveDistance = 200;
        }
        
        const moveDistance = scrollProgress * maxMoveDistance;
        
        // Use CSS custom properties for better performance
        if (isRTL) {
          carRef.current!.style.setProperty('--car-move-x', `-${moveDistance}px`);
        } else {
          carRef.current!.style.setProperty('--car-move-x', `${moveDistance}px`);
        }
      }
      

      
      // Throttle scroll events
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      
      scrollTimeoutRef.current = setTimeout(() => {
        isScrollingRef.current = false;
      }, 16); // ~60fps throttling
    });
  }, [isRTL]);

  // Handle intersection observer for car entrance animation
  const handleIntersection = useCallback((entries: IntersectionObserverEntry[]) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        // Delay car entrance for better effect
        setTimeout(() => setCarIn(true), 300);
      }
    });
  }, []);

  // Fetch transfer data from API
  useEffect(() => {
    const fetchTransferData = async () => {
      try {
        const data = await getTransferBookingSection();
        if (data) {
          setTransferData(data);
        } else {
          // Fallback data if API returns null
          setTransferData({
            id: 1,
            title: 'تجربه سفر بی‌دردسر',
            subtitle: 'خدمات تاکسی و ترنسفر حرفه‌ای',
            description: 'تجربه سفر بی‌دردسر با بهترین خدمات تاکسی و ترنسفر',
            button_text: 'رزرو ترنسفر',
            button_url: '/transfers/booking',
            background_image: undefined,
            background_image_url: undefined,
            experience_years: 20,
            countries_served: 100,
            feature_1: 'خودروهای لوکس',
            feature_2: 'رانندگان حرفه‌ای',
            feature_3: 'پیگیری ۲۴/۷',
            feature_4: 'ایمنی کامل',
            is_active: true,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          });
        }
      } catch (err) {
        console.error('Error fetching transfer data:', err);
        // Set fallback data on error
        setTransferData({
          id: 1,
          title: 'تجربه سفر بی‌دردسر',
          subtitle: 'خدمات تاکسی و ترنسفر حرفه‌ای',
          description: 'تجربه سفر بی‌دردسر با بهترین خدمات تاکسی و ترنسفر',
          button_text: 'رزرو ترنسفر',
          button_url: '/transfers/booking',
          background_image: undefined,
          background_image_url: undefined,
          experience_years: 20,
          countries_served: 100,
          feature_1: 'خودروهای لوکس',
          feature_2: 'رانندگان حرفه‌ای',
          feature_3: 'پیگیری ۲۴/۷',
          feature_4: 'ایمنی کامل',
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        });
      }
    };

    fetchTransferData();
  }, []);

  useEffect(() => {
    if (typeof document !== 'undefined') {
      setIsRTL(document.dir === 'rtl');
    }

    // Intersection Observer for car entrance
    const observer = new IntersectionObserver(handleIntersection, {
      threshold: 0.3,
      rootMargin: '0px 0px -100px 0px'
    });

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    // Scroll event listener
    window.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      observer.disconnect();
      window.removeEventListener('scroll', handleScroll);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, [handleScroll, handleIntersection]);
  

  return (
    <section ref={sectionRef} className="relative py-12 sm:py-16 lg:py-20 overflow-hidden">
      {/* Background - Modern gradient matching hero */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50/80 via-white to-secondary-50/80 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900" />

      {/* Floating particles effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(10)].map((_, i) => {
          // Deterministic positions for SSR consistency
          const positions = [
            { left: 68.91, top: 75.94 },
            { left: 21.45, top: 12.10 },
            { left: 95.42, top: 46.66 },
            { left: 83.60, top: 61.84 },
            { left: 46.02, top: 50.30 },
            { left: 36.02, top: 47.58 },
            { left: 56.86, top: 12.00 },
            { left: 65.32, top: 10.95 },
            { left: 58.31, top: 61.40 },
            { left: 38.22, top: 43.42 },
          ];

          const pos = positions[i] || { left: 50, top: 50 };

          return (
            <div
              key={i}
              className="absolute w-2 h-2 bg-accent-400/30 rounded-full animate-pulse"
              style={{
                left: `${pos.left}%`,
                top: `${pos.top}%`,
                animationDelay: `${(i * 0.3) % 3}s`,
                animationDuration: `${3 + (i * 0.2) % 2}s`,
              }}
            />
          );
        })}
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className={`flex flex-col-reverse lg:flex-row items-center justify-between gap-8 relative z-10`}>
          {/* Text Content - Now appears after car on mobile */}
          <div className={`flex-1 max-w-xl ${isRTL ? 'lg:pr-0 lg:pl-20 xl:pl-28 text-right' : 'lg:pl-0 lg:pr-20 xl:pr-28'}`}>
            {/* Badge with modern styling */}
            <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-accent-500/10 to-primary-500/10 backdrop-blur-sm rounded-full border border-accent-200/50 dark:border-accent-700/50 mb-4">
              <span className="text-sm uppercase tracking-wider text-accent-600 dark:text-accent-400 font-semibold">
                {transferData?.subtitle || (isRTL ? 'ترنسفر خصوصی' : 'Premium Transfers')}
              </span>
            </div>

            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-gray-100 mb-4">
              {transferData?.title || (isRTL ? 'به آسودگی فقط با چند کلیک' : 'Seamless Travel Experience')}
            </h2>
            <p className="text-gray-600 dark:text-gray-300 text-lg mb-8 animate-fade-in-up">
              {transferData?.description || (isRTL ? (
                // Persian text
                'ترنسفر فرودگاهی خصوصی یکی از متداول ترین ترنسفرهایی است که توسط اپراتورهای تورهای خارجی برای انتقال مستقیم مهمانان از فرودگاه به محل اقامت تور برگزار می‌شود. در تور خارجی مسافر پس از رسیدن به فرودگاه نگران پرداخت هزینه اضافی تاکسی و سایر مسائل امنیتی نیست و به راحتی می‌تواند به مقصد مورد نظر خود برسد.'
              ) : (
                // English text
                'Private airport transfer is one of the most common transfers organized by foreign tour operators for direct transportation of guests from the airport to the tour accommodation. In foreign tours, passengers are not worried about paying extra taxi costs and other security issues after arriving at the airport, and they can easily reach their desired destination.'
              ))}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8 animate-fade-in-up">
              <ul className="space-y-3 text-base text-gray-900 dark:text-white font-semibold">
                <li className="flex items-center gap-2 rtl:gap-2 animate-fade-in-left"><span className="text-accent-500 text-xl">✅</span> {transferData?.feature_1 || (isRTL ? 'خودروهای لوکس' : 'Luxury vehicles')}</li>
                <li className="flex items-center gap-2 rtl:gap-2 animate-fade-in-left"><span className="text-accent-500 text-xl">✅</span> {transferData?.feature_2 || (isRTL ? 'راننده حرفه‌ای' : 'Professional drivers')}</li>
                <li className="flex items-center gap-2 rtl:gap-2 animate-fade-in-left"><span className="text-accent-500 text-xl">✅</span> {transferData?.feature_3 || (isRTL ? 'پیگیری 24/7' : '24/7 tracking')}</li>
              </ul>
              <ul className="space-y-3 text-base text-gray-900 dark:text-white font-semibold">
                <li className="flex items-center gap-2 rtl:gap-2 animate-fade-in-right"><span className="text-accent-500 text-xl">✅</span> {transferData?.feature_4 || (isRTL ? 'قیمت شفاف' : 'Transparent pricing')}</li>
                <li className="flex items-center gap-2 rtl:gap-2 animate-fade-in-right"><span className="text-accent-500 text-xl">✅</span> {isRTL ? 'ایمنی کامل' : 'Complete safety'}</li>
                <li className="flex items-center gap-2 rtl:gap-2 animate-fade-in-right"><span className="text-accent-500 text-xl">✅</span> {isRTL ? 'رزرو فوری' : 'Instant booking'}</li>
              </ul>
            </div>
            <Button
              variant="default"
              size="lg"
              onClick={() => router.push(transferData?.button_url || '/transfers/booking')}
              className="bg-gradient-to-r from-accent-500 to-primary-500 hover:from-accent-600 hover:to-primary-600 text-white mt-6 px-12 py-4 text-lg font-bold rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300"
            >
              {transferData?.button_text || (isRTL ? 'رزرو ترنسفر' : 'Book Transfer')}
            </Button>
          </div>
        </div>

        {/* Enhanced Car Animation - Larger and Better Positioned */}
        <div className={`w-full relative mt-8 lg:mt-0 lg:absolute lg:inset-y-0 ${isRTL ? 'lg:left-0' : 'lg:right-0'} lg:w-3/5 flex items-center z-0`} style={{pointerEvents: 'none', overflow: 'visible'}}>
          <div
            ref={carRef}
            className={`relative w-full h-[220px] sm:h-[280px] md:h-[400px] lg:h-[600px] xl:h-[1200px] transition-all duration-1000 ease-out transform-gpu`
              + (carIn
                ? ' translate-x-0 opacity-100 scale-100'
                : (isRTL ? ' -translate-x-full opacity-0 scale-75' : ' translate-x-full opacity-0 scale-75'))}
            style={{
              maxWidth: '120vw', // Allow car to extend beyond container
              left: 0,
              right: 0,
              position: 'relative',
              '--car-move-x': '0px',
              transform: carIn ? `translateX(var(--car-move-x, 0px))` : undefined,
            } as React.CSSProperties & { '--car-move-x': string }}
          >
            {/* Car shadow for depth */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent transform scale-110 blur-sm" />
            
            <OptimizedImage
              src={transferData?.background_image_url || "/images/black-van-top.jpg"}
              alt="Taxi Top View"
              fill
              style={{
                objectFit: 'contain',
                objectPosition: isRTL ? 'left' : 'right',
                maxWidth: '120%',
                maxHeight: '120%',
                transform: isRTL ? 'scaleX(-1)' : 'scaleX(1)', // Mirror image for RTL
              }}
              className={`select-none pointer-events-none scale-125 lg:scale-110 xl:scale-100 transition-transform duration-500 hover:scale-110`}
            />

            {/* Car shadow for depth - no floating particles */}
          </div>
        </div>
      </div>
    </section>
  );
} 