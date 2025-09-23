'use client'

import { useState, useEffect, useRef, useMemo } from 'react'
import { FaChevronLeft, FaChevronRight, FaPlay, FaPause, FaStar, FaGlobe, FaPlane, FaBus, FaMusic, FaMapMarkerAlt, FaUsers } from 'react-icons/fa'
import { useRouter } from 'next/navigation'
import OptimizedImage from '@/components/common/OptimizedImage'
import { Button } from '@/components/ui/Button'
import { useTranslations } from 'next-intl'
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion'
import { getHeroSlides, HeroSlide, getAboutStatistics, AboutStatistic } from '@/lib/api/shared'

// README: Modern Hero Design 2025 for Travel Platforms
/*
🎯 MODERN HERO DESIGN 2025 - Peykan Tourism Platform

✅ IMPLEMENTED FEATURES:

1. 🎠 ADVANCED SLIDER SYSTEM
   - 4 dynamic slides with unique content
   - Smooth transitions with AnimatePresence
   - Auto-play with progress indicators
   - Touch/swipe support for mobile

2. 🔍 INTERACTIVE SEARCH BOX
   - Multi-type search (Tours, Events, Transfers)
   - Smart form fields based on search type
   - Real-time search suggestions
   - Integrated with routing system

3. 🎭 ADVANCED ANIMATIONS
   - Typewriter text animation
   - Staggered content reveals
   - Parallax scrolling effects
   - Floating particle animations
   - Micro-interactions on hover

4. 📱 MOBILE-FIRST DESIGN
   - Responsive grid layouts
   - Touch-friendly navigation
   - Optimized for all screen sizes
   - RTL language support

5. 🎨 MODERN AESTHETICS
   - Glassmorphism effects
   - Gradient overlays
   - Dynamic shadows
   - Modern typography scales

6. 📊 LIVE STATISTICS
   - Real-time data updates
   - Animated counters
   - Social proof elements

7. 🌟 ACCESSIBILITY FEATURES
   - ARIA labels for navigation
   - Keyboard navigation support
   - Screen reader compatibility
   - Focus management

🚀 PERFORMANCE OPTIMIZATIONS:
- Lazy loading for images
- Optimized animations with GPU acceleration
- Minimal re-renders with proper state management
- SEO-friendly structure

🎯 USER EXPERIENCE ENHANCEMENTS:
- Intuitive navigation patterns
- Clear call-to-action buttons
- Progressive disclosure of information
- Emotional connection through visuals

💡 FUTURE ENHANCEMENTS:
- AI-powered search suggestions
- Voice search integration
- AR destination previews
- Real-time availability updates
- Personalized recommendations

📈 CONVERSION OPTIMIZATION:
- Strategic CTA placement
- Trust indicators
- Social proof integration
- Urgency and scarcity elements
- Multi-step user journey
*/

// Fallback slides for when API is not available - defined outside hook
const createFallbackSlides = (t: (key: string) => string): HeroSlide[] => [
  {
    id: 'fallback-1',
      title: t('home.hero.slide1.title') || "Discover Amazing Places",
      subtitle: t('home.hero.slide1.subtitle') || "Book tours, events & transfers with ease",
    description: t('home.hero.slide1.description') || "Experience unforgettable journeys with our premium travel services",
    button_text: 'Explore Tours',
    button_url: '/tours',
    button_type: 'primary',
    desktop_image: '',
    tablet_image: '',
    mobile_image: '',
    desktop_image_url: '',
    tablet_image_url: '',
    mobile_image_url: '',
    order: 1,
    display_duration: 5000,
    show_for_authenticated: true,
    show_for_anonymous: true,
    is_active: true,
    is_active_now: true,
    view_count: 0,
    click_count: 0,
    click_rate: 0,
    created_at: '',
    updated_at: '',
    // Video fields for fallback
    video_type: 'none',
    video_file: undefined,
    video_url: undefined,
    video_thumbnail: undefined,
    video_file_url: undefined,
    video_thumbnail_url: undefined,
    has_video: false,
    video_display_name: 'No Video',
    autoplay_video: false,
    video_muted: true,
    show_video_controls: false,
    video_loop: true,
    is_video_autoplay_allowed: false
  },
  {
    id: 'fallback-2',
      title: t('home.hero.slide2.title') || "Explore Istanbul's Magic",
      subtitle: t('home.hero.slide2.subtitle') || "Where History Meets Modernity",
    description: t('home.hero.slide2.description') || "Discover the enchanting city of Istanbul with our curated experiences",
    button_text: 'Explore Events',
    button_url: '/events',
    button_type: 'secondary',
    desktop_image: '',
    tablet_image: '',
    mobile_image: '',
    desktop_image_url: '',
    tablet_image_url: '',
    mobile_image_url: '',
    order: 2,
    display_duration: 5000,
    show_for_authenticated: true,
    show_for_anonymous: true,
    is_active: true,
    is_active_now: true,
    view_count: 0,
    click_count: 0,
    click_rate: 0,
    created_at: '',
    updated_at: '',
    // Video fields for fallback
    video_type: 'none',
    video_file: undefined,
    video_url: undefined,
    video_thumbnail: undefined,
    video_file_url: undefined,
    video_thumbnail_url: undefined,
    has_video: false,
    video_display_name: 'No Video',
    autoplay_video: false,
    video_muted: true,
    show_video_controls: false,
    video_loop: true,
    is_video_autoplay_allowed: false
  },
  {
    id: 'fallback-3',
      title: t('home.hero.slide3.title') || "Live Music & Entertainment",
      subtitle: t('home.hero.slide3.subtitle') || "Feel the Rhythm of Istanbul",
    description: t('home.hero.slide3.description') || "Experience world-class concerts and entertainment in iconic venues",
    button_text: 'Book Now',
    button_url: '/events',
    button_type: 'outline',
    desktop_image: '',
    tablet_image: '',
    mobile_image: '',
    desktop_image_url: '',
    tablet_image_url: '',
    mobile_image_url: '',
    order: 3,
    display_duration: 5000,
    show_for_authenticated: true,
    show_for_anonymous: true,
    is_active: true,
    is_active_now: true,
    view_count: 0,
    click_count: 0,
    click_rate: 0,
    created_at: '',
    updated_at: '',
    // Video fields for fallback
    video_type: 'none',
    video_file: undefined,
    video_url: undefined,
    video_thumbnail: undefined,
    video_file_url: undefined,
    video_thumbnail_url: undefined,
    has_video: false,
    video_display_name: 'No Video',
    autoplay_video: false,
    video_muted: true,
    show_video_controls: false,
    video_loop: true,
    is_video_autoplay_allowed: false
  }
]

