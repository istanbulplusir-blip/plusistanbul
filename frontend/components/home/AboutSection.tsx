'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/Button'
import OptimizedImage from '@/components/common/OptimizedImage'
import { useTranslations } from 'next-intl'
import {
  getAboutSection,
  getAboutStatistics,
  getAboutFeatures,
  AboutSection as AboutSectionType,
  AboutStatistic,
  AboutFeature
} from '@/lib/api/shared'

export default function AboutSection() {
  const t = useTranslations();
  const [counters, setCounters] = useState({
    experience: 0,
    countries: 0
  })

  // API state
  const [aboutSection, setAboutSection] = useState<AboutSectionType | null>(null)
  const [aboutStatistics, setAboutStatistics] = useState<AboutStatistic[]>([])
  const [aboutFeatures, setAboutFeatures] = useState<AboutFeature[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch data from API
  useEffect(() => {
    const fetchAboutData = async () => {
      try {
        setLoading(true)
        const [section, statistics, features] = await Promise.all([
          getAboutSection(),
          getAboutStatistics(),
          getAboutFeatures()
        ])

        setAboutSection(section)
        setAboutStatistics(statistics)
        setAboutFeatures(features)
      } catch (err) {
        console.error('Error fetching about data:', err)
        setError('Failed to load about section data')
      } finally {
        setLoading(false)
      }
    }

    fetchAboutData()
  }, [])

  // Animate counters when section comes into view
  useEffect(() => {
    if (!aboutSection || loading) return

    const animateCounters = () => {
      const duration = 2000
      const steps = 60
      const stepDuration = duration / steps

      let currentStep = 0
      const interval = setInterval(() => {
        currentStep++
        const progress = currentStep / steps

        // Use API data for final values
        const finalExperience = aboutStatistics.find(stat => stat.label.toLowerCase().includes('experience'))?.value || '20'
        const finalCountries = aboutStatistics.find(stat => stat.label.toLowerCase().includes('countries'))?.value || '100'

        const experienceValue = parseInt(finalExperience.replace('+', '')) || 20
        const countriesValue = parseInt(finalCountries.replace('+', '')) || 100

        setCounters({
          experience: Math.floor(experienceValue * progress),
          countries: Math.floor(countriesValue * progress)
        })

        if (currentStep >= steps) {
          clearInterval(interval)
          setCounters({
            experience: experienceValue,
            countries: countriesValue
          })
        }
      }, stepDuration)
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateCounters()
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.5 }
    )

    const element = document.getElementById('about-section')
    if (element) observer.observe(element)

    return () => observer.disconnect()
  }, [aboutSection, aboutStatistics, loading])

  // Loading state
  if (loading) {
    return (
      <section id="about-section" className="relative py-12 sm:py-16 lg:py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-secondary-50/80 via-white to-primary-50/80 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">⏳</span>
            </div>
            <p className="text-gray-500 dark:text-gray-400">Loading about section...</p>
          </div>
        </div>
      </section>
    )
  }

  // Error state
  if (error || !aboutSection) {
    return (
      <section id="about-section" className="relative py-12 sm:py-16 lg:py-20 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-secondary-50/80 via-white to-primary-50/80 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">⚠️</span>
            </div>
            <p className="text-red-500 dark:text-red-400">
              {error || 'Failed to load about section data'}
            </p>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section id="about-section" className="relative py-12 sm:py-16 lg:py-20 overflow-hidden">
      {/* Background - Modern gradient matching hero */}
      <div className="absolute inset-0 bg-gradient-to-br from-secondary-50/80 via-white to-primary-50/80 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900" />

      {/* Floating particles effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(12)].map((_, i) => {
          // Deterministic positions for SSR consistency
          const positions = [
            { left: 4.79, top: 79.12 },
            { left: 86.77, top: 34.60 },
            { left: 74.13, top: 32.36 },
            { left: 78.54, top: 30.09 },
            { left: 44.64, top: 14.16 },
            { left: 86.64, top: 72.82 },
            { left: 50.77, top: 5.55 },
            { left: 66.15, top: 47.18 },
            { left: 30.69, top: 27.77 },
            { left: 53.02, top: 72.10 },
            { left: 67.04, top: 27.51 },
            { left: 86.70, top: 49.51 },
          ];

          const pos = positions[i] || { left: 50, top: 50 };

          return (
            <div
              key={i}
              className="absolute w-2 h-2 bg-secondary-400/30 rounded-full animate-pulse"
              style={{
                left: `${pos.left}%`,
                top: `${pos.top}%`,
                animationDelay: `${(i * 0.33) % 4}s`,
                animationDuration: `${4 + (i * 0.16) % 2}s`,
              }}
            />
          );
        })}
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Image Column */}
          <div className="relative order-2 lg:order-1">
            <div className="relative rounded-xl lg:rounded-2xl overflow-hidden shadow-xl lg:shadow-2xl">
              <OptimizedImage
                src={aboutSection.hero_image_url || "/images/about-image.jpg"}
                alt="About Us"
                width={600}
                height={500}
                className="w-full h-[300px] sm:h-[400px] lg:h-[500px] object-cover"
                fallbackSrc="/images/about-placeholder.svg"
                quality={85}
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 600px"
                placeholder="blur"
                blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
            </div>
          </div>

          {/* Content Column */}
          <div className="space-y-6 lg:space-y-8 order-1 lg:order-2">
            <div className="space-y-6">
              <div className="space-y-4">
                {/* Badge with modern styling */}
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-500/10 to-secondary-500/10 backdrop-blur-sm rounded-full border border-primary-200/50 dark:border-primary-700/50">
                  <span className="text-primary-500">🏆</span>
                  <span className="text-sm uppercase tracking-wider text-primary-600 dark:text-primary-400 font-semibold">
                    {t('about.label') || 'About Us'}
                  </span>
                </div>

                <h1 className="text-2xl sm:text-3xl lg:text-4xl xl:text-5xl font-bold text-gray-900 dark:text-white mb-4 leading-tight">
                  {aboutSection.title}
                  <br />
                  <span className="text-primary-600 dark:text-primary-400">
                    {aboutSection.subtitle}
                  </span>
                </h1>
                <p className="text-base sm:text-lg text-gray-600 dark:text-gray-300 leading-relaxed">
                  {aboutSection.description}
                </p>
              </div>

              {/* Counters */}
              <div className="grid grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
                {aboutStatistics.slice(0, 2).map((stat, index) => (
                  <div
                    key={stat.id}
                    className={`bg-gradient-to-r ${index === 0 ? 'from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 border-primary-200/50 dark:border-primary-700/50' : 'from-secondary-50 to-primary-50 dark:from-secondary-900/20 dark:to-primary-900/20 border-secondary-200/50 dark:border-secondary-700/50'} backdrop-blur-sm rounded-xl lg:rounded-2xl p-4 sm:p-6 border text-center ${index === 1 ? 'lg:text-left' : ''}`}
                  >
                    <div className="text-2xl sm:text-3xl lg:text-4xl xl:text-5xl font-bold mb-1 sm:mb-2" style={{
                      color: index === 0 ? '#dc2626' : '#059669'
                    }}>
                      {index === 0 ? counters.experience : counters.countries}{stat.value.includes('+') ? '+' : ''}
                    </div>
                    <div className="text-sm sm:text-base text-gray-600 dark:text-gray-300 font-medium">
                      {stat.label}
                    </div>
                  </div>
                ))}
              </div>

              {/* Features */}
              <div className="space-y-3 sm:space-y-4">
                {aboutFeatures.slice(0, 3).map((feature, index) => {
                  const gradients = [
                    'from-primary-50/50 to-transparent dark:from-primary-900/20 dark:to-transparent border-primary-200/30 dark:border-primary-700/30',
                    'from-secondary-50/50 to-transparent dark:from-secondary-900/20 dark:to-transparent border-secondary-200/30 dark:border-secondary-700/30',
                    'from-accent-50/50 to-transparent dark:from-accent-900/20 dark:to-transparent border-accent-200/30 dark:border-accent-700/30'
                  ]


                  return (
                    <div key={feature.id} className={`flex items-center gap-3 sm:gap-4 rtl:gap-3 rtl:sm:gap-4 bg-gradient-to-r ${gradients[index]} backdrop-blur-sm rounded-lg sm:rounded-xl p-3 sm:p-4 border`}>
                      <div className="w-2.5 h-2.5 sm:w-3 sm:h-3 bg-gradient-to-r rounded-full flex-shrink-0 animate-pulse" style={{
                        background: `linear-gradient(to right, ${index === 0 ? '#dc2626, #7c3aed' : index === 1 ? '#7c3aed, #dc2626' : '#059669, #dc2626'})`
                      }}></div>
                      <span className="text-sm sm:text-base text-gray-700 dark:text-gray-300 font-medium">
                        {feature.title}
                      </span>
                    </div>
                  )
                })}
              </div>

              {/* CTA Button */}
              <div className="pt-4 sm:pt-6">
                <Button
                  variant="default"
                  size="lg"
                  onClick={() => window.location.href = aboutSection.button_url}
                  className="w-full sm:w-auto bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg font-semibold rounded-xl sm:rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 border-0"
                >
                  <span className="mr-2">📖</span>
                  {aboutSection.button_text}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
} 