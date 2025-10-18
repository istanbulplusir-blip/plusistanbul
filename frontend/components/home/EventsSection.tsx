'use client'

import { useEffect, useMemo, useState, useCallback, useRef } from 'react'
import { useTranslations } from 'next-intl'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import OptimizedImage from '@/components/common/OptimizedImage'
import { getEvents, getHomeEvents } from '@/lib/api/events'
import type { Event, EventPerformance } from '@/lib/types/api'
import { FaMapPin, FaStar, FaFire, FaCalendar, FaUsers, FaChevronLeft, FaChevronRight } from 'react-icons/fa'
import { Button } from '@/components/ui/Button';

export default function EventsSection() {
  const router = useRouter()
  const tHome = useTranslations('home')
  const tEvents = useTranslations('events')
  const [events, setEvents] = useState<Event[]>([])
  const [categorizedEvents, setCategorizedEvents] = useState<{
    upcoming: Event[];
    past: Event[];
    special: Event[];
    featured: Event[];
    popular: Event[];
  }>({
    upcoming: [],
    past: [],
    special: [],
    featured: [],
    popular: []
  })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isRTL, setIsRTL] = useState(false)
  
  // Touch interaction state for mobile
  const [touchedCard, setTouchedCard] = useState<string | null>(null)
  const [touchTimeout, setTouchTimeout] = useState<NodeJS.Timeout | null>(null)
  
  // Slider state
  const [currentSlide, setCurrentSlide] = useState(0)
  const [itemsPerSlide, setItemsPerSlide] = useState(3)
  const sliderRef = useRef<HTMLDivElement>(null)

  // Detect RTL language
  useEffect(() => {
    const htmlDir = document.documentElement.dir
    setIsRTL(htmlDir === 'rtl')
  }, [])

  // Memoize utility functions to prevent unnecessary recalculations
  const formatDate = useCallback((dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: '2-digit' })
    } catch {
      return '-'
    }
  }, [])

  const formatTime = useCallback((timeString: string) => {
    try {
      return new Date(`2000-01-01T${timeString}`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    } catch {
      return '-'
    }
  }, [])

  const formatPrice = useCallback((price: number, currency: string) => {
    try {
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: currency || 'USD' }).format(price || 0)
    } catch {
      return `${price || 0} ${currency || 'USD'}`
    }
  }, [])

  // Helpers to classify events - memoized
  const getNextPerformanceDate = useCallback((ev: Event): Date | null => {
    // Prefer performances
    if (Array.isArray(ev.performances) && ev.performances.length > 0) {
      const dates = ev.performances
        .map((p: { date: string }) => new Date(p?.date))
        .filter((d: Date) => !isNaN(d?.getTime?.()))
        .sort((a: Date, b: Date) => a.getTime() - b.getTime())
      return dates.length > 0 ? dates[0] : null
    }
    // Fallback to performance_calendar
    const cal = ev.performance_calendar as { date: string }[] | undefined
    if (Array.isArray(cal) && cal.length > 0) {
      const dates = cal
        .map((c: { date: string }) => new Date(c?.date))
        .filter((d: Date) => !isNaN(d?.getTime?.()))
        .sort((a: Date, b: Date) => a.getTime() - b.getTime())
      return dates.length > 0 ? dates[0] : null
    }
    return null
  }, [])

  const today = useMemo(() => new Date(new Date().toDateString()), [])
  
  const getNextPerformanceDetails = useCallback((ev: Event): { date: string; start_time: string } | null => {
    if (Array.isArray(ev.performances) && ev.performances.length > 0) {
      const sorted = [...ev.performances].sort((a: { date: string; start_time?: string }, b: { date: string }) => new Date(a?.date).getTime() - new Date(b?.date).getTime())
      const first = sorted[0]
      if (first?.date) {
        return { date: first.date, start_time: first?.start_time || ev.start_time || '' }
      }
    }
    const cal = ev.performance_calendar as { date: string; start_time?: string }[] | undefined
    if (Array.isArray(cal) && cal.length > 0) {
      const sorted = [...cal].sort((a: { date: string; start_time?: string }, b: { date: string }) => new Date(a?.date).getTime() - new Date(b?.date).getTime())
      const first = sorted[0]
      if (first?.date) {
        return { date: first.date, start_time: first?.start_time || ev.start_time || '' }
      }
    }
    return null
  }, [])

  const getEventMinPrice = useCallback((ev: Event): number => {
    const perfMins = (ev.performances || [])
      .map((p: { min_price?: number }) => p?.min_price)
      .filter((v: unknown): v is number => typeof v === 'number' && isFinite(v))
    const ticketMins = (ev.ticket_types || [])
      .map((tt: { price_modifier?: number }) => tt?.price_modifier)
      .filter((v: unknown): v is number => typeof v === 'number' && isFinite(v))
    const candidates: number[] = []
    if (typeof ev.min_price === 'number') candidates.push(ev.min_price)
    if (perfMins.length > 0) candidates.push(Math.min(...perfMins))
    if (ticketMins.length > 0) candidates.push(Math.min(...ticketMins))
    return candidates.length > 0 ? Math.min(...candidates) : 0
  }, [])

  // Memoize computed values - use categorized events if available, otherwise fallback to manual categorization
  const specialEvent = useMemo(() => {
    return categorizedEvents.special[0] || categorizedEvents.featured[0] || events[0]
  }, [categorizedEvents, events])

  const upcomingEvents = useMemo(() => {
    return categorizedEvents.upcoming.length > 0 
      ? categorizedEvents.upcoming 
      : events.filter((ev) => {
          const nd = getNextPerformanceDate(ev)
          return nd !== null && nd >= today
        })
  }, [categorizedEvents.upcoming, events, today, getNextPerformanceDate])

  const pastEvents = useMemo(() => {
    return categorizedEvents.past.length > 0 
      ? categorizedEvents.past 
      : events.filter((ev) => {
          const nd = getNextPerformanceDate(ev)
          return nd !== null && nd < today
        })
  }, [categorizedEvents.past, events, today, getNextPerformanceDate])

  const featuredEvents = useMemo(() => {
    return categorizedEvents.featured.length > 0 
      ? categorizedEvents.featured 
      : events.filter((ev) => ev.is_featured)
  }, [categorizedEvents.featured, events])

  const popularEvents = useMemo(() => {
    return categorizedEvents.popular.length > 0 
      ? categorizedEvents.popular 
      : events.filter((ev) => ev.is_popular)
  }, [categorizedEvents.popular, events])

  // Handle touch events for mobile devices
  const handleTouchStart = useCallback((eventId: string) => {
    if (touchTimeout) {
      clearTimeout(touchTimeout)
    }
    
    if (touchedCard === eventId) {
      // If already touched, toggle off
      setTouchedCard(null)
    } else {
      // Set new touched card
      setTouchedCard(eventId)
    }
  }, [touchedCard, touchTimeout])

  const handleTouchEnd = useCallback(() => {
    // Add a small delay before hiding to allow user to see the content
    const timeout = setTimeout(() => {
      setTouchedCard(null)
    }, 2000) // Show for 2 seconds after touch
    
    setTouchTimeout(timeout)
  }, [])

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (touchTimeout) {
        clearTimeout(touchTimeout)
      }
    }
  }, [touchTimeout])

  // Determine if capacity info should be visible
  const isCapacityVisible = useCallback((eventId: string) => {
    return touchedCard === eventId
  }, [touchedCard])

  // Slider navigation functions
  const nextSlide = useCallback(() => {
    const totalSlides = Math.ceil(upcomingEvents.length / itemsPerSlide)
    setCurrentSlide((prev) => (prev + 1) % totalSlides)
  }, [upcomingEvents.length, itemsPerSlide])

  const prevSlide = useCallback(() => {
    const totalSlides = Math.ceil(upcomingEvents.length / itemsPerSlide)
    setCurrentSlide((prev) => (prev - 1 + totalSlides) % totalSlides)
  }, [upcomingEvents.length, itemsPerSlide])

  const scrollToSlide = useCallback((slideIndex: number) => {
    if (sliderRef.current) {
      const slideWidth = sliderRef.current.scrollWidth / Math.ceil(upcomingEvents.length / itemsPerSlide)
      sliderRef.current.scrollTo({
        left: slideWidth * slideIndex,
        behavior: 'smooth'
      })
    }
    setCurrentSlide(slideIndex)
  }, [upcomingEvents.length, itemsPerSlide])

  // Handle resize for responsive items per slide
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 640) {
        setItemsPerSlide(1)
      } else if (window.innerWidth < 768) {
        setItemsPerSlide(2)
      } else if (window.innerWidth < 1024) {
        setItemsPerSlide(3)
      } else {
        setItemsPerSlide(3)
      }
    }

    handleResize()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Memoize the fetch events function
  const fetchEvents = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      
      // Try to fetch categorized events first
      try {
        const categorizedData = await getHomeEvents()
        setCategorizedEvents({
          upcoming: (categorizedData.upcoming_events || []) as unknown as Event[],
          past: (categorizedData.past_events || []) as unknown as Event[],
          special: (categorizedData.special_events || []) as unknown as Event[],
          featured: (categorizedData.featured_events || []) as unknown as Event[],
          popular: (categorizedData.popular_events || []) as unknown as Event[]
        })
        
        // Deduplicate events within each category and create allEvents
        const deduplicateEvents = (eventsArray: any[]) => { // eslint-disable-line @typescript-eslint/no-explicit-any
          if (!Array.isArray(eventsArray)) return []
          const seen = new Set()
          return eventsArray.filter((event: any) => { // eslint-disable-line @typescript-eslint/no-explicit-any
            if (event && event.id && !seen.has(event.id)) {
              seen.add(event.id)
              return true
            }
            return false
          })
        }

        const deduplicatedCategories = {
          upcoming: deduplicateEvents(categorizedData.upcoming_events || []),
          past: deduplicateEvents(categorizedData.past_events || []),
          special: deduplicateEvents(categorizedData.special_events || []),
          featured: deduplicateEvents(categorizedData.featured_events || []),
          popular: deduplicateEvents(categorizedData.popular_events || [])
        }

        setCategorizedEvents(deduplicatedCategories)

        // Also set all events for backward compatibility
        const allEventsMap = new Map()
        Object.values(deduplicatedCategories).forEach(eventsArray => {
          eventsArray.forEach((event: any) => { // eslint-disable-line @typescript-eslint/no-explicit-any
            if (event && event.id && !allEventsMap.has(event.id)) {
              allEventsMap.set(event.id, event)
            }
          })
        })

        const allEvents = Array.from(allEventsMap.values()) as unknown as Event[]
        setEvents(allEvents)
      } catch (categorizedError) {
        console.warn('Categorized events API not available, falling back to regular API:', categorizedError)
        
        // Fallback to regular events API
        const res = await getEvents({ ordering: '-created_at', page_size: 6 })
        setEvents(Array.isArray(res?.results) ? res.results : [])
        
        // Categorize manually for fallback
        const today = new Date(new Date().toDateString())
        const categorized = {
          upcoming: [] as Event[],
          past: [] as Event[],
          special: [] as Event[],
          featured: [] as Event[],
          popular: [] as Event[]
        }
        
        res?.results?.forEach(event => {
          const nextDate = getNextPerformanceDate(event)
          if (nextDate && nextDate >= today) {
            categorized.upcoming.push(event)
          } else if (nextDate && nextDate < today) {
            categorized.past.push(event)
          }
          
          if (event.performances?.some((p: EventPerformance) => p.is_special)) {
            categorized.special.push(event)
          }
        })
        
        setCategorizedEvents(categorized)
      }
    } catch (err) {
      console.error('Error fetching events:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch events')
      setEvents([])
      setCategorizedEvents({
        upcoming: [],
        past: [],
        special: [],
        featured: [],
        popular: []
      })
    } finally {
      setIsLoading(false)
    }
  }, [getNextPerformanceDate])

  useEffect(() => {
    let isMounted = true
    
    const loadData = async () => {
      if (isMounted) {
        await fetchEvents()
      }
    }
    
    loadData()
    
    return () => {
      isMounted = false
    }
  }, [fetchEvents])

  // Helper function to get event image
  const getEventImage = useCallback((event: Event): string => {
    if (event.image) {
      return event.image
    }
    return '/images/event-image.jpg'
  }, [])

  // Helper function to get event price
  const getEventPrice = useCallback((event: Event): string => {
    const minPrice = getEventMinPrice(event)
    if (minPrice > 0) {
      return `From $${minPrice}`
    }
    return 'Price not available'
  }, [getEventMinPrice])

  // Helper function to get style color
  const getStyleColor = useCallback((style: string) => {
    switch (style) {
      case 'music': return 'bg-purple-100/60 dark:bg-purple-900/60 text-purple-800 dark:text-purple-200 border-purple-200/50 dark:border-purple-700/50'
      case 'sports': return 'bg-green-100/60 dark:bg-green-900/60 text-green-800 dark:text-green-200 border-green-200/50 dark:border-green-700/50'
      case 'theater': return 'bg-red-100/60 dark:bg-red-900/60 text-red-800 dark:text-red-200 border-red-200/50 dark:border-red-700/50'
      case 'festival': return 'bg-yellow-100/60 dark:bg-yellow-900/60 text-yellow-800 dark:text-yellow-200 border-yellow-200/50 dark:border-yellow-700/50'
      case 'conference': return 'bg-blue-100/60 dark:bg-blue-900/60 text-blue-800 dark:text-blue-400 border-blue-200/50 dark:border-blue-700/50'
      case 'exhibition': return 'bg-pink-100/60 dark:bg-pink-900/60 text-pink-800 dark:text-pink-200 border-pink-200/50 dark:border-pink-700/50'
      default: return 'bg-gray-100/60 dark:bg-gray-900/60 text-gray-800 dark:text-gray-200 border-gray-200/50 dark:border-gray-700/50'
    }
  }, [])

  // Helper function to get style icon
  const getStyleIcon = useCallback((style: string) => {
    switch (style) {
      case 'music': return <FaStar className="h-3 w-3 mr-1" aria-hidden="true" />
      case 'sports': return <FaFire className="h-3 w-3 mr-1" aria-hidden="true" />
      case 'theater': return <FaStar className="h-3 w-3 mr-1" aria-hidden="true" />
      case 'festival': return <FaStar className="h-3 w-3 mr-1" aria-hidden="true" />
      case 'conference': return <FaStar className="h-3 w-3 mr-1" aria-hidden="true" />
      case 'exhibition': return <FaStar className="h-3 w-3 mr-1" aria-hidden="true" />
      default: return <FaStar className="h-3 w-3 mr-1" aria-hidden="true" />
    }
  }, [])

  // Helper function to render stars
  const renderStars = useCallback((rating: number = 0) => (
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

  // Calculate total slides
  const totalSlides = Math.ceil(upcomingEvents.length / itemsPerSlide)

  // Don't render the section if there are no events and not loading
  if (!isLoading && !error && events.length === 0) {
    return null;
  }

  return (
    <section className="relative py-12 sm:py-16 lg:py-20 overflow-hidden">
      {/* Background - Modern gradient matching hero */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50/80 via-white to-secondary-50/80 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900" />

      {/* Floating particles effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(12)].map((_, i) => {
          // Deterministic positions for SSR consistency
          const positions = [
            { left: 73.92, top: 59.65 },
            { left: 5.90, top: 8.12 },
            { left: 29.90, top: 94.17 },
            { left: 40.10, top: 93.27 },
            { left: 93.04, top: 26.40 },
            { left: 73.23, top: 29.79 },
            { left: 8.84, top: 32.97 },
            { left: 14.46, top: 72.46 },
            { left: 19.31, top: 91.11 },
            { left: 56.20, top: 10.34 },
            { left: 3.12, top: 11.17 },
            { left: 21.98, top: 88.77 },
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
        {/* Section Header - Modern design */}
        <div className="text-center mb-6 sm:mb-8 lg:mb-10">
          {/* Badge with modern styling */}
          <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-secondary-500/10 to-primary-500/10 backdrop-blur-sm rounded-full border border-secondary-200/50 dark:border-secondary-700/50 mb-4">
            <span className="text-sm uppercase tracking-wider text-secondary-600 dark:text-secondary-400 font-semibold">
              Live Entertainment
            </span>
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            {tHome('specialEventsTitle') || 'Live Events & Entertainment'}
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-3xl mx-auto leading-relaxed">
            {tHome('specialEventsSubtitle') || 'Experience unforgettable moments with world-class events and performances tailored to your preferences.'}
          </p>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-72 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : error ? (
          <div className="text-center text-red-600 dark:text-red-400">{error}</div>
        ) : (
          <div className="space-y-12">
            {/* Special banner card */}
            {specialEvent && (
              <Link href={`/events/${specialEvent.slug}`} className="block group">
                <article className="group relative bg-white/20 dark:bg-gray-800/20 backdrop-blur-md rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-700 overflow-hidden border border-white/30 dark:border-gray-700/30 hover:scale-105 hover:shadow-secondary-500/25 cursor-pointer">
                  {/* Shimmer Effect */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out z-10" />
                  
                  {/* Image Container */}
                  <div className="relative w-full h-64 sm:h-80 md:h-96 overflow-hidden">
                    <OptimizedImage
                      src={specialEvent.image || '/images/event-hero.jpg'}
                      alt={specialEvent.title}
                      fill
                      className="object-cover transition-all duration-700 group-hover:scale-110 group-hover:rotate-1"
                      priority
                      sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 100vw, 100vw"
                      fallbackSrc="/images/event-image.jpg"
                    />
                    
                    {/* Overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500" />
                    
                    {/* Top Badges */}
                    <div className="absolute top-4 left-4 z-20 flex flex-col space-y-2">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-secondary-400 to-primary-500 text-white shadow-lg border border-secondary-300/50 animate-fade-in-down backdrop-blur-sm">
                        ⭐ SPECIAL
                      </span>
                      {specialEvent.style && (
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStyleColor(specialEvent.style)} animate-fade-in-down backdrop-blur-sm`}>
                          {getStyleIcon(specialEvent.style)} {specialEvent.style}
                        </span>
                      )}
                    </div>

                    {/* Venue Badge */}
                    {specialEvent.venue && (
                      <div className="absolute top-4 right-4 z-20">
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white/20 backdrop-blur-xl text-white shadow-lg border border-white/30 animate-fade-in-down">
                          <FaMapPin className="h-3 w-3 mr-1" aria-hidden="true" />
                          {specialEvent.venue.name || 'Venue'}
                        </span>
                      </div>
                    )}

                    {/* Bottom Content */}
                    <div className="absolute bottom-6 left-6 right-6 text-white z-20">
                      <h3 className="text-2xl sm:text-3xl md:text-4xl font-extrabold mb-3 line-clamp-2 drop-shadow-lg">
                        {specialEvent.title}
                      </h3>
                      
                      {/* Event Details */}
                      <div className="flex flex-wrap items-center gap-4 text-sm sm:text-base mb-4">
                        {(() => {
                          const nd = getNextPerformanceDetails(specialEvent)
                          return nd ? (
                            <div className="flex items-center gap-2">
                              <span className="inline-flex items-center px-3 py-1 rounded-lg bg-white/20 backdrop-blur-xl border border-white/30">
                                📅 {formatDate(nd.date)} {nd.start_time ? `• ${formatTime(nd.start_time)}` : ''}
                              </span>
                            </div>
                          ) : null
                        })()}
                        
                                                 {/* Price */}
                         <div className="inline-flex items-center px-3 py-1 rounded-lg bg-white/20 backdrop-blur-xl border border-white/30 text-white font-bold">
                           💰 {formatPrice(getEventMinPrice(specialEvent), 'USD')} 
                           <span className="ml-2 text-sm font-medium opacity-80">{tEvents('fromPrice')}</span>
                         </div>
                      </div>

                      {/* Capacity Info */}
                      {specialEvent.capacity_overview && specialEvent.capacity_overview.total_capacity > 0 && (
                        <div className="space-y-2">
                          <div className="text-sm text-white/90">
                            🎫 {specialEvent.capacity_overview.available_capacity > 0 ? 
                              `${tEvents('available') || 'Available'}: ${specialEvent.capacity_overview.available_capacity} / ${specialEvent.capacity_overview.total_capacity}` : 
                              `${tEvents('soldOut') || 'Sold Out'}: 0 / ${specialEvent.capacity_overview.total_capacity}`
                            }
                          </div>
                          <div className="w-full bg-white/20 rounded-full h-2 backdrop-blur-sm">
                            <div
                              className={`h-2 rounded-full transition-all duration-300 ${
                                specialEvent.capacity_overview.available_capacity > 0 ? 'bg-gradient-to-r from-secondary-400 to-primary-500' : 'bg-gradient-to-r from-red-400 to-red-600'
                              }`}
                              style={{ 
                                width: `${Math.max(0, Math.min(100, (specialEvent.capacity_overview.available_capacity / specialEvent.capacity_overview.total_capacity) * 100))}%` 
                              }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </article>
              </Link>
            )}

            {/* Upcoming events slider */}
            <div className="order-3">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{tEvents('upcomingEvents')}</h3>
                <Link href="/events" className="text-secondary-600 hover:text-primary-600 dark:text-secondary-400 dark:hover:text-primary-400 font-medium transition-colors duration-300">
                  {tHome('viewAllEvents') || 'View All Events'}
                </Link>
              </div>
              {upcomingEvents.length === 0 ? (
                <div className="text-gray-500 dark:text-gray-400 text-sm">{tEvents('noEventsFound') || 'No upcoming events'}</div>
              ) : (
                <div className="relative">
                  {/* Slider Container */}
                  <div
                    ref={sliderRef}
                    className="flex gap-8 transition-transform duration-500 ease-in-out relative"
                    style={{
                      transform: `translateX(-${currentSlide * (100 / itemsPerSlide)}%)`
                    }}
                  >
                    {upcomingEvents.map((ev) => (
                      <div key={`upcoming-${ev.id}`} className="flex-shrink-0 w-full" style={{ width: `calc(100% / ${itemsPerSlide})` }}>
                        <Link 
                          href={`/events/${ev.slug}`}
                          className="block group"
                          aria-label={`View details for ${ev.title}`}
                        >
                          <article
                            className="group relative bg-white/20 dark:bg-gray-800/20 backdrop-blur-md rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-700 overflow-hidden border border-white/30 dark:border-gray-700/30 hover:scale-105 hover:shadow-secondary-500/25 cursor-pointer"
                            onTouchStart={() => handleTouchStart(ev.id)}
                            onTouchEnd={() => handleTouchEnd()}
                          >
                            {/* Shimmer Effect */}
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out z-10" />
                            
                            {/* Image Container */}
                            <div className="relative h-64 overflow-hidden">
                              <OptimizedImage
                                src={getEventImage(ev)}
                                alt={ev.title || 'Event'}
                                fill
                                className="object-cover transition-all duration-700 group-hover:scale-110 group-hover:rotate-1"
                                priority={false}
                                sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                                fallbackSrc="/images/event-image.jpg"
                              />
                              
                              {/* Overlay */}
                              <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500" />
                              
                              {/* Top Badges */}
                              <div className="absolute top-4 left-4 z-20 flex flex-col space-y-2">
                                <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStyleColor(ev.style || 'music')} animate-fade-in-down`}>
                                  {getStyleIcon(ev.style || 'music')}
                                  <span className="ml-1">{ev.style || 'Event'}</span>
                                </span>
                                
                                {ev.venue && (
                                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30 animate-fade-in-down">
                                    <FaMapPin className="h-3 w-3 mr-1" aria-hidden="true" />
                                    {ev.venue.name}
                                  </span>
                                )}
                              </div>

                              {/* Bottom Badges */}
                              <div className="absolute bottom-4 z-20 flex items-center justify-between w-full px-4">
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30 animate-fade-in-down max-w-[200px] truncate">
                                  {ev.title}
                                </span>
                                
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30">
                                  {getEventPrice(ev)}
                                </span>
                              </div>
                            </div>

                            {/* Card Content */}
                            <div className="px-6 pb-6 relative z-10">
                              <div className="border-t border-white/20 dark:border-gray-700/20 pt-4">
                                <div className="space-y-3">
                                  <div className="flex items-center justify-between">
                                    <div className="text-sm text-gray-600 dark:text-gray-400">
                                      <div className="font-medium group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300">
                                        {ev.performance_calendar && ev.performance_calendar.length > 0 ? (
                                          <span className="flex items-center gap-2">
                                            <FaCalendar className="h-4 w-4" />
                                            {formatDate(ev.performance_calendar[0].date)}
                                          </span>
                                        ) : (
                                          <span className="flex items-center gap-2">
                                            <FaCalendar className="h-4 w-4" />
                                            Date not specified
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                    
                                    {/* Rating */}
                                    <div className="flex items-center">
                                      {renderStars(ev.average_rating || 0)}
                                      <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                                        {ev.average_rating ? ev.average_rating.toFixed(1) : '0.0'}
                                      </span>
                                    </div>
                                  </div>
                                  
                                  {/* Event Details */}
                                  <div className="text-xs text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors duration-300">
                                    {ev.venue && (
                                      <div className="flex items-center gap-2 mb-2">
                                        <FaMapPin className="h-3 w-3" />
                                        <span>{ev.venue.name}</span>
                                      </div>
                                    )}
                                    {ev.performance_calendar && ev.performance_calendar.length > 0 && (
                                      <div className="flex items-center gap-2">
                                        <FaCalendar className="h-3 w-3" />
                                        <span>{new Date(ev.performance_calendar[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                                      </div>
                                    )}
                                    {ev.venue && ev.venue.total_capacity && (
                                      <div className="flex items-center gap-2">
                                        <FaUsers className="h-3 w-3" />
                                        <span>{ev.venue.total_capacity} capacity</span>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                            
                            {/* Capacity Information - Grid View (Hidden by default, shown on hover) */}
                            {ev.capacity_overview && ev.capacity_overview.total_capacity > 0 ? (
                              <div className={`opacity-0 group-hover:opacity-100 transition-all duration-300 space-y-3 mt-3 px-6 pb-6 ${isCapacityVisible(ev.id) ? 'opacity-100' : ''}`}>
                                <div className="text-xs text-gray-500 dark:text-gray-400">
                                  {ev.capacity_overview.available_capacity > 0 ? 
                                    `Available: ${ev.capacity_overview.available_capacity} / ${ev.capacity_overview.total_capacity}` : 
                                    `Sold Out: 0 / ${ev.capacity_overview.total_capacity}`
                                  }
                                </div>
                                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2" role="progressbar" aria-valuenow={ev.capacity_overview.available_capacity} aria-valuemin={0} aria-valuemax={ev.capacity_overview.total_capacity}>
                                  <div
                                    className={`h-2 rounded-full transition-all duration-300 ${
                                      ev.capacity_overview.available_capacity > 0 ? 'bg-gradient-to-r from-secondary-500 to-primary-500' : 'bg-red-500'
                                    }`}
                                    style={{ 
                                      width: `${Math.max(0, Math.min(100, (ev.capacity_overview.available_capacity / ev.capacity_overview.total_capacity) * 100))}%` 
                                    }}
                                  />
                                </div>
                              </div>
                            ) : ev.venue && ev.venue.total_capacity ? (
                              <div className={`opacity-0 group-hover:opacity-100 transition-all duration-300 space-y-3 mt-3 px-6 pb-6 ${isCapacityVisible(ev.id) ? 'opacity-100' : ''}`}>
                                <div className="text-xs text-gray-500 dark:text-gray-400">
                                  Venue Capacity: {ev.venue.total_capacity}
                                </div>
                                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2" role="progressbar" aria-valuenow={ev.venue.total_capacity} aria-valuemin={0} aria-valuemax={ev.venue.total_capacity}>
                                  <div 
                                    className="h-2 rounded-full transition-all duration-300 bg-blue-500"
                                    style={{ 
                                      width: '100%'
                                    }}
                                  />
                                </div>
                              </div>
                            ) : null}
                          </article>
                        </Link>
                      </div>
                    ))}
                  </div>

                  {/* Mobile Navigation */}
                  {totalSlides > 1 && (
                    <div className="flex sm:hidden justify-center gap-4 mt-6">
                      <button
                        onClick={prevSlide}
                        disabled={totalSlides <= 1}
                        className="w-12 h-12 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg flex items-center justify-center text-2xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-secondary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed"
                        aria-label={isRTL ? "Next slide" : "Previous slide"}
                      >
                        {isRTL ? <FaChevronRight /> : <FaChevronLeft />}
                      </button>
                      <button
                        onClick={nextSlide}
                        disabled={totalSlides <= 1}
                        className="w-12 h-12 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg flex items-center justify-center text-2xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-secondary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed"
                        aria-label={isRTL ? "Previous slide" : "Next slide"}
                      >
                        {isRTL ? <FaChevronLeft /> : <FaChevronRight />}
                      </button>
                    </div>
                  )}

                  {/* Slide Indicators */}
                  {totalSlides > 1 && (
                    <div className="flex justify-center mt-6 gap-2" role="tablist" aria-label="Slide navigation">
                      {Array.from({ length: totalSlides }).map((_, index) => (
                        <button
                          key={index}
                          onClick={() => scrollToSlide(index)}
                          disabled={false}
                          role="tab"
                          aria-selected={currentSlide === index}
                          aria-label={`Go to slide ${index + 1}`}
                          className={`w-3 h-3 rounded-full transition-all duration-300 hover:scale-125 focus:outline-none focus:ring-2 focus:ring-secondary-400 ${
                            currentSlide === index
                              ? 'bg-gradient-to-r from-secondary-500 to-primary-500 scale-125 shadow-lg shadow-secondary-500/50'
                              : 'bg-gray-300/50 hover:bg-gray-400/50 backdrop-blur-sm'
                          }`}
                        />
                      ))}
                    </div>
                  )}

                  {/* Desktop Navigation */}
                  {totalSlides > 1 && (
                    <>
                      <button
                        onClick={prevSlide}
                        disabled={totalSlides <= 1}
                        className={`hidden sm:flex absolute top-1/2 -translate-y-1/2 z-20 w-16 h-16 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg items-center justify-center text-3xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-secondary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed ${
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
                        disabled={totalSlides <= 1}
                        className={`hidden sm:flex absolute top-1/2 -translate-y-1/2 z-20 w-16 h-16 bg-white/20 dark:bg-gray-700/20 backdrop-blur-md hover:bg-white/30 dark:hover:bg-gray-700/30 text-white rounded-full shadow-lg items-center justify-center text-3xl border-2 border-white/30 dark:border-gray-600/30 transition-all duration-300 hover:scale-110 active:scale-95 hover:shadow-secondary-500/25 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed ${
                          isRTL 
                            ? 'left-0 -translate-x-3' 
                            : 'right-0 translate-x-3'
                        }`}
                        aria-label={isRTL ? "Previous slide" : "Next slide"}
                      >
                        {isRTL ? <FaChevronLeft /> : <FaChevronRight />}
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Featured Events Section */}
            {featuredEvents.length > 0 && (
              <div className="order-0 mb-12">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <FaStar className="text-yellow-500" />
                    {tEvents('featuredEvents') || 'Featured Events'}
                  </h3>
                  <Link href="/events?type=featured" className="text-secondary-600 hover:text-primary-600 dark:text-secondary-400 dark:hover:text-primary-400 font-medium transition-colors duration-300">
                    {tHome('viewAll') || 'View All'}
                  </Link>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {featuredEvents.slice(0, 4).map((ev) => (
                    <div key={`featured-${ev.id}`} className="group">
                      <Link 
                        href={`/events/${ev.slug}`}
                        className="block"
                        aria-label={`View details for ${ev.title}`}
                      >
                        <article className="group relative bg-white/20 dark:bg-gray-800/20 backdrop-blur-md rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-700 overflow-hidden border border-white/30 dark:border-gray-700/30 hover:scale-105 hover:shadow-secondary-500/25 cursor-pointer">
                          {/* Shimmer Effect */}
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out z-10" />
                          
                          {/* Image Container */}
                          <div className="relative h-48 overflow-hidden">
                            <OptimizedImage
                              src={getEventImage(ev)}
                              alt={ev.title || 'Event'}
                              fill
                              className="object-cover transition-all duration-700 group-hover:scale-110 group-hover:rotate-1"
                              priority={false}
                              sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 25vw, 20vw"
                              fallbackSrc="/images/event-image.jpg"
                            />
                            
                            {/* Featured Badge */}
                            <div className="absolute top-3 left-3 z-20">
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-yellow-400 to-orange-500 text-white shadow-lg border border-yellow-300/50">
                                ⭐ FEATURED
                              </span>
                            </div>
                          </div>

                          {/* Card Content */}
                          <div className="p-4">
                            <h4 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2 group-hover:text-secondary-600 dark:group-hover:text-secondary-400 transition-colors duration-300">
                              {ev.title}
                            </h4>
                            <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                              <span>{getEventPrice(ev)}</span>
                              {ev.average_rating && (
                                <div className="flex items-center">
                                  {renderStars(ev.average_rating)}
                                </div>
                              )}
                            </div>
                          </div>
                        </article>
                      </Link>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Popular Events Section */}
            {popularEvents.length > 0 && (
              <div className="order-1 mb-12">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <FaFire className="text-red-500" />
                    {tEvents('popularEvents') || 'Popular Events'}
                  </h3>
                  <Link href="/events?type=popular" className="text-secondary-600 hover:text-primary-600 dark:text-secondary-400 dark:hover:text-primary-400 font-medium transition-colors duration-300">
                    {tHome('viewAll') || 'View All'}
                  </Link>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {popularEvents.slice(0, 3).map((ev) => (
                    <div key={`popular-${ev.id}`} className="group">
                      <Link 
                        href={`/events/${ev.slug}`}
                        className="block"
                        aria-label={`View details for ${ev.title}`}
                      >
                        <article className="group relative bg-white/20 dark:bg-gray-800/20 backdrop-blur-md rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-700 overflow-hidden border border-white/30 dark:border-gray-700/30 hover:scale-105 hover:shadow-secondary-500/25 cursor-pointer">
                          {/* Shimmer Effect */}
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out z-10" />
                          
                          {/* Image Container */}
                          <div className="relative h-56 overflow-hidden">
                            <OptimizedImage
                              src={getEventImage(ev)}
                              alt={ev.title || 'Event'}
                              fill
                              className="object-cover transition-all duration-700 group-hover:scale-110 group-hover:rotate-1"
                              priority={false}
                              sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                              fallbackSrc="/images/event-image.jpg"
                            />
                            
                            {/* Popular Badge */}
                            <div className="absolute top-3 left-3 z-20">
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-red-400 to-pink-500 text-white shadow-lg border border-red-300/50">
                                🔥 POPULAR
                              </span>
                            </div>
                          </div>

                          {/* Card Content */}
                          <div className="p-4">
                            <h4 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2 group-hover:text-secondary-600 dark:group-hover:text-secondary-400 transition-colors duration-300">
                              {ev.title}
                            </h4>
                            <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                              <span>{getEventPrice(ev)}</span>
                              {ev.average_rating && (
                                <div className="flex items-center">
                                  {renderStars(ev.average_rating)}
                                </div>
                              )}
                            </div>
                          </div>
                        </article>
                      </Link>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Past events grid (grayscale) - moved above Upcoming position visually by ordering */}
            <div className="order-2">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{tEvents('pastEvents')}</h3>
                <Link href="/events?type=past" className="text-secondary-600 hover:text-primary-600 dark:text-secondary-400 dark:hover:text-primary-400 font-medium transition-colors duration-300">
                  {tHome('viewAll') || 'View All'}
                </Link>
              </div>
              {pastEvents.length === 0 ? (
                <div className="text-gray-500 dark:text-gray-400 text-sm">{tEvents('noEventsFound') || 'No past events'}</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {pastEvents.slice(0, 6).map((ev) => (
                    <div key={`past-${ev.id}`} className="filter grayscale hover:grayscale-0 transition-all">
                      <Link 
                        href={`/events/${ev.slug}`}
                        className="block group"
                        aria-label={`View details for ${ev.title}`}
                      >
                        <article
                          className="group relative bg-white/20 dark:bg-gray-800/20 backdrop-blur-md rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-700 overflow-hidden border border-white/30 dark:border-gray-700/30 hover:scale-105 hover:shadow-secondary-500/25 cursor-pointer"
                          onTouchStart={() => handleTouchStart(ev.id)}
                          onTouchEnd={() => handleTouchEnd()}
                        >
                          {/* Shimmer Effect */}
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out z-10" />
                          
                          {/* Image Container */}
                          <div className="relative h-64 overflow-hidden">
                            <OptimizedImage
                              src={getEventImage(ev)}
                              alt={ev.title || 'Event'}
                              fill
                              className="object-cover transition-all duration-700 group-hover:scale-110 group-hover:rotate-1"
                              priority={false}
                              sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
                              fallbackSrc="/images/event-image.jpg"
                            />
                            
                            {/* Overlay */}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-500" />
                            
                            {/* Top Badges */}
                            <div className="absolute top-4 left-4 z-20 flex flex-col space-y-2">
                              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStyleColor(ev.style || 'music')} animate-fade-in-down`}>
                                {getStyleIcon(ev.style || 'music')}
                                <span className="ml-1">{ev.style || 'Event'}</span>
                              </span>
                              
                              {ev.venue && (
                                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30 animate-fade-in-down">
                                  <FaMapPin className="h-3 w-3 mr-1" aria-hidden="true" />
                                  {ev.venue.name}
                                </span>
                              )}
                            </div>

                            {/* Bottom Badges */}
                            <div className="absolute bottom-4 z-20 flex items-center justify-between w-full px-4">
                              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30 animate-fade-in-down max-w-[200px] truncate">
                                {ev.title}
                              </span>
                              
                              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white/15 backdrop-blur-xl text-white shadow-lg border border-white/30">
                                {getEventPrice(ev)}
                              </span>
                            </div>
                          </div>

                          {/* Card Content */}
                          <div className="px-6 pb-6 relative z-10">
                            <div className="border-t border-white/20 dark:border-gray-700/20 pt-4">
                              <div className="space-y-3">
                                <div className="flex items-center justify-between">
                                  <div className="text-sm text-gray-600 dark:text-gray-400">
                                    <div className="font-medium group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300">
                                      {ev.performance_calendar && ev.performance_calendar.length > 0 ? (
                                        <span className="flex items-center gap-2">
                                          <FaCalendar className="h-4 w-4" />
                                          {formatDate(ev.performance_calendar[0].date)}
                                        </span>
                                      ) : (
                                        <span className="flex items-center gap-2">
                                          <FaCalendar className="h-4 w-4" />
                                          Date not specified
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                  
                                  {/* Rating */}
                                  <div className="flex items-center">
                                    {renderStars(ev.average_rating || 0)}
                                    <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                                      {ev.average_rating ? ev.average_rating.toFixed(1) : '0.0'}
                                    </span>
                                  </div>
                                </div>
                                
                                {/* Event Details */}
                                <div className="text-xs text-gray-500 dark:text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors duration-300">
                                  {ev.venue && (
                                    <div className="flex items-center gap-2 mb-2">
                                      <FaMapPin className="h-3 w-3" />
                                      <span>{ev.venue.name}</span>
                                    </div>
                                  )}
                                  {ev.performance_calendar && ev.performance_calendar.length > 0 && (
                                    <div className="flex items-center gap-2">
                                      <FaCalendar className="h-3 w-3" />
                                      <span>{new Date(ev.performance_calendar[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                                    </div>
                                  )}
                                  {ev.venue && ev.venue.total_capacity && (
                                    <div className="flex items-center gap-2">
                                      <FaUsers className="h-3 w-3" />
                                      <span>{ev.venue.total_capacity} capacity</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          {/* Capacity Information - Grid View (Hidden by default, shown on hover) */}
                          {ev.capacity_overview && ev.capacity_overview.total_capacity > 0 ? (
                            <div className={`opacity-0 group-hover:opacity-100 transition-all duration-300 space-y-3 mt-3 px-6 pb-6 ${isCapacityVisible(ev.id) ? 'opacity-100' : ''}`}>
                              <div className="text-xs text-gray-500 dark:text-gray-400">
                                {ev.capacity_overview.available_capacity > 0 ? 
                                  `Available: ${ev.capacity_overview.available_capacity} / ${ev.capacity_overview.total_capacity}` : 
                                  `Sold Out: 0 / ${ev.capacity_overview.total_capacity}`
                                }
                              </div>
                              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2" role="progressbar" aria-valuenow={ev.capacity_overview.available_capacity} aria-valuemin={0} aria-valuemax={ev.capacity_overview.total_capacity}>
                                <div 
                                  className={`h-2 rounded-full transition-all duration-300 ${
                                    ev.capacity_overview.available_capacity > 0 ? 'bg-green-500' : 'bg-red-500'
                                  }`}
                                  style={{ 
                                    width: `${Math.max(0, Math.min(100, (ev.capacity_overview.available_capacity / ev.capacity_overview.total_capacity) * 100))}%` 
                                  }}
                                />
                              </div>
                            </div>
                          ) : ev.venue && ev.venue.total_capacity ? (
                            <div className={`opacity-0 group-hover:opacity-100 transition-all duration-300 space-y-3 mt-3 px-6 pb-6 ${isCapacityVisible(ev.id) ? 'opacity-100' : ''}`}>
                              <div className="text-xs text-gray-500 dark:text-gray-400">
                                Venue Capacity: {ev.venue.total_capacity}
                              </div>
                              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2" role="progressbar" aria-valuenow={ev.venue.total_capacity} aria-valuemin={0} aria-valuemax={ev.venue.total_capacity}>
                                <div
                                  className="h-2 rounded-full transition-all duration-300 bg-gradient-to-r from-secondary-500 to-primary-500"
                                  style={{ 
                                    width: '100%'
                                  }}
                                />
                              </div>
                            </div>
                          ) : null}
                        </article>
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

                          <div className="mt-8 text-center">
                            <Button
                              variant="default"
                              size="lg"
                              onClick={() => router.push('/events')}
                              className="bg-gradient-to-r from-secondary-500 to-primary-500 hover:from-secondary-600 hover:to-primary-600 text-white px-8 py-4 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300"
                            >
                              <FaStar className="w-5 h-5 mr-2" />
                              {tHome('viewAllEvents') || 'Explore All Events'}
                            </Button>
                          </div>
      </div>
    </section>
  )
}
