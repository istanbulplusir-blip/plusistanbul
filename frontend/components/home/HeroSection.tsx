'use client'

import { useState, useEffect, useRef, useMemo } from 'react'
import { FaChevronLeft, FaChevronRight, FaPlay, FaPause, FaStar, FaGlobe, FaPlane, FaBus, FaMusic, FaMapMarkerAlt, FaUsers } from 'react-icons/fa'
import { useRouter } from 'next/navigation'
import OptimizedImage from '@/components/common/OptimizedImage'
import { Button } from '@/components/ui/Button'
import { useTranslations } from 'next-intl'
import { motion, AnimatePresence, useScroll, useTransform } from 'framer-motion'
import { getHeroSlides, HeroSlide, getAboutStatistics, AboutStatistic, getSiteSettings, SiteSettings } from '@/lib/api/shared'

// Fallback slides for when API is not available
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

// Improved Video Player Component with error handling and loading state
const VideoPlayer = ({
    src,
    poster,
    autoplay,
    muted,
    loop,
    controls,
    className,
    slideId,
    onError
}: {
    src: string
    poster?: string
    autoplay: boolean
    muted: boolean
    loop: boolean
    controls: boolean
    className?: string
    slideId?: string
    onError?: () => void
}) => {
    const videoRef = useRef<HTMLVideoElement>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const video = videoRef.current
        if (video && autoplay) {
            video.play().catch((error) => {
                console.error('Autoplay failed:', error)
                onError?.()
            })
        }
    }, [autoplay, src, onError])

    return (
        <>
            {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-gray-900/50 z-10">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
                </div>
            )}
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
                data-slide-id={slideId}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                onLoadedData={() => setIsLoading(false)}
                onWaiting={() => setIsLoading(true)}
                onPlaying={() => setIsLoading(false)}
                onError={(e) => {
                    console.error('Video error:', e)
                    setIsLoading(false)
                    onError?.()
                }}
            />
        </>
    )
}