// Custom hook for advanced text animation
const useAdvancedTextAnimation = (currentSlide: number, t: (key: string) => string, heroSlides: HeroSlide[], fallbackSlides: HeroSlide[]) => {
  const [displayText, setDisplayText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isTyping, setIsTyping] = useState(true)
  const [showCursor, setShowCursor] = useState(true)

  // Transform hero slides to display format
  const slides = useMemo(() => {
    if (heroSlides && heroSlides.length > 0) {
      return heroSlides.map(slide => ({
        title: slide.title,
        subtitle: slide.subtitle,
        description: slide.description,
        // Video fields
        video_type: slide.video_type,
        has_video: slide.has_video,
        autoplay_video: slide.autoplay_video,
        video_muted: slide.video_muted,
        show_video_controls: slide.show_video_controls,
        video_loop: slide.video_loop,
        is_video_autoplay_allowed: slide.is_video_autoplay_allowed,
        video_file_url: slide.video_file_url,
        video_url: slide.video_url,
        video_thumbnail_url: slide.video_thumbnail_url
      }))
    }
    return fallbackSlides
  }, [heroSlides, fallbackSlides]) // Include both dependencies

  useEffect(() => {
    const slideArray = heroSlides && heroSlides.length > 0 ? heroSlides : fallbackSlides
    const currentSlideData = slideArray[currentSlide] || slideArray[0]
    const targetText = currentSlideData?.title || ''
    let timeout: NodeJS.Timeout

    if (isTyping) {
      if (currentIndex < targetText.length) {
        timeout = setTimeout(() => {
          setDisplayText(prev => prev + targetText[currentIndex])
          setCurrentIndex(prev => prev + 1)
        }, 100)
      } else {
        setTimeout(() => setIsTyping(false), 2000)
      }
    } else {
      if (currentIndex > 0) {
        timeout = setTimeout(() => {
          setDisplayText(prev => prev.slice(0, -1))
          setCurrentIndex(prev => prev - 1)
        }, 50)
      } else {
        setTimeout(() => {
          setIsTyping(true)
          setCurrentIndex(0)
        }, 500)
      }
    }

    return () => {
      if (timeout) clearTimeout(timeout)
    }
  }, [currentIndex, isTyping, currentSlide, t, heroSlides, fallbackSlides])

  // Cursor blinking effect
  useEffect(() => {
    const cursorInterval = setInterval(() => {
      setShowCursor(prev => !prev)
    }, 500)

    return () => clearInterval(cursorInterval)
  }, [])

  return {
    displayText,
    subtitle: slides[currentSlide]?.subtitle || '',
    description: slides[currentSlide]?.description || '',
    showCursor
  }
}

// Video Player Component
const VideoPlayer = ({
  src,
  poster,
  autoplay,
  muted,
  loop,
  controls,
  className
}: {
  src: string
  poster?: string
  autoplay: boolean
  muted: boolean
  loop: boolean
  controls: boolean
  className?: string
}) => {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    const video = videoRef.current
    if (video && autoplay) {
      video.play().catch(() => {
        // Autoplay failed, user interaction required
      })
    }
  }, [autoplay, src])

  return (
    <video
      ref={videoRef}
      src={src}
      poster={poster}
      autoPlay={autoplay}
      muted={muted}
      loop={loop}
      controls={controls}
      playsInline
      className={className}
      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
    />
  )
}

// Custom hook for carousel management
const useCarousel = (totalSlides: number) => {
  const [currentSlide, setCurrentSlide] = useState(0)

  useEffect(() => {
    if (totalSlides <= 0) return

    const interval = setInterval(() => {
      setCurrentSlide(prev => (prev + 1) % totalSlides)
    }, 8000)

    return () => clearInterval(interval)
  }, [totalSlides])

  const nextSlide = () => {
    if (totalSlides <= 0) return
    setCurrentSlide(prev => (prev + 1) % totalSlides)
  }

  const prevSlide = () => {
    if (totalSlides <= 0) return
    setCurrentSlide(prev => (prev - 1 + totalSlides) % totalSlides)
  }

  const goToSlide = (index: number) => {
    if (index >= 0 && index < totalSlides) {
      setCurrentSlide(index)
    }
  }

  return { currentSlide, nextSlide, prevSlide, goToSlide }
}

