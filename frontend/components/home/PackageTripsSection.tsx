'use client'

import React, { useState, useEffect, useCallback, useMemo, useTransition } from 'react'
import Link from 'next/link'
import { FaChevronLeft, FaChevronRight, FaMapPin, FaStar } from 'react-icons/fa'
import OptimizedImage from '@/components/common/OptimizedImage'
import { getHomeTours } from '@/lib/api/tours'
import { apiClient } from '@/lib/api/client'
import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/Button'

// Improved TypeScript interfaces with better type safety
interface Destination {
  readonly id: string
  readonly name: string
  readonly title?: string
  readonly description?: string
  readonly short_description?: string
  readonly image: string
  readonly image_url?: string
  readonly category: string
  readonly category_name?: string
  readonly slug?: string
  readonly starting_price?: number
  readonly next_schedule_date?: string
  readonly next_schedule_capacity_total?: number
  readonly next_schedule_capacity_available?: number
  readonly has_upcoming?: boolean
  readonly type: 'tour'
  readonly location?: string
  readonly duration_hours?: number
  readonly rating?: number
  readonly average_rating?: number
  readonly review_count?: number
  readonly min_participants?: number
  readonly max_participants?: number
  readonly is_featured?: boolean
  readonly is_popular?: boolean
  readonly is_special?: boolean
  readonly is_seasonal?: boolean
}

interface CategoryTab {
  readonly id: string
  readonly name: string
}

interface ApiResponse<T> {
  data?: {
    results?: T[]
  } | T[]
}

const defaultCategories: readonly CategoryTab[] = [
  { id: 'all', name: 'All' },
] as const

// Constants for better maintainability
const BREAKPOINTS = {
  MOBILE: 640,
  TABLET: 768,
  DESKTOP: 1024,
} as const

const ITEMS_PER_SLIDE = {
  MOBILE: 1,
  TABLET: 2,
  DESKTOP: 3,
  LARGE: 4,
} as const

