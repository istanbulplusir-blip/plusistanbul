'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import OptimizedImage from './OptimizedImage'
import { getBanners, trackBannerView, trackBannerClick, Banner as BannerType } from '@/lib/api/shared'

interface BannerProps {
  position?: 'top' | 'bottom' | 'sidebar' | 'middle' | 'popup'
  page?: string
  className?: string
}

export default function Banner({ position = 'top', page = 'home', className = '' }: BannerProps) {
  const [banners, setBanners] = useState<BannerType[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchBanners = async () => {
      try {
        setLoading(true)
        const bannerData = await getBanners(page)
        console.log('Fetched banners:', bannerData)

        // Filter banners by position
        const filteredBanners = bannerData.filter(banner => banner.position === position)
        setBanners(filteredBanners)
        console.log('Filtered banners for position', position, ':', filteredBanners.length)
      } catch (err) {
        console.error('Error fetching banners:', err)
        setError('Failed to load banners')
      } finally {
        setLoading(false)
      }
    }

    fetchBanners()
  }, [page, position])

  const handleBannerClick = async (banner: BannerType) => {
    try {
      await trackBannerClick(banner.id)
      if (banner.link_url) {
        window.open(banner.link_url, banner.link_target === '_blank' ? '_blank' : '_self')
      }
    } catch (error) {
      console.error('Error tracking banner click:', error)
    }
  }

  const handleBannerView = async (banner: BannerType) => {
    try {
      await trackBannerView(banner.id)
    } catch (error) {
      console.error('Error tracking banner view:', error)
    }
  }

  if (loading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="bg-gray-200 dark:bg-gray-700 rounded-lg h-32 flex items-center justify-center">
          <div className="text-gray-500 dark:text-gray-400">Loading banners...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 ${className}`}>
        <div className="text-red-600 dark:text-red-400 text-center">
          {error}
        </div>
      </div>
    )
  }

  if (banners.length === 0) {
    return null
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {banners.map((banner, index) => (
        <motion.div
          key={banner.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: index * 0.1 }}
          className="relative overflow-hidden rounded-lg shadow-lg hover:shadow-xl transition-shadow duration-300"
          onMouseEnter={() => handleBannerView(banner)}
        >
          <div
            className="cursor-pointer group"
            onClick={() => handleBannerClick(banner)}
          >
            {/* Banner Image */}
            <div className="relative aspect-[3/1] overflow-hidden">
              <OptimizedImage
                src={banner.image_url || '/media/defaults/no-image.png'}
                alt={banner.alt_text || banner.title}
                fill
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              />

              {/* Gradient Overlay */}
              <div className="absolute inset-0 bg-gradient-to-r from-black/20 to-transparent opacity-60 group-hover:opacity-40 transition-opacity duration-300" />

              {/* Content Overlay */}
              <div className="absolute inset-0 flex items-center justify-center p-6">
                <div className="text-center text-white">
                  <h3 className="text-xl md:text-2xl font-bold mb-2 drop-shadow-lg">
                    {banner.title}
                  </h3>
                  {banner.link_url && (
                    <div className="text-sm opacity-90">
                      Click to learn more →
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Banner Info (for debugging) */}
          <div className="absolute top-2 left-2 bg-black/50 text-white text-xs px-2 py-1 rounded">
            {banner.banner_type} - {banner.position}
          </div>

          {/* Analytics Info */}
          <div className="absolute top-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded">
            Views: {banner.view_count} | Clicks: {banner.click_count}
          </div>
        </motion.div>
      ))}
    </div>
  )
}