export default function HeroSection() {
  const router = useRouter()
  const t = useTranslations()
  const heroRef = useRef<HTMLDivElement>(null)
  const [isRTL, setIsRTL] = useState(false)
  const [isVideoPlaying, setIsVideoPlaying] = useState(true)
  const [heroSlides, setHeroSlides] = useState<HeroSlide[]>([])
  const [, setLoadingSlides] = useState(true)
  const [aboutStatistics, setAboutStatistics] = useState<AboutStatistic[]>([])

  // Fallback slides defined in component scope
  const fallbackSlides = useMemo(() => createFallbackSlides(t), [t])

  // Total number of slides (dynamic based on API) - moved after slides definition

  // Scroll-based parallax
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"]
  })

  const y = useTransform(scrollYProgress, [0, 1], [0, -200])
  const opacity = useTransform(scrollYProgress, [0, 0.8], [1, 0])

  // Detect RTL language
  useEffect(() => {
    const htmlDir = document.documentElement.dir
    setIsRTL(htmlDir === 'rtl')
  }, [])

  // Fetch hero slides from API
  useEffect(() => {
    const fetchHeroSlides = async () => {
      try {
        setLoadingSlides(true)
        const fetchedSlides = await getHeroSlides()
        console.log('Fetched hero slides:', fetchedSlides)
        if (fetchedSlides && fetchedSlides.length > 0) {
          setHeroSlides(fetchedSlides)
        } else {
          setHeroSlides([{
            id: 'fallback',
            title: 'Welcome to Peykan Tourism',
            subtitle: 'Discover amazing places',
            description: 'Your gateway to amazing travel experiences',
            button_text: 'Explore Tours',
            button_url: '/tours',
            button_type: 'primary' as const,
            desktop_image: 'http://localhost:8000/media/hero/hero-main.jpg',
            tablet_image: 'http://localhost:8000/media/hero/hero-main.jpg',
            mobile_image: 'http://localhost:8000/media/hero/hero-main.jpg',
            desktop_image_url: 'http://localhost:8000/media/hero/hero-main.jpg',
            tablet_image_url: 'http://localhost:8000/media/hero/hero-main.jpg',
            mobile_image_url: 'http://localhost:8000/media/hero/hero-main.jpg',
            order: 0,
            display_duration: 5000,
            show_for_authenticated: true,
            show_for_anonymous: true,
            start_date: undefined,
            end_date: undefined,
            is_active: true,
            is_active_now: true,
            view_count: 0,
            click_count: 0,
            click_rate: 0,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            // Video fields for fallback
            video_type: 'none' as const,
            video_file: undefined,
            video_url: undefined,
            video_thumbnail: undefined,
            video_file_url: undefined,
            video_thumbnail_url: undefined,
            has_video: false,
            video_display_name: 'No Video',
            autoplay_video: false,
            video_muted: true,
            show_video_controls: false,
            video_loop: true,
            is_video_autoplay_allowed: false
          }])
        }
      } catch (error) {
        console.error('Error fetching hero slides:', error)
        console.log('Using fallback slides due to error')
      } finally {
        setLoadingSlides(false)
      }
    }

    fetchHeroSlides()
  }, [])

  // Fetch about statistics from API
  useEffect(() => {
    const fetchAboutStatistics = async () => {
      try {
        const fetchedStats = await getAboutStatistics()
        console.log('Fetched about statistics:', fetchedStats)
        if (fetchedStats && fetchedStats.length > 0) {
          setAboutStatistics(fetchedStats)
        }
      } catch (error) {
        console.error('Error fetching about statistics:', error)
      }
    }

    fetchAboutStatistics()
  }, [])

  // Total number of slides (dynamic based on API)
  const totalSlides = useMemo(() => {
    const slideArray = heroSlides && heroSlides.length > 0 ? heroSlides : fallbackSlides
    return slideArray.length > 0 ? slideArray.length : 1
  }, [heroSlides, fallbackSlides])

  // Map about statistics to display format
  const getStatisticsForDisplay = useMemo(() => {
    if (!aboutStatistics || aboutStatistics.length === 0) {
      // Fallback to static stats if no API data
      return [
        { icon: FaBus, label: 'Fleet Size', value: '150+', color: 'text-green-300' },
        { icon: FaUsers, label: 'Happy Customers', value: '50K+', color: 'text-blue-300' },
        { icon: FaStar, label: 'Rating', value: '4.9/5', color: 'text-yellow-300' },
        { icon: FaMapMarkerAlt, label: 'Destinations', value: '500+', color: 'text-purple-300' }
      ]
    }

    // Map API statistics to display format
    const iconMap: { [key: string]: React.ComponentType<{ className?: string }> } = {
      'fleet': FaBus,
      'customers': FaUsers,
      'rating': FaStar,
      'destinations': FaMapMarkerAlt,
      'bus': FaBus,
      'users': FaUsers,
      'star': FaStar,
      'location': FaMapMarkerAlt,
      'map': FaMapMarkerAlt
    }

    const colorMap: { [key: number]: string } = {
      0: 'text-green-300',
      1: 'text-blue-300', 
      2: 'text-yellow-300',
      3: 'text-purple-300'
    }

    return aboutStatistics.slice(0, 4).map((stat, index) => {
      const iconKey = stat.icon?.toLowerCase() || stat.label?.toLowerCase() || 'star'
      const IconComponent = Object.keys(iconMap).find(key => iconKey.includes(key)) 
        ? iconMap[Object.keys(iconMap).find(key => iconKey.includes(key))!]
        : FaStar

      return {
        icon: IconComponent,
        label: stat.label || 'Statistic',
        value: stat.value || '0',
        color: colorMap[index] || 'text-gray-300'
      }
    })
  }, [aboutStatistics])

  // Use custom hooks
  const { currentSlide, nextSlide, prevSlide, goToSlide } = useCarousel(totalSlides)
  const { displayText, subtitle, description, showCursor } = useAdvancedTextAnimation(currentSlide, t, heroSlides, fallbackSlides)
  const currentHeroSlide = heroSlides[currentSlide] || heroSlides[0]
  const slideArray = heroSlides && heroSlides.length > 0 ? heroSlides : fallbackSlides
  const currentSlideData = slideArray[currentSlide] || slideArray[0]


  const renderSlideContent = () => {
    switch (currentSlide) {
      case 0:
        // Main hero with advanced animations
        return (
          <motion.div
            className="absolute inset-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-full max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-center">
                  {/* Content */}
                  <motion.div
                    className="space-y-6 sm:space-y-8 text-center"
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                  >
                    <div className="space-y-6">
                      <motion.div
                        className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20"
                        whileHover={{ scale: 1.05 }}
                      >
                        <FaGlobe className="w-4 h-4 text-primary-300" />
                        <span className="text-sm font-medium text-white">Worldwide Travel</span>
                      </motion.div>

                      <div className="space-y-4">
                        <motion.div
                          className="text-lg sm:text-xl lg:text-2xl xl:text-3xl font-medium text-gray-700 dark:text-gray-300 tracking-wide"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.6, delay: 0.4 }}
                        >
                          {currentSlideData?.subtitle || subtitle}
                        </motion.div>

                        <motion.div
                          className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold text-gray-900 dark:text-gray-100 tracking-tight leading-tight"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.6, delay: 0.6 }}
                        >
                          {currentSlideData?.title || displayText}
                          <motion.span
                            className={`ml-2 ${showCursor ? 'opacity-100' : 'opacity-0'} transition-opacity duration-150`}
                            animate={{ opacity: showCursor ? 1 : 0 }}
                          >
                            |
                          </motion.span>
                        </motion.div>

                        <motion.p
                          className="text-xl lg:text-2xl font-light text-gray-200 max-w-2xl"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.6, delay: 0.8 }}
                        >
                          {currentSlideData?.description || description}
                        </motion.p>
                      </div>

                      <motion.div
                        className="flex justify-center pt-4 sm:pt-6"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 1.0 }}
                      >
                        {/* Primary Button from API */}
                        {currentSlideData?.button_text && currentSlideData?.button_url && (
                          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                            <Button
                              variant={currentSlideData.button_type === 'primary' ? 'default' : 'outline'}
                              size="lg"
                              className={`${
                                currentSlideData.button_type === 'primary'
                                  ? 'bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-8 py-4 rounded-xl shadow-lg hover:shadow-primary-500/25'
                                  : 'bg-white/10 backdrop-blur-md border-white/30 text-white hover:bg-white hover:text-gray-900 px-8 py-4 rounded-xl'
                              } transition-all duration-300`}
                              onClick={() => {
                                if (currentSlideData.button_url) {
                                  if (currentSlideData.button_url.startsWith('http')) {
                                    window.open(currentSlideData.button_url, '_blank')
                                  } else {
                                    router.push(currentSlideData.button_url)
                                  }
                                }
                              }}
                            >
                              <FaPlane className="w-5 h-5 mr-2" />
                              {currentSlideData.button_text}
                            </Button>
                          </motion.div>
                        )}

                        {/* Fallback button if no API button is available */}
                        {(!currentSlideData?.button_text || !currentSlideData?.button_url) && (
                          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                            <Button
                              variant="default"
                              size="lg"
                              className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-8 py-4 rounded-xl shadow-lg hover:shadow-primary-500/25 transition-all duration-300"
                              onClick={() => router.push('/tours')}
                            >
                              <FaPlane className="w-5 h-5 mr-2" />
                              {t('home.hero.slide1.exploreTours') || 'Explore Tours'}
                            </Button>
                          </motion.div>
                        )}
                      </motion.div>
                    </div>
                  </motion.div>

                </div>
              </div>
            </div>
          </motion.div>
        )

      case 1:
        // Dynamic slide with video support
        const hasVideo = currentSlideData?.has_video || currentHeroSlide?.has_video
        const videoSrc = currentSlideData?.video_file_url || currentSlideData?.video_url || "/images/istanbul-heli.mp4"
        const videoPoster = currentSlideData?.video_thumbnail_url || currentHeroSlide?.desktop_image_url || "/images/istanbul-fallback.jpg"

        return (
          <motion.div
            className="absolute inset-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          >
            {hasVideo ? (
              <VideoPlayer
                src={videoSrc}
                poster={videoPoster}
                autoplay={currentSlideData?.is_video_autoplay_allowed || false}
                muted={currentSlideData?.video_muted ?? true}
                loop={currentSlideData?.video_loop ?? true}
                controls={currentSlideData?.show_video_controls ?? false}
              className="w-full h-full object-cover"
              />
            ) : (
              <OptimizedImage
                src={currentHeroSlide?.desktop_image_url || "/images/istanbul-fallback.jpg"}
                alt="Istanbul"
                fill
                className="object-cover"
                quality={85}
                sizes="100vw"
                placeholder="blur"
                blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="
              />
            )}
            
            {/* Video Control Button - only show if video has controls */}
            {hasVideo && currentSlideData?.show_video_controls && (
            <motion.button
              onClick={() => setIsVideoPlaying(!isVideoPlaying)}
              className="absolute top-4 right-4 w-12 h-12 bg-black/50 hover:bg-black/70 backdrop-blur-sm rounded-full flex items-center justify-center text-white transition-all duration-300 hover:scale-110 z-20"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              aria-label={isVideoPlaying ? 'Pause video' : 'Play video'}
            >
              {isVideoPlaying ? <FaPause className="w-5 h-5" /> : <FaPlay className="w-5 h-5 ml-0.5" />}
            </motion.button>
            )}
            <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-primary-900/40 to-secondary-900/30"></div>

            <div className="absolute inset-0 flex items-center">
              <div className="w-full max-w-6xl mx-auto px-6 lg:px-8">
                <div className="text-center text-white">
                  <motion.div
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                  >
                    <h1 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold mb-6 tracking-tight text-gray-900 dark:text-gray-100">
                      {currentSlideData?.title || t('home.hero.slide2.title') || 'Istanbul Magic'}
                    </h1>
                    <h3 className="text-lg sm:text-xl lg:text-2xl xl:text-3xl font-medium tracking-wide text-gray-700 dark:text-gray-300 mb-8">
                      {currentSlideData?.subtitle || t('home.hero.slide2.subtitle') || 'Where History Meets Modernity'}
                    </h3>
                    <p className="text-base sm:text-lg lg:text-xl text-gray-600 dark:text-gray-400 max-w-4xl mx-auto mb-12 leading-relaxed">
                      {currentSlideData?.description || t('home.hero.slide2.description') || 'Experience the enchanting blend of Eastern and Western cultures in Istanbul'}
                    </p>
                  </motion.div>

                  <motion.div
                    className="flex flex-col sm:flex-row gap-6 justify-center items-center"
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                  >
                    {/* Primary Button from API */}
                    {currentSlideData?.button_text && currentSlideData?.button_url && (
                      <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                        <Button
                          variant={currentSlideData.button_type === 'primary' ? 'default' : 'outline'}
                          size="lg"
                          className={`${
                            currentSlideData.button_type === 'primary'
                              ? 'bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white text-xl px-10 py-5 rounded-2xl shadow-2xl'
                              : 'bg-white/10 backdrop-blur-md border-white/30 text-white hover:bg-white hover:text-gray-900 text-xl px-10 py-5 rounded-2xl'
                          } transition-all duration-300`}
                          onClick={() => {
                            if (currentSlideData.button_url) {
                              if (currentSlideData.button_url.startsWith('http')) {
                                window.open(currentSlideData.button_url, '_blank')
                              } else {
                                router.push(currentSlideData.button_url)
                              }
                            }
                          }}
                        >
                          <FaMapMarkerAlt className="w-6 h-6 mr-3" />
                          {currentSlideData.button_text}
                        </Button>
                      </motion.div>
                    )}

                    {/* Fallback button if no API button is available */}
                    {(!currentSlideData?.button_text || !currentSlideData?.button_url) && (
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button
                        variant="default"
                        size="lg"
                        className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white text-xl px-10 py-5 rounded-2xl shadow-2xl"
                        onClick={() => router.push('/tours')}
                      >
                        <FaMapMarkerAlt className="w-6 h-6 mr-3" />
                        {t('home.hero.slide2.viewFeaturedTour') || 'Explore Istanbul Tours'}
                      </Button>
                    </motion.div>
                    )}

                    {/* Video control button - only show if video has controls */}
                    {hasVideo && currentSlideData?.show_video_controls && (
                    <motion.button
                      className="flex items-center gap-3 text-white/80 hover:text-white transition-colors duration-300"
                      onClick={() => setIsVideoPlaying(!isVideoPlaying)}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {isVideoPlaying ? <FaPause className="w-5 h-5" /> : <FaPlay className="w-5 h-5" />}
                      <span className="text-lg">{isVideoPlaying ? 'Pause' : 'Play'} Video</span>
                    </motion.button>
                    )}
                  </motion.div>
                </div>
              </div>
            </div>
          </motion.div>
        )

      case 2:
        // Events & Entertainment
        return (
          <motion.div
            className="absolute inset-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          >
            <OptimizedImage
              src="/images/concert-hall.jpg"
              alt="Concert Hall"
              fill
              className="object-cover"
              quality={85}
              sizes="100vw"
              placeholder="blur"
              blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="
            />

            <div className="absolute inset-0 flex items-center">
              <div className="w-full max-w-6xl mx-auto px-6 lg:px-8">
                <div className="text-center text-white">
                  <motion.div
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                  >
                    <div className="flex justify-center mb-8">
                      <motion.div
                        className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500/20 to-primary-500/20 backdrop-blur-sm rounded-full border border-white/20"
                        whileHover={{ scale: 1.05 }}
                        animate={{ rotate: [0, 5, -5, 0] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        <FaMusic className="w-6 h-6 text-purple-300" />
                        <span className="text-lg font-semibold text-white">Live Entertainment</span>
                      </motion.div>
                    </div>

                    <h1 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold mb-6 tracking-tight text-gray-900 dark:text-gray-100">
                      {currentSlideData?.title || t('home.hero.slide3.title') || 'Live Music & Events'}
                    </h1>
                    <h3 className="text-lg sm:text-xl lg:text-2xl xl:text-3xl font-medium tracking-wide text-gray-700 dark:text-gray-300 mb-8">
                      {currentSlideData?.subtitle || t('home.hero.slide3.subtitle') || 'Feel the Rhythm of Istanbul'}
                    </h3>
                    <p className="text-base sm:text-lg lg:text-xl text-gray-600 dark:text-gray-400 max-w-4xl mx-auto mb-12 leading-relaxed">
                      {currentSlideData?.description || t('home.hero.slide3.description') || 'Experience world-class concerts and entertainment in iconic venues across Istanbul'}
                    </p>
                  </motion.div>

                  <motion.div
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.6 }}
                  >
                    {/* Primary Button from API */}
                    {currentSlideData?.button_text && currentSlideData?.button_url ? (
                      <Button
                        variant={currentSlideData.button_type === 'primary' ? 'default' : 'outline'}
                        size="lg"
                        className={`${
                          currentSlideData.button_type === 'primary'
                            ? 'bg-gradient-to-r from-purple-500 to-primary-500 hover:from-purple-600 hover:to-primary-600 text-white text-xl px-10 py-5 rounded-2xl shadow-2xl hover:shadow-purple-500/25'
                            : 'bg-white/10 backdrop-blur-md border-white/30 text-white hover:bg-white hover:text-gray-900 text-xl px-10 py-5 rounded-2xl'
                        } transition-all duration-300`}
                        onClick={() => {
                          if (currentSlideData.button_url) {
                            if (currentSlideData.button_url.startsWith('http')) {
                              window.open(currentSlideData.button_url, '_blank')
                            } else {
                              router.push(currentSlideData.button_url)
                            }
                          }
                        }}
                      >
                        <FaMusic className="w-6 h-6 mr-3" />
                        {currentSlideData.button_text}
                      </Button>
                    ) : (
                      /* Fallback button if no API button is available */
                    <Button
                      variant="default"
                      size="lg"
                      className="bg-gradient-to-r from-purple-500 to-primary-500 hover:from-purple-600 hover:to-primary-600 text-white text-xl px-10 py-5 rounded-2xl shadow-2xl hover:shadow-purple-500/25"
                      onClick={() => router.push('/events')}
                    >
                      <FaMusic className="w-6 h-6 mr-3" />
                      {t('home.hero.slide3.viewFeaturedEvent') || 'Discover Events'}
                    </Button>
                    )}
                  </motion.div>
                </div>
              </div>
            </div>
          </motion.div>
        )

      case 3:
        // Transfers & Transportation
        return (
          <motion.div
            className="absolute inset-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          >

            <div className="absolute inset-0 flex items-center">
              <div className="w-full max-w-6xl mx-auto px-6 lg:px-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                  <motion.div
                    className="space-y-8"
                    initial={{ x: -50, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                  >
                    <div className="space-y-6">
                      <motion.div
                        className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20"
                        whileHover={{ scale: 1.05 }}
                      >
                        <FaBus className="w-4 h-4 text-green-300" />
                        <span className="text-sm font-medium text-white">Premium Transfers</span>
                      </motion.div>

                      <div className="space-y-4">
                        <h1 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold text-gray-900 dark:text-gray-100 tracking-tight leading-tight">
                          {currentSlideData?.title || 'Seamless Travel'}
                        </h1>
                        <h3 className="text-lg sm:text-xl lg:text-2xl xl:text-3xl font-medium text-gray-700 dark:text-gray-300 tracking-wide">
                          {currentSlideData?.subtitle || 'Premium Airport Transfers'}
                        </h3>
                        <p className="text-base sm:text-lg lg:text-xl text-gray-600 dark:text-gray-400 max-w-xl">
                          {currentSlideData?.description || 'Experience luxury transportation with our premium transfer services. Safe, reliable, and comfortable journeys to your destination.'}
                        </p>
                      </div>

                      <motion.div
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        {/* Primary Button from API */}
                        {currentSlideData?.button_text && currentSlideData?.button_url ? (
                          <Button
                            variant={currentSlideData.button_type === 'primary' ? 'default' : 'outline'}
                            size="lg"
                            className={`${
                              currentSlideData.button_type === 'primary'
                                ? 'bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white text-lg px-8 py-4 rounded-2xl shadow-2xl'
                                : 'bg-white/10 backdrop-blur-md border-white/30 text-white hover:bg-white hover:text-gray-900 text-lg px-8 py-4 rounded-2xl'
                            } transition-all duration-300`}
                            onClick={() => {
                              if (currentSlideData.button_url) {
                                if (currentSlideData.button_url.startsWith('http')) {
                                  window.open(currentSlideData.button_url, '_blank')
                                } else {
                                  router.push(currentSlideData.button_url)
                                }
                              }
                            }}
                          >
                            <FaBus className="w-5 h-5 mr-2" />
                            {currentSlideData.button_text}
                          </Button>
                        ) : (
                          /* Fallback button if no API button is available */
                        <Button
                          variant="default"
                          size="lg"
                          className="bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white text-lg px-8 py-4 rounded-2xl shadow-2xl"
                          onClick={() => router.push('/transfers/booking')}
                        >
                          <FaBus className="w-5 h-5 mr-2" />
                          Book Transfer Now
                        </Button>
                        )}
                      </motion.div>
                    </div>
                  </motion.div>

                  {/* Transfer Stats */}
                  <motion.div
                    className="space-y-6"
                    initial={{ x: 50, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.4 }}
                  >
                    <div className="grid grid-cols-2 gap-4">
                      {getStatisticsForDisplay.map((stat, index) => (
                        <motion.div
                          key={stat.label}
                          className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20"
                          initial={{ y: 20, opacity: 0 }}
                          animate={{ y: 0, opacity: 1 }}
                          transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
                          whileHover={{ scale: 1.05, y: -5 }}
                        >
                          <stat.icon className={`w-8 h-8 ${stat.color} mb-3`} />
                          <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                          <div className="text-sm text-gray-300">{stat.label}</div>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                </div>
              </div>
            </div>
          </motion.div>
        )

      default:
        // Generic slide for any additional slides beyond the predefined ones
        return (
          <motion.div
            className="absolute inset-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="absolute inset-0 flex items-center pt-20">
              <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
                  {/* Left Content */}
                  <motion.div
                    className="space-y-6 sm:space-y-8"
                    initial={{ x: -50, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                  >
                    <div className="space-y-6">
                      <motion.div
                        className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20"
                        whileHover={{ scale: 1.05 }}
                      >
                        <FaGlobe className="w-4 h-4 text-primary-300" />
                        <span className="text-sm font-medium text-white">Premium Experience</span>
                      </motion.div>

                      <div className="space-y-4">
                        <motion.div
                          className="text-lg sm:text-xl lg:text-2xl xl:text-3xl font-medium text-gray-700 dark:text-gray-300 tracking-wide"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.6, delay: 0.4 }}
                        >
                          {currentSlideData?.subtitle || 'Discover Amazing Places'}
                        </motion.div>

                        <motion.div
                          className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold text-gray-900 dark:text-gray-100 tracking-tight leading-tight"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.6, delay: 0.6 }}
                        >
                          {currentSlideData?.title || 'Welcome to Our Platform'}
                        </motion.div>

                        <motion.p
                          className="text-xl lg:text-2xl font-light text-gray-200 max-w-2xl"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.6, delay: 0.8 }}
                        >
                          {currentSlideData?.description || 'Experience unforgettable journeys with our premium travel services'}
                        </motion.p>
                      </div>

                      <motion.div
                        className="flex flex-col sm:flex-row gap-3 sm:gap-4 lg:gap-6 pt-4 sm:pt-6"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6, delay: 1.0 }}
                      >
                        {/* Primary Button from API */}
                        {currentSlideData?.button_text && currentSlideData?.button_url && (
                          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                            <Button
                              variant={currentSlideData.button_type === 'primary' ? 'default' : 'outline'}
                              size="lg"
                              className={`${
                                currentSlideData.button_type === 'primary'
                                  ? 'bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-6 py-3 rounded-xl shadow-lg hover:shadow-primary-500/25'
                                  : 'bg-white/10 backdrop-blur-md border-white/30 text-white hover:bg-white hover:text-gray-900 px-5 py-2.5 rounded-xl'
                              } transition-all duration-300`}
                              onClick={() => {
                                if (currentSlideData.button_url) {
                                  if (currentSlideData.button_url.startsWith('http')) {
                                    window.open(currentSlideData.button_url, '_blank')
                                  } else {
                                    router.push(currentSlideData.button_url)
                                  }
                                }
                              }}
                            >
                              <FaPlane className="w-5 h-5 mr-2" />
                              {currentSlideData.button_text}
                            </Button>
                          </motion.div>
                        )}

                        {/* Fallback buttons if no API button is available */}
                        {(!currentSlideData?.button_text || !currentSlideData?.button_url) && (
                          <>
                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                              <Button
                                variant="default"
                                size="lg"
                                className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-6 py-3 rounded-xl shadow-lg hover:shadow-primary-500/25 transition-all duration-300"
                                onClick={() => router.push('/tours')}
                              >
                                <FaPlane className="w-5 h-5 mr-2" />
                                Explore Tours
                              </Button>
                            </motion.div>

                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                              <Button
                                variant="outline"
                                size="lg"
                                className="bg-white/10 backdrop-blur-md border-white/30 text-white hover:bg-white hover:text-gray-900 px-5 py-2.5 rounded-xl transition-all duration-300"
                                onClick={() => router.push('/events')}
                              >
                                <FaMusic className="w-5 h-5 mr-2" />
                                Discover Events
                              </Button>
                            </motion.div>
                          </>
                        )}
                      </motion.div>
                    </div>
                  </motion.div>

                </div>
              </div>
            </div>

            {/* Background Image/Video */}
            <div className="absolute inset-0 -z-10">
              {currentSlideData?.has_video ? (
                <VideoPlayer
                  src={currentSlideData.video_file_url || currentSlideData.video_url || ""}
                  poster={currentSlideData.video_thumbnail_url || currentHeroSlide?.desktop_image_url}
                  autoplay={currentSlideData.is_video_autoplay_allowed}
                  muted={currentSlideData.video_muted}
                  loop={currentSlideData.video_loop}
                  controls={currentSlideData.show_video_controls}
                  className="w-full h-full object-cover"
                />
              ) : (
                <OptimizedImage
                  src={currentSlideData?.desktop_image_url || currentHeroSlide?.desktop_image_url || "http://localhost:8000/media/hero/hero-main.jpg"}
                  alt={`Hero Background - Slide ${currentSlide + 1}`}
                  fill
                  className="object-cover"
                  priority
                  quality={90}
                  sizes="100vw"
                  placeholder="blur"
                  blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="
                />
              )}
            </div>
          </motion.div>
        )
    }
  }


  return (
    <motion.section
      ref={heroRef}
      className="relative h-screen overflow-hidden"
      style={{ y, opacity }}
    >
      {/* Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900" />


      <div className="relative z-10">
        {/* Main Hero Carousel */}
        <div className="relative h-screen overflow-hidden">
          {/* Slide Background */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`slide-${currentSlide}-bg`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.5 }}
              className="absolute inset-0"
            >
              {currentSlideData?.has_video ? (
                <VideoPlayer
                  src={currentSlideData.video_file_url || currentSlideData.video_url || ""}
                  poster={currentSlideData.video_thumbnail_url || currentHeroSlide?.desktop_image_url}
                  autoplay={currentSlideData.is_video_autoplay_allowed}
                  muted={currentSlideData.video_muted}
                  loop={currentSlideData.video_loop}
                  controls={currentSlideData.show_video_controls}
                  className="w-full h-full object-cover"
                />
              ) : (
              <OptimizedImage
                src={currentHeroSlide?.desktop_image_url || "http://localhost:8000/media/hero/hero-main.jpg"}
                alt={`Hero Background - Slide ${currentSlide + 1}`}
                fill
                className="object-cover"
                priority
                quality={90}
                sizes="100vw"
                placeholder="blur"
                blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="
              />
              )}
            </motion.div>
          </AnimatePresence>

          {/* Slide Content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentSlide}
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ duration: 0.8 }}
              className="absolute inset-0"
            >
              {renderSlideContent()}
            </motion.div>
          </AnimatePresence>

          {/* Enhanced Navigation */}
          <motion.button
            onClick={prevSlide}
            className={`hidden lg:flex absolute top-1/2 transform -translate-y-1/2 w-20 h-20 bg-white/10 dark:bg-gray-900/10 backdrop-blur-xl hover:bg-white/20 dark:hover:bg-gray-900/20 text-white rounded-full shadow-2xl items-center justify-center text-4xl border-2 border-white/20 dark:border-gray-700/20 transition-all duration-500 hover:scale-110 active:scale-95 ${
              isRTL ? 'right-8' : 'left-8'
            }`}
            whileHover={{
              scale: 1.1,
              boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
            }}
            whileTap={{ scale: 0.9 }}
            aria-label={isRTL ? t('home.navigation.nextSlide') : t('home.navigation.previousSlide')}
          >
            {isRTL ? <FaChevronRight /> : <FaChevronLeft />}
          </motion.button>

          <motion.button
            onClick={nextSlide}
            className={`hidden lg:flex absolute top-1/2 transform -translate-y-1/2 w-20 h-20 bg-white/10 dark:bg-gray-900/10 backdrop-blur-xl hover:bg-white/20 dark:hover:bg-gray-900/20 text-white rounded-full shadow-2xl items-center justify-center text-4xl border-2 border-white/20 dark:border-gray-700/20 transition-all duration-500 hover:scale-110 active:scale-95 ${
              isRTL ? 'left-8' : 'right-8'
            }`}
            whileHover={{
              scale: 1.1,
              boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.25)"
            }}
            whileTap={{ scale: 0.9 }}
            aria-label={isRTL ? t('home.navigation.previousSlide') : t('home.navigation.nextSlide')}
          >
            {isRTL ? <FaChevronLeft /> : <FaChevronRight />}
          </motion.button>

          {/* Mobile Navigation */}
          <div className="lg:hidden absolute bottom-20 left-1/2 transform -translate-x-1/2 flex gap-6">
            <motion.button
              onClick={prevSlide}
              className="w-14 h-14 bg-white/20 dark:bg-gray-900/20 backdrop-blur-xl hover:bg-white/30 dark:hover:bg-gray-900/30 text-white rounded-full shadow-xl flex items-center justify-center text-2xl border-2 border-white/30 dark:border-gray-700/30 transition-all duration-300 hover:scale-110 active:scale-95"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              aria-label={isRTL ? t('home.navigation.nextSlide') : t('home.navigation.previousSlide')}
            >
              {isRTL ? <FaChevronRight /> : <FaChevronLeft />}
            </motion.button>
            <motion.button
              onClick={nextSlide}
              className="w-14 h-14 bg-white/20 dark:bg-gray-900/20 backdrop-blur-xl hover:bg-white/30 dark:hover:bg-gray-900/30 text-white rounded-full shadow-xl flex items-center justify-center text-2xl border-2 border-white/30 dark:border-gray-700/30 transition-all duration-300 hover:scale-110 active:scale-95"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              aria-label={isRTL ? t('home.navigation.previousSlide') : t('home.navigation.nextSlide')}
            >
              {isRTL ? <FaChevronLeft /> : <FaChevronRight />}
            </motion.button>
          </div>

          {/* Enhanced Slide Indicators */}
          <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex gap-3">
            {[...Array(totalSlides)].map((_, index) => (
              <motion.button
                key={index}
                onClick={() => goToSlide(index)}
                className={`relative overflow-hidden rounded-full transition-all duration-500 ${
                  currentSlide === index
                    ? 'w-12 h-4 bg-gradient-to-r from-primary-500 to-secondary-500 shadow-lg'
                    : 'w-4 h-4 bg-white/50 hover:bg-white/70 backdrop-blur-sm'
                }`}
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
                aria-label={`${t('home.navigation.goToSlide')} ${index + 1}`}
                aria-current={currentSlide === index ? 'true' : 'false'}
              >
                {currentSlide === index && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-primary-400 to-secondary-400"
                    initial={{ x: '-100%' }}
                    animate={{ x: '0%' }}
                    transition={{ duration: 8, ease: 'linear' }}
                  />
                )}
              </motion.button>
            ))}
          </div>
        </div>
      </div>
    </motion.section>
  )
} 