export default function PackageTripsSection(): React.JSX.Element | null {
  const tHome = useTranslations('home')
  const [activeCategory, setActiveCategory] = useState<string>('all')
  const [currentSlide, setCurrentSlide] = useState<number>(0)
  const [itemsPerSlide, setItemsPerSlide] = useState<number>(ITEMS_PER_SLIDE.LARGE)
  const [apiDestinations, setApiDestinations] = useState<readonly Destination[]>([])
  const [categories, setCategories] = useState<readonly CategoryTab[]>(defaultCategories)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()
  const [isRTL, setIsRTL] = useState<boolean>(false)
  
  // Touch interaction state for mobile
  const [, ] = useState<NodeJS.Timeout | null>(null)
  
  // Collapsible categories state
  const [showAllCategories, setShowAllCategories] = useState<boolean>(false)
  const [visibleCategoriesCount, setVisibleCategoriesCount] = useState<number>(4)
  const [specialTours, setSpecialTours] = useState<readonly Destination[]>([])
  const [seasonalTours, setSeasonalTours] = useState<readonly Destination[]>([])
  const [currentSpecialSlide, setCurrentSpecialSlide] = useState<number>(0)
  const [currentSeasonalSlide, setCurrentSeasonalSlide] = useState<number>(0)

  // Detect RTL language
  useEffect(() => {
    const htmlDir = document.documentElement.dir
    setIsRTL(htmlDir === 'rtl')
  }, [])

  // Responsive visible categories count
  useEffect(() => {
    const updateVisibleCount = () => {
      if (window.innerWidth < 640) { // Mobile
        setVisibleCategoriesCount(3)
      } else if (window.innerWidth < 1024) { // Tablet
        setVisibleCategoriesCount(4)
      } else { // Desktop
        setVisibleCategoriesCount(5)
      }
    }

    updateVisibleCount()
    window.addEventListener('resize', updateVisibleCount)
    
    return () => window.removeEventListener('resize', updateVisibleCount)
  }, [])

  // Reset showAllCategories when screen size changes
  useEffect(() => {
    const handleResize = () => {
      setShowAllCategories(false)
    }
    
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])


  // Memoized resize handler with proper cleanup
  const handleResize = useCallback((): void => {
    const width = window.innerWidth
    if (width < BREAKPOINTS.MOBILE) {
      setItemsPerSlide(ITEMS_PER_SLIDE.MOBILE)
    } else if (width < BREAKPOINTS.TABLET) {
      setItemsPerSlide(ITEMS_PER_SLIDE.TABLET)
    } else if (width < BREAKPOINTS.DESKTOP) {
      setItemsPerSlide(ITEMS_PER_SLIDE.DESKTOP)
    } else {
      setItemsPerSlide(ITEMS_PER_SLIDE.LARGE)
    }
  }, [])

  // Improved resize effect with proper cleanup
  useEffect((): (() => void) => {
    handleResize()
    window.addEventListener('resize', handleResize, { passive: true })
    return (): void => window.removeEventListener('resize', handleResize)
  }, [handleResize])

  // Type-safe API response handling
  const parseApiResponse = <T,>(response: unknown): T[] => {
    if (response && typeof response === 'object' && 'data' in response) {
      const data = (response as ApiResponse<T>).data
      if (Array.isArray(data)) {
        return data
      }
      if (data && typeof data === 'object' && 'results' in data) {
        const results = (data as { results?: T[] }).results
        return Array.isArray(results) ? results : []
      }
    }
    return []
  }

  // Memoized and type-safe fetch tours function
  const fetchTours = useCallback(async (): Promise<void> => {
    try {
      setIsLoading(true)

      // Try to get home tours first
      try {
        const homeToursData = await getHomeTours()

        // Process featured tours
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const featuredMapped: Destination[] = homeToursData.featured_tours.map((tour: any) => ({
          id: tour.id,
          name: tour.title || tour.name || 'Tour',
          title: tour.title || tour.name || 'Tour',
          description: tour.description || tour.short_description || 'No description available',
          short_description: tour.short_description || tour.description || 'No description available',
          image: tour.image_url || tour.image || '/images/tour-image.jpg',
          image_url: tour.image_url || tour.image || '/images/tour-image.jpg',
          category: tour.category_slug || 'all',
          category_name: tour.category_name || 'Tour',
          slug: tour.slug,
          starting_price: tour.starting_price,
          next_schedule_date: tour.next_schedule_date,
          next_schedule_capacity_total: tour.next_schedule_capacity_total,
          next_schedule_capacity_available: tour.next_schedule_capacity_available,
          has_upcoming: tour.has_upcoming,
          type: 'tour' as const,
          location: tour.location || 'Location not specified',
          duration_hours: tour.duration_hours || 8,
          rating: tour.rating || tour.average_rating || 0,
          average_rating: tour.average_rating || tour.rating || 0,
          review_count: tour.review_count || 0,
          min_participants: tour.min_participants || 1,
          max_participants: tour.max_participants || 20,
          is_featured: tour.is_featured || false,
          is_popular: tour.is_popular || false,
          is_special: tour.is_special || false,
          is_seasonal: tour.is_seasonal || false
        }))

        // Process special tours
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const specialMapped: Destination[] = homeToursData.special_tours.map((tour: any) => ({
          id: tour.id,
          name: tour.title || tour.name || 'Tour',
          title: tour.title || tour.name || 'Tour',
          description: tour.description || tour.short_description || 'No description available',
          short_description: tour.short_description || tour.description || 'No description available',
          image: tour.image_url || tour.image || '/images/tour-image.jpg',
          image_url: tour.image_url || tour.image || '/images/tour-image.jpg',
          category: tour.category_slug || 'all',
          category_name: tour.category_name || 'Tour',
          slug: tour.slug,
          starting_price: tour.starting_price,
          next_schedule_date: tour.next_schedule_date,
          next_schedule_capacity_total: tour.next_schedule_capacity_total,
          next_schedule_capacity_available: tour.next_schedule_capacity_available,
          has_upcoming: tour.has_upcoming,
          type: 'tour' as const,
          location: tour.location || 'Location not specified',
          duration_hours: tour.duration_hours || 8,
          rating: tour.rating || tour.average_rating || 0,
          average_rating: tour.average_rating || tour.rating || 0,
          review_count: tour.review_count || 0,
          min_participants: tour.min_participants || 1,
          max_participants: tour.max_participants || 20,
          is_featured: tour.is_featured || false,
          is_popular: tour.is_popular || false,
          is_special: tour.is_special || false,
          is_seasonal: tour.is_seasonal || false
        }))

        // Process seasonal tours
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const seasonalMapped: Destination[] = homeToursData.seasonal_tours.map((tour: any) => ({
          id: tour.id,
          name: tour.title || tour.name || 'Tour',
          title: tour.title || tour.name || 'Tour',
          description: tour.description || tour.short_description || 'No description available',
          short_description: tour.short_description || tour.description || 'No description available',
          image: tour.image_url || tour.image || '/images/tour-image.jpg',
          image_url: tour.image_url || tour.image || '/images/tour-image.jpg',
          category: tour.category_slug || 'all',
          category_name: tour.category_name || 'Tour',
          slug: tour.slug,
          starting_price: tour.starting_price,
          next_schedule_date: tour.next_schedule_date,
          next_schedule_capacity_total: tour.next_schedule_capacity_total,
          next_schedule_capacity_available: tour.next_schedule_capacity_available,
          has_upcoming: tour.has_upcoming,
          type: 'tour' as const,
          location: tour.location || 'Location not specified',
          duration_hours: tour.duration_hours || 8,
          rating: tour.rating || tour.average_rating || 0,
          average_rating: tour.average_rating || tour.rating || 0,
          review_count: tour.review_count || 0,
          min_participants: tour.min_participants || 1,
          max_participants: tour.max_participants || 20,
          is_featured: tour.is_featured || false,
          is_popular: tour.is_popular || false,
          is_special: tour.is_special || false,
          is_seasonal: tour.is_seasonal || false
        }))

        // Process popular tours (for the main section)
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const popularMapped: Destination[] = homeToursData.popular_tours.map((tour: any) => ({
          id: tour.id,
          name: tour.title || tour.name || 'Tour',
          title: tour.title || tour.name || 'Tour',
          description: tour.description || tour.short_description || 'No description available',
          short_description: tour.short_description || tour.description || 'No description available',
          image: tour.image_url || tour.image || '/images/tour-image.jpg',
          image_url: tour.image_url || tour.image || '/images/tour-image.jpg',
          category: tour.category_slug || 'all',
          category_name: tour.category_name || 'Tour',
          slug: tour.slug,
          starting_price: tour.starting_price,
          next_schedule_date: tour.next_schedule_date,
          next_schedule_capacity_total: tour.next_schedule_capacity_total,
          next_schedule_capacity_available: tour.next_schedule_capacity_available,
          has_upcoming: tour.has_upcoming,
          type: 'tour' as const,
          location: tour.location || 'Location not specified',
          duration_hours: tour.duration_hours || 8,
          rating: tour.rating || tour.average_rating || 0,
          average_rating: tour.average_rating || tour.rating || 0,
          review_count: tour.review_count || 0,
          min_participants: tour.min_participants || 1,
          max_participants: tour.max_participants || 20,
          is_featured: tour.is_featured || false,
          is_popular: tour.is_popular || false,
          is_special: tour.is_special || false,
          is_seasonal: tour.is_seasonal || false
        }))

        // Set the different tour categories
        setSpecialTours(specialMapped)
        setSeasonalTours(seasonalMapped)

        // Combine all tours for the main section (remove duplicates)
        const allToursMap = new Map()

        // Add tours to map to ensure uniqueness
        ;[...featuredMapped, ...specialMapped, ...seasonalMapped, ...popularMapped].forEach(tour => {
          if (!allToursMap.has(tour.id)) {
            allToursMap.set(tour.id, tour)
          }
        })

        const allTours = Array.from(allToursMap.values())
        setApiDestinations(allTours)

        setLoadError(null)
        setIsLoading(false)
        return

      } catch (homeToursError) {
        console.warn('Failed to fetch home tours, falling back to regular API:', homeToursError)
      }

      // Fallback to regular API
      const response = await apiClient.get('/tours/', {
        params: { page_size: 12 },
        signal: AbortSignal.timeout(10000) // 10 second timeout
      })

      const rawData = parseApiResponse(response)

      const mapped: Destination[] = rawData.map((tour: unknown) => {
        const t = tour as {
          id: string
          title?: string
          name?: string
          description?: string
          short_description?: string
          image?: string
          image_url?: string
          category_slug?: string
          category_name?: string
          slug: string
          starting_price?: number
          next_schedule_date?: string
          next_schedule_capacity_total?: number
          next_schedule_capacity_available?: number
          has_upcoming?: boolean
          location?: string
          duration_hours?: number
          rating?: number
          average_rating?: number
          review_count?: number
          min_participants?: number
          max_participants?: number
        }

        // Clean and validate image URLs
        const cleanImageUrl = (url?: string): string => {
          if (!url || url === 'null' || url === 'undefined' || url.includes('via.placeholder.com')) {
            return '/images/tour-image.jpg'
          }
          return url
        }

        return {
          id: t.id,
          name: t.title || t.name || 'Tour',
          title: t.title || t.name || 'Tour',
          description: t.description || t.short_description || 'No description available',
          short_description: t.short_description || t.description || 'No description available',
          image: cleanImageUrl(t.image_url || t.image),
          image_url: cleanImageUrl(t.image_url || t.image),
          category: t.category_slug || 'all',
          category_name: t.category_name || 'Tour',
          slug: t.slug,
          starting_price: t.starting_price,
          next_schedule_date: t.next_schedule_date,
          next_schedule_capacity_total: t.next_schedule_capacity_total,
          next_schedule_capacity_available: t.next_schedule_capacity_available,
          has_upcoming: t.has_upcoming,
          type: 'tour' as const,
          location: t.location || 'Location not specified',
          duration_hours: t.duration_hours || 8,
          rating: t.rating || t.average_rating || 0,
          average_rating: t.average_rating || t.rating || 0,
          review_count: t.review_count || 0,
          min_participants: t.min_participants || 1,
          max_participants: t.max_participants || 20,
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          is_featured: (t as any).is_featured || false,
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          is_popular: (t as any).is_popular || false,
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          is_special: (t as any).is_special || false,
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          is_seasonal: (t as any).is_seasonal || false
        }
      })

      // Separate tours by category for fallback
      const specialToursFallback = mapped.filter(tour => tour.is_special)
      const seasonalToursFallback = mapped.filter(tour => tour.is_seasonal)

      setSpecialTours(specialToursFallback)
      setSeasonalTours(seasonalToursFallback)

      // Remove duplicates from main section
      const mainToursMap = new Map()
      mapped.forEach(tour => {
        if (!mainToursMap.has(tour.id)) {
          mainToursMap.set(tour.id, tour)
        }
      })

      setApiDestinations(Array.from(mainToursMap.values()))
      setLoadError(null)
    } catch (error) {
      console.error('Failed to fetch tours:', error)
      setApiDestinations([])
      setLoadError('failed')
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Memoized and type-safe fetch categories function
  const fetchCategories = useCallback(async (): Promise<void> => {
    try {
      const response = await apiClient.get('/tours/categories/', {
        signal: AbortSignal.timeout(5000) // 5 second timeout
      })
      
      const data = parseApiResponse(response)
      
      const mapped: CategoryTab[] = [
        { id: 'all', name: 'All' },
        ...data.map((c: unknown) => {
          const category = c as {
            slug?: string
            id?: string
            name?: string
            title?: string
          }
          return {
            id: category.slug || category.id || category.name || 'unknown',
            name: category.name || category.title || 'Unknown'
          }
        })
      ]
      
      setCategories(mapped)
    } catch (error) {
      console.error('Failed to fetch categories:', error)
      // Keep default categories on error
    }
  }, [])

  // Filter categories to only show those with active products
  const activeCategories = useMemo((): readonly CategoryTab[] => {
    if (categories.length <= 1) return categories // Only "All" category
    
    const categoriesWithProducts = categories.filter(category => {
      if (category.id === 'all') return true // Always include "All"
      
      // Check if this category has any products (not just upcoming ones)
      return apiDestinations.some(dest => dest.category === category.id)
    })
    
    return categoriesWithProducts
  }, [categories, apiDestinations])

  // Collapsible categories logic
  const visibleCategories = useMemo((): readonly CategoryTab[] => {
    if (showAllCategories || activeCategories.length <= visibleCategoriesCount) {
      return activeCategories
    }
    return activeCategories.slice(0, visibleCategoriesCount)
  }, [activeCategories, showAllCategories, visibleCategoriesCount])

  const hiddenCategoriesCount = activeCategories.length - visibleCategories.length

  // Toggle categories visibility
  const toggleCategories = useCallback((): void => {
    setShowAllCategories(prev => !prev)
  }, [])

  // Reset active category if it becomes inactive
  useEffect(() => {
    if (activeCategory !== 'all' && !activeCategories.some(cat => cat.id === activeCategory)) {
      setActiveCategory('all')
    }
  }, [activeCategories, activeCategory])

  // Improved data loading with proper cleanup
  useEffect((): (() => void) => {
    let isMounted = true
    
    const loadData = async (): Promise<void> => {
      if (isMounted) {
        await fetchTours()
      }
    }
    
    loadData()
    
    return (): void => {
      isMounted = false
    }
  }, [fetchTours])

  useEffect((): (() => void) => {
    let isMounted = true
    
    const loadCategories = async (): Promise<void> => {
      if (isMounted) {
        await fetchCategories()
      }
    }
    
    loadCategories()
    
    return (): void => {
      isMounted = false
    }
  }, [fetchCategories])

  // Memoized filtered destinations with proper dependency array
  const filteredDestinations = useMemo((): readonly Destination[] => {
    if (activeCategory === 'all') {
      return apiDestinations
    }
    return apiDestinations.filter(dest => dest.category === activeCategory)
  }, [apiDestinations, activeCategory])

  // Memoized current slide items
  const currentSlideItems = useMemo((): readonly Destination[] => {
    const startIndex = currentSlide * itemsPerSlide
    return filteredDestinations.slice(startIndex, startIndex + itemsPerSlide)
  }, [filteredDestinations, currentSlide, itemsPerSlide])

  // Memoized current special slide items
  const currentSpecialSlideItems = useMemo((): readonly Destination[] => {
    const startIndex = currentSpecialSlide * itemsPerSlide
    return specialTours.slice(startIndex, startIndex + itemsPerSlide)
  }, [specialTours, currentSpecialSlide, itemsPerSlide])

  // Memoized current seasonal slide items
  const currentSeasonalSlideItems = useMemo((): readonly Destination[] => {
    const startIndex = currentSeasonalSlide * itemsPerSlide
    return seasonalTours.slice(startIndex, startIndex + itemsPerSlide)
  }, [seasonalTours, currentSeasonalSlide, itemsPerSlide])

  // Memoized total slides
  const totalSlides = useMemo((): number => {
    return Math.ceil(filteredDestinations.length / itemsPerSlide)
  }, [filteredDestinations.length, itemsPerSlide])

  // Memoized special tours slides
  const specialTotalSlides = useMemo((): number => {
    return Math.ceil(specialTours.length / itemsPerSlide)
  }, [specialTours.length, itemsPerSlide])

  // Memoized seasonal tours slides
  const seasonalTotalSlides = useMemo((): number => {
    return Math.ceil(seasonalTours.length / itemsPerSlide)
  }, [seasonalTours.length, itemsPerSlide])

  // Navigation functions with useTransition for better UX
  const nextSlide = useCallback((): void => {
    startTransition((): void => {
      setCurrentSlide(prev => (prev + 1) % totalSlides)
    })
  }, [totalSlides, startTransition])

  const prevSlide = useCallback((): void => {
    startTransition((): void => {
      setCurrentSlide(prev => (prev - 1 + totalSlides) % totalSlides)
    })
  }, [totalSlides, startTransition])

  const handleSlideIndicatorClick = useCallback((index: number): void => {
    startTransition((): void => {
      setCurrentSlide(index)
    })
  }, [startTransition])

  const handleCategoryChange = useCallback((categoryId: string): void => {
    startTransition((): void => {
      setActiveCategory(categoryId)
      setCurrentSlide(0) // Reset to first slide when changing category
    })
  }, [startTransition])

  // Special tours navigation functions
  const nextSpecialSlide = useCallback((): void => {
    startTransition((): void => {
      setCurrentSpecialSlide(prev => (prev + 1) % specialTotalSlides)
    })
  }, [specialTotalSlides, startTransition])

  const prevSpecialSlide = useCallback((): void => {
    startTransition((): void => {
      setCurrentSpecialSlide(prev => (prev - 1 + specialTotalSlides) % specialTotalSlides)
    })
  }, [specialTotalSlides, startTransition])

  const handleSpecialSlideIndicatorClick = useCallback((index: number): void => {
    startTransition((): void => {
      setCurrentSpecialSlide(index)
    })
  }, [startTransition])

  // Seasonal tours navigation functions
  const nextSeasonalSlide = useCallback((): void => {
    startTransition((): void => {
      setCurrentSeasonalSlide(prev => (prev + 1) % seasonalTotalSlides)
    })
  }, [seasonalTotalSlides, startTransition])

  const prevSeasonalSlide = useCallback((): void => {
    startTransition((): void => {
      setCurrentSeasonalSlide(prev => (prev - 1 + seasonalTotalSlides) % seasonalTotalSlides)
    })
  }, [seasonalTotalSlides, startTransition])

  const handleSeasonalSlideIndicatorClick = useCallback((index: number): void => {
    startTransition((): void => {
      setCurrentSeasonalSlide(index)
    })
  }, [startTransition])

  // Optimized helper functions
  const renderStars = useCallback((rating: number = 0): React.JSX.Element => (
    <div className="flex gap-0.5" role="img" aria-label={`Rating: ${rating} out of 5 stars`}>
      {Array.from({ length: 5 }, (_, i) => (
        <FaStar 
          key={i} 
          className={`h-4 w-4 ${i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300 dark:text-gray-600'}`} 
          aria-hidden="true"
        />
      ))}
    </div>
  ), [])


  const getProductImage = useCallback((destination: Destination): string => {
    return destination.image_url || destination.image || '/images/tour-image.jpg'
  }, [])

  const getProductTitle = useCallback((destination: Destination): string => {
    return destination.title || destination.name || 'Tour'
  }, [])

  const getProductPrice = useCallback((destination: Destination): string => {
    if (destination.starting_price != null && destination.starting_price > 0) {
      return `From $${destination.starting_price.toLocaleString()}`
    }
    return 'Price not available'
  }, [])

  // Error boundary component
  if (loadError) {
    return (
      <section className="py-16 bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <div className="text-6xl mb-4 animate-bounce" role="img" aria-label="Sad face">😔</div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Failed to load tours
            </h2>
            <Button
              onClick={fetchTours}
              disabled={isLoading}
              variant="default"
              size="lg"
            >
              {isLoading ? 'Loading...' : 'Try Again'}
            </Button>
          </div>
        </div>
      </section>
    )
  }

  // Don't render the section if there are no tours and not loading
  if (!isLoading && !loadError && apiDestinations.length === 0) {
    return null;
  }

  return (
    <section className="relative py-12 sm:py-16 lg:py-20 overflow-hidden" role="region" aria-label="Package Trips">
      {/* Background - Modern gradient matching hero */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50/80 via-white to-secondary-50/80 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900" />

      {/* Floating particles effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(15)].map((_, i) => {
          // Deterministic positions for SSR consistency
          const positions = [
            { left: 31.78, top: 51.37 },
            { left: 3.77, top: 37.41 },
            { left: 85.54, top: 49.77 },
            { left: 2.78, top: 20.98 },
            { left: 68.42, top: 31.29 },
            { left: 59.20, top: 31.34 },
            { left: 96.71, top: 34.52 },
            { left: 28.25, top: 90.84 },
            { left: 4.99, top: 72.11 },
            { left: 71.36, top: 38.27 },
            { left: 98.85, top: 84.92 },
            { left: 15.38, top: 5.56 },
            { left: 84.06, top: 28.31 },
            { left: 96.63, top: 79.54 },
            { left: 29.52, top: 2.08 },
          ];

          const pos = positions[i] || { left: 50, top: 50 };

          return (
            <div
              key={i}
              className="absolute w-1 h-1 bg-primary-400/30 rounded-full animate-pulse"
              style={{
                left: `${pos.left}%`,
                top: `${pos.top}%`,
                animationDelay: `${(i * 0.2) % 3}s`,
                animationDuration: `${3 + (i * 0.1) % 2}s`,
              }}
            />
          );
        })}
      </div>

      <div className="container mx-auto px-4 relative z-10">
        {/* Seasonal Tours Section */}
        {seasonalTours.length > 0 && (
          <div className="mb-12 sm:mb-16 lg:mb-20">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                {tHome('seasonalTours') || 'Seasonal Tours'}
              </h3>
              <Link href="/tours?seasonal=true" className="text-secondary-600 hover:text-primary-600 dark:text-secondary-400 dark:hover:text-primary-400 font-medium transition-colors duration-300">
                {tHome('viewAllSeasonalTours') || 'View All Seasonal Tours'}
              </Link>
            </div>
            {seasonalTours.length === 0 ? (
              <div className="text-gray-500 dark:text-gray-400 text-sm">{tHome('noSeasonalTours') || 'No seasonal tours available'}</div>
            ) : (
              <div className="relative">
                {/* Seasonal Tours Slider Container */}
                <div
                  className="flex gap-8 transition-transform duration-500 ease-in-out relative"
                  style={{
                    transform: `translateX(-${currentSeasonalSlide * (100 / itemsPerSlide)}%)`
                  }}
                >
                  {currentSeasonalSlideItems.map((tour) => (
                    <div key={`seasonal-${tour.id}`} className="flex-shrink-0 w-full" style={{ width: `calc(100% / ${itemsPerSlide})` }}>
                      <Link
                        href={tour.slug ? `/${typeof window !== 'undefined' ? (window.location.pathname.split('/')[1] || 'en') : 'en'}/tours/${tour.slug}` : '#'}
                        className="block group"
                        aria-label={`View details for ${getProductTitle(tour)}`}
                      >
                        <article
                          className="group relative bg-white/20 dark:bg-gray-800/20 backdrop-blur-md rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-700 overflow-hidden border border-white/30 dark:border-gray-700/30 hover:scale-105 hover:shadow-secondary-500/25 cursor-pointer"
                        >
                          {/* Shimmer Effect */}
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out z-10" />

                          {/* Image Container */}
                          <div className="relative h-64 overflow-hidden">
                            <OptimizedImage
                              src={getProductImage(tour)}
                              alt={getProductTitle(tour)}
                              fill
                              className="object-cover transition-all duration-700 group-hover:scale-110 group-hover:rotate-1"
                              priority={false}
                              sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                              fallbackSrc={(() => {
                                const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';
                                return `${backendUrl}/media/defaults/tour-default.png`;
                              })()}
                            />

                            {/* Overlay */}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500" />

                            {/* Top Badges */}
                            <div className="absolute top-4 left-4 z-20 flex flex-col space-y-2">
                              <span className="inline-flex items-center px-3 py-1 rounded-2xl text-xs font-medium bg-gradient-to-r from-green-500/20 to-blue-500/20 backdrop-blur-xl text-green-800 dark:text-green-200 border border-green-400/30 animate-fade-in-down">
                                <FaMapPin className="h-3 w-3 mr-1" aria-hidden="true" />
                                Seasonal
                              </span>

                              {tour.category_name && (
                                <span className="inline-flex items-center px-3 py-1 rounded-2xl text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30 animate-fade-in-down">
                                  <FaMapPin className="h-3 w-3 mr-1" aria-hidden="true" />
                                  {tour.category_name}
                                </span>
                              )}
                            </div>

                            {/* Bottom Badges */}
                            <div className="absolute bottom-4 z-20 flex items-center justify-between w-full px-4">
                              <span className="inline-flex items-center px-3 py-1 rounded-2xl text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30 animate-fade-in-down max-w-[200px] truncate">
                                {getProductTitle(tour)}
                              </span>

                              <span className="inline-flex items-center px-3 py-1 rounded-2xl text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30">
                                {getProductPrice(tour)}
                              </span>
                            </div>
                          </div>

                          {/* Card Content */}
                          <div className="px-6 pb-6 relative z-10">
                            <div className="border-t border-white/20 dark:border-gray-700/20 pt-4">
                              <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                  <div className="text-sm text-gray-600 dark:text-gray-400">
                                    <div className="font-medium group-hover:text-primary-600 transition-colors duration-300">
                                      Duration: {tour.duration_hours} hours
                                    </div>
                                  </div>

                                  {/* Rating */}
                                  <div className="flex items-center">
                                    {renderStars(tour.rating || 0)}
                                    <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                                      {tour.rating ? tour.rating.toFixed(1) : '0.0'}
                                    </span>
                                    {(tour.review_count || 0) > 0 && (
                                      <span className="ml-1 text-sm text-gray-500 group-hover:text-primary-600 transition-colors duration-300">
                                        ({tour.review_count || 0} reviews)
                                      </span>
                                    )}
                                  </div>
                                </div>

                                {/* Location Info */}
                                <div className="text-xs text-gray-500 dark:text-gray-400 group-hover:text-primary-600 transition-colors duration-300">
                                  <div className="flex items-center gap-2">
                                    <FaMapPin className="h-3 w-3" />
                                    <span>{tour.location || 'Location not specified'}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </article>
                      </Link>
                    </div>
                  ))}
                </div>

                {/* Seasonal Tours Navigation */}
                <div className="flex sm:hidden justify-center gap-4 mt-6 w-full">
                  <button
                    onClick={prevSeasonalSlide}
                    disabled={isPending || seasonalTotalSlides <= 1}
                    className="w-12 h-12 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg flex items-center justify-center text-2xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label={isRTL ? "Next seasonal slide" : "Previous seasonal slide"}
                  >
                    {isRTL ? <FaChevronRight /> : <FaChevronLeft />}
                  </button>
                  <button
                    onClick={nextSeasonalSlide}
                    disabled={isPending || seasonalTotalSlides <= 1}
                    className="w-12 h-12 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg flex items-center justify-center text-2xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label={isRTL ? "Previous seasonal slide" : "Next seasonal slide"}
                  >
                    {isRTL ? <FaChevronLeft /> : <FaChevronRight />}
                  </button>
                </div>

                {/* Seasonal Tours Slide Indicators */}
                {seasonalTotalSlides > 1 && (
                  <div className="flex justify-center mt-6 gap-2 rtl:gap-2" role="tablist" aria-label="Seasonal tours slide navigation">
                    {Array.from({ length: seasonalTotalSlides }).map((_, index) => (
                      <button
                        key={index}
                        onClick={(): void => handleSeasonalSlideIndicatorClick(index)}
                        disabled={isPending}
                        role="tab"
                        aria-selected={currentSeasonalSlide === index}
                        aria-label={`Go to seasonal tours slide ${index + 1}`}
                        className={`w-3 h-3 rounded-full transition-all duration-300 hover:scale-125 focus:outline-none focus:ring-2 focus:ring-primary-400 ${
                          currentSeasonalSlide === index
                            ? 'bg-gradient-to-r from-primary-500 to-secondary-500 scale-125 shadow-lg shadow-primary-500/50'
                            : 'bg-gray-300/50 hover:bg-gray-400/50 backdrop-blur-sm'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      />
                    ))}
                  </div>
                )}

                {/* Seasonal Tours Desktop Navigation */}
                <button
                  onClick={prevSeasonalSlide}
                  disabled={isPending || seasonalTotalSlides <= 1}
                  className={`hidden lg:flex absolute top-[55%] -translate-y-[40%] z-20 w-16 h-16 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg items-center justify-center text-3xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed ${
                    isRTL
                      ? 'right-0 translate-x-3'
                      : 'left-0 -translate-x-3'
                  }`}
                  aria-label={isRTL ? "Next seasonal slide" : "Previous seasonal slide"}
                >
                  {isRTL ? <FaChevronRight /> : <FaChevronLeft />}
                </button>
                <button
                  onClick={nextSeasonalSlide}
                  disabled={isPending || seasonalTotalSlides <= 1}
                  className={`hidden lg:flex absolute top-[55%] -translate-y-[40%] z-20 w-16 h-16 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg items-center justify-center text-3xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed ${
                    isRTL
                      ? 'left-0 -translate-x-3'
                      : 'right-0 translate-x-3'
                  }`}
                  aria-label={isRTL ? "Previous seasonal slide" : "Next seasonal slide"}
                >
                  {isRTL ? <FaChevronLeft /> : <FaChevronRight />}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Special Tours Section */}
        {specialTours.length > 0 && (
          <div className="mb-12 sm:mb-16 lg:mb-20">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
                {tHome('specialTours') || 'Special Tours'}
              </h3>
              <Link href="/tours?featured=true" className="text-secondary-600 hover:text-primary-600 dark:text-secondary-400 dark:hover:text-primary-400 font-medium transition-colors duration-300">
                {tHome('viewAllTours') || 'View All Tours'}
              </Link>
            </div>
            {specialTours.length === 0 ? (
              <div className="text-gray-500 dark:text-gray-400 text-sm">{tHome('noSpecialTours') || 'No special tours available'}</div>
            ) : (
              <div className="relative">
                {/* Special Tours Slider Container */}
                <div
                  className="flex gap-8 transition-transform duration-500 ease-in-out relative"
                  style={{
                    transform: `translateX(-${currentSpecialSlide * (100 / itemsPerSlide)}%)`
                  }}
                >
                  {currentSpecialSlideItems.map((tour) => (
                    <div key={`special-${tour.id}`} className="flex-shrink-0 w-full" style={{ width: `calc(100% / ${itemsPerSlide})` }}>
                      <Link
                        href={tour.slug ? `/${typeof window !== 'undefined' ? (window.location.pathname.split('/')[1] || 'en') : 'en'}/tours/${tour.slug}` : '#'}
                        className="block group"
                        aria-label={`View details for ${getProductTitle(tour)}`}
                      >
                        <article
                          className="group relative bg-white/20 dark:bg-gray-800/20 backdrop-blur-md rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-700 overflow-hidden border border-white/30 dark:border-gray-700/30 hover:scale-105 hover:shadow-secondary-500/25 cursor-pointer"
                        >
                          {/* Shimmer Effect */}
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out z-10" />

                          {/* Image Container */}
                          <div className="relative h-64 overflow-hidden">
                            <OptimizedImage
                              src={getProductImage(tour)}
                              alt={getProductTitle(tour)}
                              fill
                              className="object-cover transition-all duration-700 group-hover:scale-110 group-hover:rotate-1"
                              priority={false}
                              sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                              fallbackSrc={(() => {
                                const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';
                                return `${backendUrl}/media/defaults/tour-default.png`;
                              })()}
                            />

                            {/* Overlay */}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500" />

                            {/* Top Badges */}
                            <div className="absolute top-4 left-4 z-20 flex flex-col space-y-2">
                              <span className="inline-flex items-center px-3 py-1 rounded-2xl text-xs font-medium bg-gradient-to-r from-yellow-500/20 to-orange-500/20 backdrop-blur-xl text-yellow-800 dark:text-yellow-200 border border-yellow-400/30 animate-fade-in-down">
                                <FaMapPin className="h-3 w-3 mr-1" aria-hidden="true" />
                                Special
                              </span>

                              {tour.category_name && (
                                <span className="inline-flex items-center px-3 py-1 rounded-2xl text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30 animate-fade-in-down">
                                  <FaMapPin className="h-3 w-3 mr-1" aria-hidden="true" />
                                  {tour.category_name}
                                </span>
                              )}
                            </div>

                            {/* Bottom Badges */}
                            <div className="absolute bottom-4 z-20 flex items-center justify-between w-full px-4">
                              <span className="inline-flex items-center px-3 py-1 rounded-2xl text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30 animate-fade-in-down max-w-[200px] truncate">
                                {getProductTitle(tour)}
                              </span>

                              <span className="inline-flex items-center px-3 py-1 rounded-2xl text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30">
                                {getProductPrice(tour)}
                              </span>
                            </div>
                          </div>

                          {/* Card Content */}
                          <div className="px-6 pb-6 relative z-10">
                            <div className="border-t border-white/20 dark:border-gray-700/20 pt-4">
                              <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                  <div className="text-sm text-gray-600 dark:text-gray-400">
                                    <div className="font-medium group-hover:text-primary-600 transition-colors duration-300">
                                      Duration: {tour.duration_hours} hours
                                    </div>
                                  </div>

                                  {/* Rating */}
                                  <div className="flex items-center">
                                    {renderStars(tour.rating || 0)}
                                    <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                                      {tour.rating ? tour.rating.toFixed(1) : '0.0'}
                                    </span>
                                    {(tour.review_count || 0) > 0 && (
                                      <span className="ml-1 text-sm text-gray-500 group-hover:text-primary-600 transition-colors duration-300">
                                        ({tour.review_count || 0} reviews)
                                      </span>
                                    )}
                                  </div>
                                </div>

                                {/* Location Info */}
                                <div className="text-xs text-gray-500 dark:text-gray-400 group-hover:text-primary-600 transition-colors duration-300">
                                  <div className="flex items-center gap-2">
                                    <FaMapPin className="h-3 w-3" />
                                    <span>{tour.location || 'Location not specified'}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </article>
                      </Link>
                    </div>
                  ))}
                </div>

                {/* Special Tours Navigation */}
                <div className="flex sm:hidden justify-center gap-4 mt-6 w-full">
                  <button
                    onClick={prevSpecialSlide}
                    disabled={isPending || specialTotalSlides <= 1}
                    className="w-12 h-12 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg flex items-center justify-center text-2xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label={isRTL ? "Next slide" : "Previous slide"}
                  >
                    {isRTL ? <FaChevronRight /> : <FaChevronLeft />}
                  </button>
                  <button
                    onClick={nextSpecialSlide}
                    disabled={isPending || specialTotalSlides <= 1}
                    className="w-12 h-12 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg flex items-center justify-center text-2xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed"
                    aria-label={isRTL ? "Previous slide" : "Next slide"}
                  >
                    {isRTL ? <FaChevronLeft /> : <FaChevronRight />}
                  </button>
                </div>

                {/* Special Tours Slide Indicators */}
                {specialTotalSlides > 1 && (
                  <div className="flex justify-center mt-6 gap-2 rtl:gap-2" role="tablist" aria-label="Special tours slide navigation">
                    {Array.from({ length: specialTotalSlides }).map((_, index) => (
                      <button
                        key={index}
                        onClick={(): void => handleSpecialSlideIndicatorClick(index)}
                        disabled={isPending}
                        role="tab"
                        aria-selected={currentSpecialSlide === index}
                        aria-label={`Go to special tours slide ${index + 1}`}
                        className={`w-3 h-3 rounded-full transition-all duration-300 hover:scale-125 focus:outline-none focus:ring-2 focus:ring-primary-400 ${
                          currentSpecialSlide === index
                            ? 'bg-gradient-to-r from-primary-500 to-secondary-500 scale-125 shadow-lg shadow-primary-500/50'
                            : 'bg-gray-300/50 hover:bg-gray-400/50 backdrop-blur-sm'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      />
                    ))}
                  </div>
                )}

                {/* Special Tours Desktop Navigation */}
                <button
                  onClick={prevSpecialSlide}
                  disabled={isPending || specialTotalSlides <= 1}
                  className={`hidden lg:flex absolute top-[55%] -translate-y-[40%] z-20 w-16 h-16 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg items-center justify-center text-3xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed ${
                    isRTL
                      ? 'right-0 translate-x-3'
                      : 'left-0 -translate-x-3'
                  }`}
                  aria-label={isRTL ? "Next special slide" : "Previous special slide"}
                >
                  {isRTL ? <FaChevronRight /> : <FaChevronLeft />}
                </button>
                <button
                  onClick={nextSpecialSlide}
                  disabled={isPending || specialTotalSlides <= 1}
                  className={`hidden lg:flex absolute top-[55%] -translate-y-[40%] z-20 w-16 h-16 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg items-center justify-center text-3xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed ${
                    isRTL
                      ? 'left-0 -translate-x-3'
                      : 'right-0 translate-x-3'
                  }`}
                  aria-label={isRTL ? "Previous special slide" : "Next special slide"}
                >
                  {isRTL ? <FaChevronLeft /> : <FaChevronRight />}
                </button>
              </div>
            )}
          </div>
        )}

        {/* Section Header - Modern design */}
        <div className="text-center mb-6 sm:mb-8 lg:mb-10">
          {/* Badge with modern styling */}
          <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-primary-500/10 to-secondary-500/10 backdrop-blur-sm rounded-full border border-primary-200/50 dark:border-primary-700/50 mb-4">
            <span className="text-sm uppercase tracking-wider text-primary-600 dark:text-primary-400 font-semibold">
              Premium Tours
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            {tHome('featuredTours') || 'Discover Amazing Destinations'}
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            {tHome('featuredToursDesc') || 'Explore handpicked tours and experiences crafted for unforgettable adventures and memories that last a lifetime.'}
          </p>
        </div>

        {/* Category Tabs */}
        <nav className="flex flex-col items-center gap-4 sm:gap-6 mb-8 sm:mb-10 lg:mb-12" role="tablist" aria-label="Tour categories">
          {/* Visible Categories */}
          <div className="flex flex-wrap justify-center gap-4">
            {visibleCategories.map((category, index) => (
              <button
                key={category.id}
                onClick={(): void => handleCategoryChange(category.id)}
                disabled={isPending}
                role="tab"
                aria-selected={activeCategory === category.id}
                aria-controls={`category-${category.id}`}
                className={`px-6 py-3 rounded-full font-semibold transition-all duration-500 hover:scale-105 active:scale-95 backdrop-blur-md border focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 ${
                  activeCategory === category.id
                    ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg shadow-primary-500/50 border-primary-400/50'
                    : 'bg-white/20 dark:bg-gray-700/20 text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 border-white/30 dark:border-gray-600/30'
                } animate-fade-in-up disabled:opacity-50 disabled:cursor-not-allowed`}
                style={{ animationDelay: `${0.3 + index * 0.1}s` }}
              >
                {category.name}
              </button>
            ))}
          </div>

          {/* Hidden Categories (Collapsible) */}
          {hiddenCategoriesCount > 0 && (
            <div className={`overflow-hidden transition-all duration-500 ease-in-out ${
              showAllCategories ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
            }`}>
              <div className="flex flex-wrap justify-center gap-4 pt-4">
                {activeCategories.slice(visibleCategoriesCount).map((category) => (
                  <button
                    key={category.id}
                    onClick={(): void => handleCategoryChange(category.id)}
                    disabled={isPending}
                    role="tab"
                    aria-selected={activeCategory === category.id}
                    aria-controls={`category-${category.id}`}
                    className={`px-6 py-3 rounded-full font-semibold transition-all duration-500 hover:scale-105 active:scale-95 backdrop-blur-md border focus:outline-none focus:ring-2 focus:ring-primary-400 focus:ring-offset-2 ${
                      activeCategory === category.id
                        ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg shadow-primary-500/50 border-primary-400/50'
                        : 'bg-white/20 dark:bg-gray-700/20 text-gray-700 dark:text-gray-300 hover:bg-white/30 dark:hover:bg-gray-700/30 border-white/30 dark:border-gray-600/30'
                    } animate-fade-in-up disabled:opacity-50 disabled:cursor-not-allowed`}
                    style={{ animationDelay: `${0.1}s` }}
                  >
                    {category.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Toggle Button */}
          {hiddenCategoriesCount > 0 && (
            <button
              onClick={toggleCategories}
              className="group flex items-center gap-2 px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-all duration-300 hover:scale-105 active:scale-95 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 rounded-lg"
              aria-expanded={showAllCategories}
              aria-controls="hidden-categories"
            >
              <span className="transition-transform duration-300 group-hover:scale-110">
                {showAllCategories ? (
                  <>
                    <span className="hidden sm:inline">Hide</span>
                    <span className="sm:hidden">Hide</span>
                    <span className="ml-1">({hiddenCategoriesCount})</span>
                  </>
                ) : (
                  <>
                    <span className="hidden sm:inline">Show</span>
                    <span className="sm:hidden">Show</span>
                    <span className="ml-1">+{hiddenCategoriesCount} More</span>
                  </>
                )}
              </span>
              <svg
                className={`w-4 h-4 transition-transform duration-300 ${
                  showAllCategories ? 'rotate-180' : 'rotate-0'
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          )}
        </nav>

        {/* Carousel Container */}
        <div className="relative flex flex-col items-center justify-center w-full">
          {/* Cards Row */}
          <div className="overflow-visible w-full pb-8">
            <div
              className={`grid gap-8 transition-transform duration-500 grid-cols-1 ${itemsPerSlide === 2 ? 'sm:grid-cols-2' : ''} ${itemsPerSlide === 3 ? 'md:grid-cols-3' : ''} ${itemsPerSlide === 4 ? 'lg:grid-cols-4' : ''}`}
              style={{ width: '100%' }}
              role="region"
              aria-label="Tour cards"
              aria-live="polite"
            >
              {isLoading ? (
                // Skeleton loading state
                Array.from({ length: Math.max(itemsPerSlide * 2, 4) }).map((_, index) => (
                  <article
                    key={`skeleton-${index}`}
                    className={`flex flex-col ${index % 2 === 1 ? 'translate-y-8' : 'translate-y-0'} w-full animate-fade-in-up`}
                    style={{ animationDelay: `${0.5 + index * 0.1}s` }}
                    aria-hidden="true"
                  >
                    <div className="bg-white/20 dark:bg-gray-800/20 backdrop-blur-md rounded-2xl shadow-lg overflow-hidden border border-white/30 dark:border-gray-700/30">
                      <div className="w-full h-64 bg-gradient-to-r from-gray-200/50 to-gray-300/50 dark:from-gray-700/50 dark:to-gray-600/50 animate-pulse" />
                      <div className="p-6">
                        <div className="h-6 bg-gradient-to-r from-gray-200/50 to-gray-300/50 dark:from-gray-700/50 dark:to-gray-600/50 rounded animate-pulse mb-3" />
                        <div className="h-4 bg-gradient-to-r from-gray-200/50 to-gray-300/50 dark:from-gray-700/50 dark:to-gray-600/50 rounded animate-pulse mb-2" />
                        <div className="h-4 bg-gradient-to-r from-gray-200/50 to-gray-300/50 dark:from-gray-700/50 dark:to-gray-600/50 rounded animate-pulse w-2/3" />
                      </div>
                    </div>
                  </article>
                ))
              ) : (
                // Actual tour cards
                currentSlideItems.map((destination) => (
                  <Link
                    key={`tour-${destination.id}`}
                    href={destination.slug ? `/${typeof window !== 'undefined' ? (window.location.pathname.split('/')[1] || 'en') : 'en'}/tours/${destination.slug}` : '#'}
                    className="block group"
                    aria-label={`View details for ${getProductTitle(destination)}`}
                  >
                    <div className="relative w-full rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border-0 overflow-hidden bg-white dark:bg-gray-900 hover:scale-[1.01] hover:-translate-y-0.5 min-h-[420px]">
                      {/* Modern Gradient Background */}
                      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/20 via-white to-purple-50/10 dark:from-gray-800 dark:via-gray-900 dark:to-gray-800" />

                      {/* Image Section */}
                      <div className="relative h-64 overflow-hidden">
                        <OptimizedImage
                          src={getProductImage(destination)}
                          alt={getProductTitle(destination)}
                          fill
                          className="w-full h-full object-cover transition-all duration-300 group-hover:scale-105"
                          fallbackSrc={(() => {
                            const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';
                            return `${backendUrl}/media/defaults/tour-default.png`;
                          })()}
                          sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                          priority={false}
                        />

                        {/* Modern Overlay */}
                        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300" />

                        {/* Top Badges */}
                        <div className="absolute top-2 left-2 z-20 flex flex-col gap-1">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-white/20 backdrop-blur-md text-white shadow-md border border-white/30">
                            <FaMapPin className="h-2.5 w-2.5 mr-1" />
                            {destination.category_name || 'Tour'}
                          </span>
                        </div>

                        {/* Price Badge on Image */}
                        <div className="absolute bottom-3 right-3 z-20">
                          <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-xl px-3 py-2 shadow-lg border border-white/20 dark:border-gray-700/20">
                            <div className="text-sm font-bold text-primary-600 dark:text-primary-400">
                              {getProductPrice(destination)}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Content Section */}
                      <div className="p-4 flex flex-col h-full relative z-10">
                        <div className="flex-1">
                          <h3 className={`text-base font-bold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300 line-clamp-2 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                            {getProductTitle(destination)}
                          </h3>

                          <p className={`text-gray-600 dark:text-gray-300 text-xs mb-3 line-clamp-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                            {destination.description || destination.short_description || 'No description available'}
                          </p>

                          {/* Rating & Reviews */}
                          <div className="flex items-center gap-2 mb-3">
                            <div className="flex items-center">
                              {renderStars(destination.rating || 0)}
                              <span className="ml-1 text-xs font-medium text-gray-600 dark:text-gray-400">
                                {destination.rating ? destination.rating.toFixed(1) : '0.0'}
                              </span>
                            </div>
                            {(destination.review_count || 0) > 0 && (
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                ({destination.review_count})
                              </span>
                            )}
                          </div>

                          {/* Details Grid */}
                          <div className="grid grid-cols-1 gap-2 mb-3">
                            <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                              <FaMapPin className="h-3.5 w-3.5 text-red-500" />
                              <span className="truncate">{destination.location || 'Location not specified'}</span>
                            </div>

                            {destination.duration_hours && (
                              <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                                <FaMapPin className="h-3.5 w-3.5 text-blue-500" />
                                <span>{destination.duration_hours} hours</span>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Action Button */}
                        <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {(() => {
                              if (typeof destination.next_schedule_capacity_available === 'number' && typeof destination.next_schedule_capacity_total === 'number') {
                                return destination.next_schedule_capacity_available > 0 ?
                                  `${destination.next_schedule_capacity_available} of ${destination.next_schedule_capacity_total} Available` :
                                  'Sold Out';
                              }
                              return destination.next_schedule_capacity_available === 0 ? 'Sold Out' : 'Available';
                            })()}
                          </div>
                          <div className="flex items-center text-blue-600 dark:text-blue-400 font-medium group-hover:gap-1 transition-all duration-300">
                            <span className="text-xs">View Details</span>
                            <FaChevronRight className="h-3 w-3 ml-1 group-hover:translate-x-0.5 transition-transform duration-300" />
                          </div>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>

          {/* Mobile Navigation */}
          <div className="flex sm:hidden justify-center gap-4 mt-2 w-full">
            <button
              onClick={prevSlide}
              disabled={isPending || totalSlides <= 1}
              className="w-12 h-12 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg flex items-center justify-center text-2xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label={isRTL ? "Next slide" : "Previous slide"}
            >
              {isRTL ? <FaChevronRight /> : <FaChevronLeft />}
            </button>
            <button
              onClick={nextSlide}
              disabled={isPending || totalSlides <= 1}
              className="w-12 h-12 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg flex items-center justify-center text-2xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label={isRTL ? "Previous slide" : "Next slide"}
            >
              {isRTL ? <FaChevronLeft /> : <FaChevronRight />}
            </button>
          </div>

          {/* Slide Indicators */}
          {totalSlides > 1 && (
            <div className="flex justify-center mt-6 gap-2 rtl:gap-2" role="tablist" aria-label="Slide navigation">
              {Array.from({ length: totalSlides }).map((_, index) => (
                <button
                  key={index}
                  onClick={(): void => handleSlideIndicatorClick(index)}
                  disabled={isPending}
                  role="tab"
                  aria-selected={currentSlide === index}
                  aria-label={`Go to slide ${index + 1}`}
                  className={`w-3 h-3 rounded-full transition-all duration-300 hover:scale-125 focus:outline-none focus:ring-2 focus:ring-primary-400 ${
                    currentSlide === index
                      ? 'bg-gradient-to-r from-primary-500 to-secondary-500 scale-125 shadow-lg shadow-primary-500/50'
                      : 'bg-gray-300/50 hover:bg-gray-400/50 backdrop-blur-sm'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                />
              ))}
            </div>
          )}
        </div>

        {/* Desktop Navigation - Only show on large screens and above */}
        <button
          onClick={prevSlide}
          disabled={isPending || totalSlides <= 1}
          className={`hidden lg:flex absolute top-[55%] -translate-y-[40%] z-20 w-16 h-16 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg items-center justify-center text-3xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed ${
            isRTL
              ? 'right-0 translate-x-3'
              : 'left-0 -translate-x-3'
          }`}
          aria-label={isRTL ? "Next slide" : "Previous slide"}
        >
          {isRTL ? <FaChevronRight /> : <FaChevronLeft />}
        </button>
        <button
          onClick={nextSlide}
          disabled={isPending || totalSlides <= 1}
          className={`hidden lg:flex absolute top-[55%] -translate-y-[40%] z-20 w-16 h-16 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg items-center justify-center text-3xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-primary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed ${
            isRTL
              ? 'left-0 -translate-x-3'
              : 'right-0 translate-x-3'
          }`}
          aria-label={isRTL ? "Previous slide" : "Next slide"}
        >
          {isRTL ? <FaChevronLeft /> : <FaChevronRight />}
        </button>
      </div>

      {/* CSS Animations */}
      <style jsx>{`
        @keyframes fade-in-down {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fade-in-down {
          animation: fade-in-down 0.6s ease-out forwards;
        }
        
        .animate-fade-in-up {
          animation: fade-in-up 0.6s ease-out forwards;
        }
        
        .animate-fade-in-up:nth-child(1) { animation-delay: 0.1s; }
        .animate-fade-in-up:nth-child(2) { animation-delay: 0.2s; }
        .animate-fade-in-up:nth-child(3) { animation-delay: 0.3s; }
        .animate-fade-in-up:nth-child(4) { animation-delay: 0.4s; }
      `}</style>
    </section>
  )
} 