// Custom hook for advanced text animation
const useAdvancedTextAnimation = (
    currentSlide: number,
    t: (key: string) => string,
    heroSlides: HeroSlide[],
    fallbackSlides: HeroSlide[]
) => {
    const [displayText, setDisplayText] = useState('')
    const [currentIndex, setCurrentIndex] = useState(0)
    const [isTyping, setIsTyping] = useState(true)
    const [showCursor, setShowCursor] = useState(true)

    const slides = useMemo(() => {
        if (heroSlides && heroSlides.length > 0) {
            return heroSlides.map(slide => ({
                title: slide.title,
                subtitle: slide.subtitle,
                description: slide.description,
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
    }, [heroSlides, fallbackSlides])

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
    }, [currentIndex, isTyping, currentSlide, heroSlides, fallbackSlides])

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

    // Improved: Video states per slide
    const [videoStates, setVideoStates] = useState<Record<string, boolean>>({})
    const [videoErrors, setVideoErrors] = useState<Record<string, boolean>>({})

    const [heroSlides, setHeroSlides] = useState<HeroSlide[]>([])
    const [, setLoadingSlides] = useState(true)
    const [aboutStatistics, setAboutStatistics] = useState<AboutStatistic[]>([])
    const [siteSettings, setSiteSettings] = useState<SiteSettings | null>(null)

    const fallbackSlides = useMemo(() => createFallbackSlides(t), [t])

    const { scrollYProgress } = useScroll({
        target: heroRef,
        offset: ["start start", "end start"]
    })

    const y = useTransform(scrollYProgress, [0, 1], [0, -200])
    const opacity = useTransform(scrollYProgress, [0, 0.8], [1, 0])

    useEffect(() => {
        const htmlDir = document.documentElement.dir
        setIsRTL(htmlDir === 'rtl')
    }, [])

    useEffect(() => {
        const fetchData = async () => {
            setLoadingSlides(true)

            const settings = await getSiteSettings()
            setSiteSettings(settings)

            const fetchedSlides = await getHeroSlides()
            console.log('Fetched hero slides:', fetchedSlides)

            if (fetchedSlides && fetchedSlides.length > 0) {
                setHeroSlides(fetchedSlides)
            } else {
                // Use SiteSettings defaults or fallback to hardcoded values
                const defaultHeroImage = settings?.default_hero_image_url || '/images/hero-main.jpg'
                const defaultTitle = settings?.default_hero_title || 'Welcome to Peykan Tourism'
                const defaultSubtitle = settings?.default_hero_subtitle || 'Discover amazing places'
                const defaultDescription = settings?.default_hero_description || 'Your gateway to amazing travel experiences'
                const defaultButtonText = settings?.default_hero_button_text || 'Explore Tours'
                const defaultButtonUrl = settings?.default_hero_button_url || '/tours'

                setHeroSlides([{
                    id: 'fallback',
                    title: defaultTitle,
                    subtitle: defaultSubtitle,
                    description: defaultDescription,
                    button_text: defaultButtonText,
                    button_url: defaultButtonUrl,
                    button_type: 'primary' as const,
                    desktop_image: defaultHeroImage,
                    tablet_image: defaultHeroImage,
                    mobile_image: defaultHeroImage,
                    desktop_image_url: defaultHeroImage,
                    tablet_image_url: defaultHeroImage,
                    mobile_image_url: defaultHeroImage,
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
            setLoadingSlides(false)
        }

        fetchData()
    }, [])

    useEffect(() => {
        const fetchAboutStatistics = async () => {
            const fetchedStats = await getAboutStatistics()
            if (fetchedStats && fetchedStats.length > 0) {
                setAboutStatistics(fetchedStats)
            }
        }

        fetchAboutStatistics()
    }, [])

    const totalSlides = useMemo(() => {
        const slideArray = heroSlides && heroSlides.length > 0 ? heroSlides : fallbackSlides
        return slideArray.length > 0 ? slideArray.length : 1
    }, [heroSlides, fallbackSlides])

    const getStatisticsForDisplay = useMemo(() => {
        if (!aboutStatistics || aboutStatistics.length === 0) {
            return [
                { icon: FaBus, label: 'Fleet Size', value: '150+', color: 'text-green-300' },
                { icon: FaUsers, label: 'Happy Customers', value: '50K+', color: 'text-blue-300' },
                { icon: FaStar, label: 'Rating', value: '4.9/5', color: 'text-yellow-300' },
                { icon: FaMapMarkerAlt, label: 'Destinations', value: '500+', color: 'text-purple-300' }
            ]
        }

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

    const { currentSlide, nextSlide, prevSlide, goToSlide } = useCarousel(totalSlides)
    const { displayText, subtitle, description, showCursor } = useAdvancedTextAnimation(currentSlide, t, heroSlides, fallbackSlides)

    const slideArray = heroSlides && heroSlides.length > 0 ? heroSlides : fallbackSlides
    const currentSlideData = slideArray[currentSlide] || slideArray[0]
    const currentHeroSlide = heroSlides[currentSlide] || heroSlides[0]

    // Improved: Calculate hasVideo with proper logic
    const hasVideo = useMemo(() => {
        if (!currentSlideData) return false

        return (
            currentSlideData.video_type !== 'none' &&
            (
                (currentSlideData.video_type === 'file' && !!currentSlideData.video_file_url) ||
                (currentSlideData.video_type === 'url' && !!currentSlideData.video_url)
            )
        )
    }, [currentSlideData])

    // Improved: Get video source with proper fallback
    const videoSrc = useMemo(() => {
        if (!hasVideo || !currentSlideData) return ""
        return currentSlideData.video_file_url || currentSlideData.video_url || ""
    }, [hasVideo, currentSlideData])

    // Improved: Get video poster with proper fallback chain
    const videoPoster = useMemo(() => {
        return currentSlideData?.video_thumbnail_url ||
            currentHeroSlide?.desktop_image_url ||
            siteSettings?.default_hero_image_url ||
            "/images/hero-main.jpg"
    }, [currentSlideData, currentHeroSlide, siteSettings])

    // Get current video state
    const currentVideoPlaying = videoStates[currentSlideData?.id] ?? true
    const currentVideoError = videoErrors[currentSlideData?.id] ?? false

    // Toggle video playback
    const toggleVideoPlayback = (slideId: string) => {
        setVideoStates(prev => ({
            ...prev,
            [slideId]: !prev[slideId]
        }))

        const videoElement = document.querySelector(`video[data-slide-id="${slideId}"]`) as HTMLVideoElement
        if (videoElement) {
            if (videoStates[slideId]) {
                videoElement.pause()
            } else {
                videoElement.play().catch(console.error)
            }
        }
    }

    // Handle video error
    const handleVideoError = (slideId: string) => {
        console.error(`Video error for slide: ${slideId}`)
        setVideoErrors(prev => ({
            ...prev,
            [slideId]: true
        }))
    }

    const renderSlideContent = () => {
        // For simplicity, we'll render a generic slide that works for all cases
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
                        <div className="text-center text-white">
                            <motion.div
                                initial={{ y: 50, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ duration: 0.8, delay: 0.2 }}
                                className="space-y-6"
                            >
                                <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20">
                                    <FaGlobe className="w-4 h-4 text-primary-300" />
                                    <span className="text-sm font-medium text-white">Premium Experience</span>
                                </div>

                                <h3 className="text-lg sm:text-xl lg:text-2xl font-medium text-gray-200">
                                    {currentSlideData?.subtitle || subtitle}
                                </h3>

                                <h1 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-bold text-white">
                                    {currentSlideData?.title || displayText}
                                    <motion.span
                                        className={`ml-2 ${showCursor ? 'opacity-100' : 'opacity-0'}`}
                                        animate={{ opacity: showCursor ? 1 : 0 }}
                                    >
                                        |
                                    </motion.span>
                                </h1>

                                <p className="text-xl text-gray-200 max-w-2xl mx-auto">
                                    {currentSlideData?.description || description}
                                </p>

                                <motion.div
                                    className="flex justify-center pt-4"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.6, delay: 1.0 }}
                                >
                                    {currentSlideData?.button_text && currentSlideData?.button_url && (
                                        <Button
                                            variant={currentSlideData.button_type === 'primary' ? 'default' : 'outline'}
                                            size="lg"
                                            className="bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white px-8 py-4 rounded-xl"
                                            onClick={() => {
                                                if (currentSlideData.button_url.startsWith('http')) {
                                                    window.open(currentSlideData.button_url, '_blank')
                                                } else {
                                                    router.push(currentSlideData.button_url)
                                                }
                                            }}
                                        >
                                            <FaPlane className="w-5 h-5 mr-2" />
                                            {currentSlideData.button_text}
                                        </Button>
                                    )}
                                </motion.div>
                            </motion.div>
                        </div>
                    </div>
                </div>

                {/* Background Image/Video */}
                <div className="absolute inset-0 -z-10">
                    <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-primary-900/40 to-secondary-900/30"></div>

                    {hasVideo && !currentVideoError ? (
                        <VideoPlayer
                            src={videoSrc}
                            poster={videoPoster}
                            autoplay={currentSlideData?.is_video_autoplay_allowed || false}
                            muted={currentSlideData?.video_muted ?? true}
                            loop={currentSlideData?.video_loop ?? true}
                            controls={currentSlideData?.show_video_controls ?? false}
                            className="w-full h-full object-cover"
                            slideId={currentSlideData?.id}
                            onError={() => handleVideoError(currentSlideData?.id || '')}
                        />
                    ) : (
                        <OptimizedImage
                            src={currentSlideData?.desktop_image_url || currentHeroSlide?.desktop_image_url || siteSettings?.default_hero_image_url || "/images/hero-main.jpg"}
                            alt={`Hero Background - Slide ${currentSlide + 1}`}
                            fill
                            className="object-cover"
                            priority
                            quality={90}
                            sizes="100vw"
                            placeholder="blur"
                            blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="
                            fallbackSrc="/images/hero-main.jpg"
                        />
                    )}
                </div>

                {/* Video Control Button */}
                {hasVideo && !currentVideoError && !currentSlideData?.show_video_controls && (
                    <motion.button
                        onClick={() => toggleVideoPlayback(currentSlideData?.id || '')}
                        className="absolute top-4 right-4 w-12 h-12 bg-black/50 hover:bg-black/70 backdrop-blur-sm rounded-full flex items-center justify-center text-white transition-all duration-300 hover:scale-110 z-20"
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        aria-label={currentVideoPlaying ? 'Pause video' : 'Play video'}
                    >
                        {currentVideoPlaying ? <FaPause className="w-5 h-5" /> : <FaPlay className="w-5 h-5 ml-0.5" />}
                    </motion.button>
                )}

                {/* Error Message */}
                {currentVideoError && (
                    <div className="absolute top-4 left-4 bg-red-500/80 text-white px-4 py-2 rounded-lg text-sm z-20">
                        Video failed to load. Showing image instead.
                    </div>
                )}
            </motion.div>
        )
    }

    return (
        <motion.section
            ref={heroRef}
            className="relative h-screen overflow-hidden"
            style={{ y, opacity }}
        >
            <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-secondary-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900" />

            <div className="relative z-10">
                <div className="relative h-screen overflow-hidden">
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

                    {/* Navigation Buttons */}
                    <motion.button
                        onClick={prevSlide}
                        className={`hidden lg:flex absolute top-1/2 transform -translate-y-1/2 w-20 h-20 bg-white/10 backdrop-blur-xl hover:bg-white/20 text-white rounded-full shadow-2xl items-center justify-center text-4xl border-2 border-white/20 transition-all duration-500 hover:scale-110 ${isRTL ? 'right-8' : 'left-8'
                            }`}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        aria-label="Previous slide"
                    >
                        {isRTL ? <FaChevronRight /> : <FaChevronLeft />}
                    </motion.button>

                    <motion.button
                        onClick={nextSlide}
                        className={`hidden lg:flex absolute top-1/2 transform -translate-y-1/2 w-20 h-20 bg-white/10 backdrop-blur-xl hover:bg-white/20 text-white rounded-full shadow-2xl items-center justify-center text-4xl border-2 border-white/20 transition-all duration-500 hover:scale-110 ${isRTL ? 'left-8' : 'right-8'
                            }`}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        aria-label="Next slide"
                    >
                        {isRTL ? <FaChevronLeft /> : <FaChevronRight />}
                    </motion.button>

                    {/* Slide Indicators */}
                    <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex gap-3 z-20">
                        {[...Array(totalSlides)].map((_, index) => (
                            <motion.button
                                key={index}
                                onClick={() => goToSlide(index)}
                                className={`relative overflow-hidden rounded-full transition-all duration-500 ${currentSlide === index
                                    ? 'w-12 h-3 bg-white'
                                    : 'w-3 h-3 bg-white/50 hover:bg-white/75'
                                    }`}
                                whileHover={{ scale: 1.2 }}
                                whileTap={{ scale: 0.9 }}
                                aria-label={`Go to slide ${index + 1}`}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </motion.section>
    )
}
