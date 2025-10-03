'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { FaInstagram, FaTelegram, FaWhatsapp } from 'react-icons/fa'
import { useTranslations } from 'next-intl'
import { getFooter, Footer as FooterType } from '@/lib/api/shared'

export default function Footer() {
  const t = useTranslations('footer')
  const [isRTL, setIsRTL] = useState(false)

  // API state
  const [footerData, setFooterData] = useState<FooterType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Detect RTL language
  useEffect(() => {
    const htmlDir = document.documentElement.dir
    setIsRTL(htmlDir === 'rtl')
  }, [])

  // Fetch footer data from API
  useEffect(() => {
    const fetchFooterData = async () => {
      try {
        setLoading(true)
        const data = await getFooter()
        setFooterData(data)
      } catch (err) {
        console.error('Error fetching footer data:', err)
        setError('Failed to load footer data')
      } finally {
        setLoading(false)
      }
    }

    fetchFooterData()
  }, [])

  if (loading) {
    return (
      <footer className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white py-8 sm:py-10 lg:py-12 overflow-hidden">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-gray-300 rounded w-1/2"></div>
          </div>
        </div>
      </footer>
    );
  }

  if (error) {
    return (
      <footer className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white py-8 sm:py-10 lg:py-12 overflow-hidden">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-red-400">{error}</p>
        </div>
      </footer>
    );
  }

  return (
    <footer className="relative bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white py-8 sm:py-10 lg:py-12 overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-primary-900/20 via-secondary-900/10 to-accent-900/20"></div>

        {/* Floating particles effect */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(25)].map((_, i) => {
            // Deterministic positions for SSR consistency
            const positions = [
              { left: 71.30, top: 64.97 },
              { left: 87.57, top: 4.56 },
              { left: 40.24, top: 76.47 },
              { left: 27.70, top: 99.94 },
              { left: 6.85, top: 97.76 },
              { left: 76.61, top: 33.68 },
              { left: 93.92, top: 84.33 },
              { left: 14.07, top: 5.24 },
              { left: 28.21, top: 52.63 },
              { left: 5.44, top: 1.36 },
              { left: 71.10, top: 71.14 },
              { left: 45.31, top: 4.68 },
              { left: 85.15, top: 38.03 },
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
              { left: 23.78, top: 6.33 },
              { left: 54.27, top: 83.77 },
            ];

            const pos = positions[i] || { left: 50, top: 50 };

            return (
              <div
                key={i}
                className="absolute w-2 h-2 bg-white/10 rounded-full animate-pulse"
                style={{
                  left: `${pos.left}%`,
                  top: `${pos.top}%`,
                  animationDelay: `${(i * 0.32) % 8}s`,
                  animationDuration: `${8 + (i * 0.16) % 4}s`,
                }}
              />
            );
          })}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
          {/* Newsletter Column */}
          <div className={`lg:col-span-4 ${isRTL ? 'order-2 lg:order-1' : 'order-2 lg:order-2'}`}>
            <div className="space-y-4 sm:space-y-6">
              {/* Badge with modern styling */}
              <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold text-white">
                {footerData?.newsletter_title || t('newsletter') || 'Newsletter'}
              </h2>
              <p className="text-gray-300 text-lg sm:text-xl leading-relaxed">
                {footerData?.newsletter_description || t('newsletterDesc') || 'Get exclusive deals, travel tips, and destination highlights delivered to your inbox.'}
              </p>

              {/* Subscribe Box */}
              <div className="space-y-4">
                <div className={`flex ${isRTL ? 'flex-row-reverse' : 'flex-row'} bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 overflow-hidden`}>
                  <input
                    type="email"
                    placeholder={footerData?.newsletter_placeholder || t('emailPlaceholder') || 'Enter your email address'}
                    className="flex-1 px-4 sm:px-6 py-3 sm:py-4 bg-transparent border-0 focus:outline-none focus:ring-0 text-white placeholder-gray-400 text-base sm:text-lg"
                    dir={isRTL ? 'rtl' : 'ltr'}
                  />
                  <button className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white font-medium rounded-xl transition-all duration-300 text-base">
                    {t('subscribe') || 'Subscribe'}
                  </button>
                </div>

                <p className="text-xs sm:text-sm text-gray-400">
                  By subscribing, you agree to our Privacy Policy and consent to receive updates from our company.
                </p>
              </div>
            </div>
          </div>

          {/* Logo & Navigation Column */}
          <div className={`lg:col-span-8 ${isRTL ? 'order-1 lg:order-2' : 'order-1 lg:order-1'}`}>
            <div className="space-y-4 sm:space-y-6">
              {/* Logo */}
              <div className={`flex items-center gap-6 ${isRTL ? 'justify-center lg:justify-end' : 'justify-center lg:justify-start'}`}>
                <div className="relative w-20 h-20 sm:w-24 sm:h-24 rounded-3xl overflow-hidden shadow-2xl bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-sm border border-white/20">
                  <Image
                    src={footerData?.logo_url || "/logo.png"}
                    alt="Peykan Tourism Logo"
                    width={100}
                    height={100}
                    className="w-full h-full object-contain p-2"
                    quality={100}
                  />
                </div>
                <div className={`text-center ${isRTL ? 'lg:text-right' : 'lg:text-left'}`}>
                  <h2 className="text-2xl sm:text-3xl lg:text-4xl font-semibold text-white">
                    {footerData?.company_name || 'Peykan Tourism'}
                  </h2>
                  <p className="text-gray-300 text-base sm:text-lg mt-2 font-medium">
                    {footerData?.company_description || t('platformTitle') || 'Your Travel Companion'}
                  </p>
                  <div className={`flex items-center gap-2 mt-3 ${isRTL ? 'justify-center lg:justify-end' : 'justify-center lg:justify-start'}`}>
                    <div className="flex gap-1">
                      {[...Array(5)].map((_, i) => (
                        <span key={i} className="text-yellow-400 text-sm">⭐</span>
                      ))}
                    </div>
                    <span className="text-gray-400 text-sm">{footerData?.trusted_by_text || t('trustedBy') || 'Trusted by 50K+ travelers'}</span>
                  </div>
                </div>
              </div>

              {/* Navigation */}
              <nav className={`flex flex-wrap justify-center gap-3 sm:gap-4 lg:gap-6 ${isRTL ? 'lg:justify-end' : 'lg:justify-start'}`}>
                {footerData?.navigation_links?.map((link) => (
                  <Link
                    key={link.id}
                    href={link.url}
                    className="text-gray-300 hover:text-white transition-colors duration-300 text-sm sm:text-base font-medium"
                  >
                    {link.label}
                  </Link>
                )) || [
                  { href: '/tours', label: 'Tours', icon: '✈️' },
                  { href: '/events', label: 'Events', icon: '🎭' },
                  { href: '/transfers/booking', label: 'Transfers', icon: '🚗' },
                  { href: '/faq', label: 'FAQ', icon: '❓' },
                  { href: '/about', label: 'About', icon: '🏢' },
                  { href: '/contact', label: 'Contact', icon: '📞' }
                ].map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="text-gray-300 hover:text-white transition-colors duration-300 text-sm sm:text-base font-medium"
                  >
                    {link.label}
                  </Link>
                ))}
              </nav>

              {/* Social Media */}
              <div className={`flex justify-center gap-4 sm:gap-6 ${isRTL ? 'lg:justify-end' : 'lg:justify-start'}`}>
                {footerData?.instagram_url && (
                  <a
                    href={footerData.instagram_url}
                    className="w-12 h-12 sm:w-14 sm:h-14 bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-gradient-to-r hover:from-purple-500 hover:to-pink-500 rounded-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 hover:shadow-xl group"
                    aria-label="Instagram"
                  >
                    <FaInstagram className="w-5 h-5 sm:w-6 sm:h-6 text-gray-300 group-hover:text-white transition-colors duration-300" />
                  </a>
                )}
                {footerData?.telegram_url && (
                  <a
                    href={footerData.telegram_url}
                    className="w-12 h-12 sm:w-14 sm:h-14 bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-gradient-to-r hover:from-blue-500 hover:to-blue-600 rounded-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 hover:shadow-xl group"
                    aria-label="Telegram"
                  >
                    <FaTelegram className="w-5 h-5 sm:w-6 sm:h-6 text-gray-300 group-hover:text-white transition-colors duration-300" />
                  </a>
                )}
                {footerData?.whatsapp_number && (
                  <a
                    href={`https://wa.me/${footerData.whatsapp_number.replace(/[^0-9]/g, '')}`}
                    className="w-12 h-12 sm:w-14 sm:h-14 bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-gradient-to-r hover:from-green-500 hover:to-green-600 rounded-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 hover:shadow-xl group"
                    aria-label="WhatsApp"
                  >
                    <FaWhatsapp className="w-5 h-5 sm:w-6 sm:h-6 text-gray-300 group-hover:text-white transition-colors duration-300" />
                  </a>
                )}
                {!footerData?.instagram_url && !footerData?.telegram_url && !footerData?.whatsapp_number && [
                  { icon: FaInstagram, label: 'Instagram', color: 'hover:bg-gradient-to-r hover:from-purple-500 hover:to-pink-500' },
                  { icon: FaTelegram, label: 'Telegram', color: 'hover:bg-gradient-to-r hover:from-blue-500 hover:to-blue-600' },
                  { icon: FaWhatsapp, label: 'WhatsApp', color: 'hover:bg-gradient-to-r hover:from-green-500 hover:to-green-600' }
                ].map((social) => (
                  <a
                    key={social.label}
                    href="#"
                    className={`w-12 h-12 sm:w-14 sm:h-14 bg-white/10 backdrop-blur-sm border border-white/20 ${social.color} rounded-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 hover:shadow-xl group`}
                    aria-label={social.label}
                  >
                    <social.icon className="w-5 h-5 sm:w-6 sm:h-6 text-gray-300 group-hover:text-white transition-colors duration-300" />
                  </a>
                ))}
              </div>

              {/* Copyright and Legal Links */}
              <div className={`flex flex-col lg:flex-row justify-between items-center gap-3 sm:gap-4 ${isRTL ? 'lg:flex-row-reverse' : 'lg:flex-row'}`}>
                <div className="text-gray-300 text-sm sm:text-base text-center lg:text-left font-medium">
                  {footerData?.copyright_text || `© ${new Date().getFullYear()} Peykan Tourism. All rights reserved.`}
                </div>
                <div className="flex gap-4 sm:gap-6">
                  {footerData?.navigation_links?.filter(link => link.label.toLowerCase().includes('privacy')).map(link => (
                    <Link key={link.id} href={link.url} className="text-gray-400 hover:text-primary-400 transition-all duration-300 hover:scale-105 text-sm sm:text-base font-medium">
                      {link.label}
                    </Link>
                  )) || (
                    <Link href="/privacy" className="text-gray-400 hover:text-primary-400 transition-all duration-300 hover:scale-105 text-sm sm:text-base font-medium">
                      {t('privacy') || 'Privacy Policy'}
                    </Link>
                  )}
                  {footerData?.navigation_links?.filter(link => link.label.toLowerCase().includes('terms')).map(link => (
                    <Link key={link.id} href={link.url} className="text-gray-400 hover:text-secondary-400 transition-all duration-300 hover:scale-105 text-sm sm:text-base font-medium">
                      {link.label}
                    </Link>
                  )) || (
                    <Link href="/terms" className="text-gray-400 hover:text-secondary-400 transition-all duration-300 hover:scale-105 text-sm sm:text-base font-medium">
                      {t('terms') || 'Terms of Service'}
                    </Link>
                  )}
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </footer>
  )
} 