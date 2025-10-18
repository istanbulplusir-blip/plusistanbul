'use client';

import { useState, useEffect, useCallback } from 'react';

import { motion, AnimatePresence } from 'framer-motion';
import { getEvents, getEventFilters } from '@/lib/api/events';
import { Event, EventCategory, Venue } from '@/lib/types/api';
import { useLocale } from 'next-intl';
import { 
  Search, 
  Filter, 
  Grid,
  List,
  X
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import ProductCard from '@/components/common/ProductCard';

interface EventFilters {
  search: string;
  category: string;
  venue: string;
  style: string;
  min_price: number;
  max_price: number;
  date_from: string;
  date_to: string;
  sort_by: string;
}



export default function EventsPage() {
  const currentLang = useLocale();
  const [events, setEvents] = useState<Event[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [filterOptions, setFilterOptions] = useState({
    categories: [] as EventCategory[],
    venues: [] as Venue[],
    styles: [] as string[]
  });

  const [filters, setFilters] = useState<EventFilters>({
    search: '',
    category: '',
    venue: '',
    style: '',
    min_price: 0,
    max_price: 5000,
    date_from: '',
    date_to: '',
    sort_by: 'date'
  });

  // Fetch events
  const fetchEvents = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await getEvents({
        page_size: 50,
        ordering: '-created_at'
      });
      
      if (response && Array.isArray(response.results)) {
        setEvents(response.results);
        setFilteredEvents(response.results);
      } else {
        setEvents([]);
        setFilteredEvents([]);
      }
      setError(null);
    } catch (err) {
      console.error('Error fetching events:', err);
      setError('Failed to load events');
      setEvents([]);
      setFilteredEvents([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch filter options
  const fetchFilterOptions = useCallback(async () => {
    try {
      const response = await getEventFilters();
      if (response) {
        setFilterOptions({
          categories: response.categories || [],
          venues: response.venues || [],
          styles: (response.styles || []).map((style: { value: string } | string) => typeof style === 'string' ? style : style.value)
        });
      }
    } catch (err) {
      console.error('Error fetching filter options:', err);
    }
  }, []);

  useEffect(() => {
    fetchEvents();
    fetchFilterOptions();
  }, [fetchEvents, fetchFilterOptions]);

  // Filter events
  useEffect(() => {
    let filtered = events;

    if (filters.search) {
      filtered = filtered.filter(event => 
        event.title?.toLowerCase().includes(filters.search.toLowerCase()) ||
        event.short_description?.toLowerCase().includes(filters.search.toLowerCase()) ||
        event.venue?.name.toLowerCase().includes(filters.search.toLowerCase())
      );
    }

    if (filters.category) {
      filtered = filtered.filter(event => 
        event.category?.id === filters.category
      );
    }

    if (filters.venue) {
      filtered = filtered.filter(event => 
        event.venue?.id === filters.venue
      );
    }

    if (filters.style) {
      filtered = filtered.filter(event => 
        event.style === filters.style
      );
    }

    if (filters.min_price > 0 || filters.max_price < 5000) {
      filtered = filtered.filter(event => {
        const minPrice = event.min_price || 0;
        return minPrice >= filters.min_price && minPrice <= filters.max_price;
      });
    }

    if (filters.date_from) {
      filtered = filtered.filter(event => {
        if (!event.performances || event.performances.length === 0) return false;
        const eventDate = new Date(event.performances[0].date);
        const fromDate = new Date(filters.date_from);
        return eventDate >= fromDate;
      });
    }

    if (filters.date_to) {
      filtered = filtered.filter(event => {
        if (!event.performances || event.performances.length === 0) return false;
        const eventDate = new Date(event.performances[0].date);
        const toDate = new Date(filters.date_to);
        return eventDate <= toDate;
      });
    }

    // Sort events
    filtered.sort((a, b) => {
      switch (filters.sort_by) {
        case 'date':
          if (!a.performances || !b.performances) return 0;
          return new Date(a.performances[0].date).getTime() - new Date(b.performances[0].date).getTime();
        case 'price':
          return (a.min_price || 0) - (b.min_price || 0);
        case 'name':
          return (a.title || '').localeCompare(b.title || '');
        case 'rating':
          return ((b as Event & { rating?: number; average_rating?: number }).rating || (b as Event & { rating?: number; average_rating?: number }).average_rating || 0) - ((a as Event & { rating?: number; average_rating?: number }).rating || (a as Event & { rating?: number; average_rating?: number }).average_rating || 0);
        default:
          return 0;
      }
    });

    setFilteredEvents(filtered);
  }, [events, filters]);

  const handleFilterChange = (key: keyof EventFilters, value: string | number) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      category: '',
      venue: '',
      style: '',
      min_price: 0,
      max_price: 5000,
      date_from: '',
      date_to: '',
      sort_by: 'date'
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fa-IR', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };



  // Convert Event to ProductCard format
  const convertEventToProduct = (event: Event) => ({
    ...event,
    type: 'event' as const,
    // Ensure required fields for ProductCard
    title: event.title || event.slug,
    description: event.description || event.short_description || '',
    short_description: event.short_description || event.description || '',
    price: (event as Event & { price?: string; currency?: string; image_url?: string; rating?: number; average_rating?: number }).price || '0',
    currency: (event as Event & { price?: string; currency?: string; image_url?: string; rating?: number; average_rating?: number }).currency || 'USD',
    image_url: (event as Event & { price?: string; currency?: string; image_url?: string; rating?: number; average_rating?: number }).image_url || event.image || '/images/event-default.jpg',
    rating: (event as Event & { price?: string; currency?: string; image_url?: string; rating?: number; average_rating?: number }).rating || (event as Event & { price?: string; currency?: string; image_url?: string; rating?: number; average_rating?: number }).average_rating || 0,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="container mx-auto px-4 py-8">
          {/* Header Skeleton */}
          <motion.div 
            className="text-center mb-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <div className="animate-pulse">
              <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-12 md:h-16 rounded-xl mb-4 max-w-md mx-auto"></div>
              <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-6 rounded-lg max-w-2xl mx-auto"></div>
            </div>
          </motion.div>

          {/* Search Bar Skeleton */}
          <motion.div 
            className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-6 mb-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="animate-pulse">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div className="flex-1">
                  <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-12 rounded-xl"></div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-10 w-32 rounded-lg"></div>
                  <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-10 w-32 rounded-lg"></div>
                  <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-10 w-20 rounded-lg"></div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Results Count Skeleton */}
          <motion.div 
            className="mb-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="animate-pulse">
              <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-5 w-32 rounded-lg"></div>
            </div>
          </motion.div>

          {/* Cards Grid Skeleton */}
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            {Array.from({ length: 6 }).map((_, i) => (
              <motion.div 
                key={i} 
                className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 + i * 0.1 }}
              >
                <div className="animate-pulse">
                  {/* Image Skeleton */}
                  <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-48 w-full"></div>
                  
                  {/* Content Skeleton */}
                  <div className="p-6">
                    {/* Title */}
                    <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-6 rounded-lg mb-3"></div>
                    
                    {/* Description */}
                    <div className="space-y-2 mb-4">
                      <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-4 rounded-lg"></div>
                      <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-4 rounded-lg w-3/4"></div>
                    </div>
                    
                    {/* Venue & Date */}
                    <div className="flex items-center gap-4 mb-4">
                      <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-4 w-24 rounded-lg"></div>
                      <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-4 w-20 rounded-lg"></div>
                    </div>
                    
                    {/* Price & Button */}
                    <div className="flex items-center justify-between">
                      <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-6 w-24 rounded-lg"></div>
                      <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-10 w-20 rounded-xl"></div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div 
          className="text-center mb-12"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-4">
            {currentLang === 'fa' ? 'رویدادها و کنسرت‌ها' : 'Events & Concerts'}
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            {currentLang === 'fa' 
              ? 'تجربه‌ای منحصر به فرد با بهترین رویدادها و کنسرت‌ها' 
              : 'Experience unique moments with the best events and concerts'
            }
          </p>
        </motion.div>

        {/* Search and Filter Bar */}
        <motion.div 
          className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-6 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <Input
                  type="text"
                  placeholder={currentLang === 'fa' ? 'جستجو در رویدادها...' : 'Search events...'}
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="pl-10 w-full"
                />
            </div>
            </div>

            <div className="flex items-center gap-4">
                {/* Category Filter */}
                  <select
                    value={filters.category}
                    onChange={(e) => handleFilterChange('category', e.target.value)}
                    className="w-full px-3 py-2 bg-white/50 dark:bg-gray-700/50 border border-white/30 dark:border-gray-600/30 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                  >
                    <option value="">{currentLang === 'fa' ? 'همه دسته‌بندی‌ها' : 'All Categories'}</option>
                    {filterOptions.categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>

                {/* Venue Filter */}
                  <select
                    value={filters.venue}
                    onChange={(e) => handleFilterChange('venue', e.target.value)}
                    className="w-full px-3 py-2 bg-white/50 dark:bg-gray-700/50 border border-white/30 dark:border-gray-600/30 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                  >
                    <option value="">{currentLang === 'fa' ? 'همه محل‌ها' : 'All Venues'}</option>
                    {filterOptions.venues.map((venue) => (
                      <option key={venue.id} value={venue.id}>
                        {venue.name}
                  </option>
                ))}
              </select>

              {/* View Mode Toggle */}
              <div className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                  className="px-3 py-1"
                >
                  <Grid className="w-4 h-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                  className="px-3 py-1"
                >
                  <List className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Advanced Filters */}
          <AnimatePresence mode="wait">
            {showFilters && (
              <motion.div 
                className="mt-6 pt-6 border-t border-gray-200/50 dark:border-gray-700/50 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
              >
                {/* Style Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {currentLang === 'fa' ? 'نوع رویداد' : 'Event Style'}
                  </label>
                  <select
                    value={filters.style}
                    onChange={(e) => handleFilterChange('style', e.target.value)}
                    className="w-full px-3 py-2 bg-white/50 dark:bg-gray-700/50 border border-white/30 dark:border-gray-600/30 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                  >
                    <option value="">{currentLang === 'fa' ? 'همه انواع' : 'All Styles'}</option>
                    {filterOptions.styles.map((style) => (
                      <option key={style} value={style}>
                        {style}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Price Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {currentLang === 'fa' ? 'محدوده قیمت' : 'Price Range'}
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="number"
                      placeholder={currentLang === 'fa' ? 'از' : 'From'}
                      value={filters.min_price}
                      onChange={(e) => handleFilterChange('min_price', Number(e.target.value))}
                      className="flex-1 px-3 py-2 bg-white/50 dark:bg-gray-700/50 border border-white/30 dark:border-gray-600/30 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                    />
                    <input
                      type="number"
                      placeholder={currentLang === 'fa' ? 'تا' : 'To'}
                      value={filters.max_price}
                      onChange={(e) => handleFilterChange('max_price', Number(e.target.value))}
                      className="flex-1 px-3 py-2 bg-white/50 dark:bg-gray-700/50 border border-white/30 dark:border-gray-600/30 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                    />
                  </div>
                </div>

                {/* Date Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {currentLang === 'fa' ? 'محدوده تاریخ' : 'Date Range'}
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="date"
                      value={filters.date_from}
                      onChange={(e) => handleFilterChange('date_from', e.target.value)}
                      className="flex-1 px-3 py-2 bg-white/50 dark:bg-gray-700/50 border border-white/30 dark:border-gray-600/30 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                    />
                    <input
                      type="date"
                      value={filters.date_to}
                      onChange={(e) => handleFilterChange('date_to', e.target.value)}
                      className="flex-1 px-3 py-2 bg-white/50 dark:bg-gray-700/50 border border-white/30 dark:border-gray-600/30 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                    />
                  </div>
                </div>

                {/* Sort By */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {currentLang === 'fa' ? 'مرتب‌سازی' : 'Sort By'}
                  </label>
                  <select
                    value={filters.sort_by}
                    onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                    className="w-full px-3 py-2 bg-white/50 dark:bg-gray-700/50 border border-white/30 dark:border-gray-600/30 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                  >
                    <option value="date">{currentLang === 'fa' ? 'تاریخ' : 'Date'}</option>
                    <option value="price">{currentLang === 'fa' ? 'قیمت' : 'Price'}</option>
                    <option value="name">{currentLang === 'fa' ? 'نام' : 'Name'}</option>
                    <option value="rating">{currentLang === 'fa' ? 'امتیاز' : 'Rating'}</option>
                  </select>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Filter Toggle */}
          <div className="flex items-center justify-between mt-4">
            <Button
              onClick={() => setShowFilters(!showFilters)}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <Filter className="w-4 h-4" />
              {currentLang === 'fa' ? 'فیلترهای پیشرفته' : 'Advanced Filters'}
            </Button>
                  <Button
                    onClick={clearFilters}
                    variant="outline"
                    size="sm"
              className="flex items-center gap-2"
                  >
              <X className="w-4 h-4" />
                    {currentLang === 'fa' ? 'پاک کردن فیلترها' : 'Clear Filters'}
                  </Button>
                </div>
        </motion.div>

        {/* Results Count */}
        <motion.div 
          className="mb-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <p className="text-gray-600 dark:text-gray-300">
            {currentLang === 'fa' 
              ? `${filteredEvents.length} رویداد یافت شد` 
              : `Found ${filteredEvents.length} events`
            }
          </p>
        </motion.div>

        {/* Events Grid/List */}
        {error ? (
          <motion.div 
            className="text-center py-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-red-500 text-lg mb-4">{error}</div>
            <Button onClick={fetchEvents} variant="outline">
              {currentLang === 'fa' ? 'تلاش مجدد' : 'Try Again'}
            </Button>
          </motion.div>
        ) : filteredEvents.length === 0 ? (
          <motion.div 
            className="text-center py-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
            <div className="text-gray-500 text-lg mb-4">
              {currentLang === 'fa' ? 'هیچ رویدادی یافت نشد' : 'No events found'}
          </div>
          </motion.div>
        ) : (
          <AnimatePresence mode="wait">
            {viewMode === 'grid' ? (
              <motion.div 
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                key="grid"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
              >
                {filteredEvents.map((event, index) => (
                  <motion.div
                    key={event.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <ProductCard
                      product={convertEventToProduct(event)}
                      viewMode="grid"
                      formatDate={formatDate}
                    />
                  </motion.div>
                ))}
              </motion.div>
            ) : (
              <motion.div 
                className="space-y-6"
                key="list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
              >
                {filteredEvents.map((event, index) => (
                  <motion.div
                  key={event.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <ProductCard
                      product={convertEventToProduct(event)}
                      viewMode="list"
                      formatDate={formatDate}
                    />
                  </motion.div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
} 