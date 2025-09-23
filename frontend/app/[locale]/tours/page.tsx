'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiClient } from '@/lib/api/client';
import { useLocale } from 'next-intl';
import { 
  Search, 
  Grid, 
  List
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import ProductCard from '@/components/common/ProductCard';
import Head from 'next/head';

interface Tour {
  id: string;
  slug: string;
  title?: string;
  description?: string;
  short_description?: string;
  price: string;
  starting_price?: number | null;
  currency: string;
  duration_hours: number;
  min_participants?: number;
  max_participants?: number;
  is_active: boolean;
  created_at: string;
  image?: string;
  image_url?: string;
  location?: string;
  rating?: number;
  average_rating?: number;
  category?: {
    id: string;
    name: string;
  };
  category_slug?: string;
  category_name?: string;
  next_schedule_date?: string | null;
  next_schedule_capacity_total?: number;
  next_schedule_capacity_available?: number;
  has_upcoming?: boolean;
}

export default function ToursListPage() {
  const currentLang = useLocale();
  const [tours, setTours] = useState<Tour[]>([]);
  const [filteredTours, setFilteredTours] = useState<Tour[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');

 
  // Fetch tours
  const fetchTours = useCallback(async () => {
      try {
        setIsLoading(true);
      const response = await apiClient.get('/tours/', {
        params: {
          page_size: 50,
          ordering: '-created_at'
        }
      });
      

      
      // Handle both paginated and direct array responses
      let toursData = [];
      const responseData = (response as { data: unknown }).data;
      if (responseData && Array.isArray(responseData)) {
        toursData = responseData;
      } else if (responseData && typeof responseData === 'object' && responseData !== null && 'results' in responseData && Array.isArray((responseData as { results: unknown }).results)) {
        toursData = (responseData as { results: unknown[] }).results;
      }
      
      setTours(toursData);
      setFilteredTours(toursData);
      setError(null);
    } catch (err) {
      console.error('Error fetching tours:', err);
      setError('Failed to load tours');
      setTours([]);
      setFilteredTours([]);
      } finally {
        setIsLoading(false);
      }
  }, []);

  useEffect(() => {
    fetchTours();
  }, [fetchTours]);

  // Filter tours
  useEffect(() => {
    let filtered = tours;

    if (searchTerm) {
      filtered = filtered.filter(tour => 
        tour.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tour.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tour.location?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedCategory) {
      filtered = filtered.filter(tour => 
        tour.category?.id === selectedCategory ||
        tour.category_slug === selectedCategory
      );
    }

    setFilteredTours(filtered);
  }, [tours, searchTerm, selectedCategory]);

  // Get unique categories
  const categories = useMemo(() => {
    const categoryMap = new Map();
    tours.forEach(tour => {
      if (tour.category) {
        categoryMap.set(tour.category.id, tour.category);
      } else if (tour.category_slug && tour.category_name) {
        categoryMap.set(tour.category_slug, {
          id: tour.category_slug,
          name: tour.category_name
        });
      }
    });
    return Array.from(categoryMap.values());
  }, [tours]);



  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('fa-IR', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };



  // Convert Tour to ProductCard format
  const convertTourToProduct = (tour: Tour) => ({
    ...tour,
    type: 'tour' as const,
    // Ensure required fields for ProductCard
    title: tour.title || tour.slug,
    description: tour.description || tour.short_description || '',
    short_description: tour.short_description || tour.description || '',
    price: tour.price,
    currency: tour.currency,
    image_url: tour.image_url || tour.image || '/images/tour-default.jpg',
    location: tour.location || 'Location not specified',
    rating: tour.rating || tour.average_rating || 0,
    category: tour.category || (tour.category_slug && tour.category_name ? {
      id: tour.category_slug,
      name: tour.category_name
    } : undefined),
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
                    
                    {/* Location & Duration */}
                    <div className="flex items-center gap-4 mb-4">
                      <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-4 w-20 rounded-lg"></div>
                      <div className="bg-gradient-to-r from-primary-200/50 to-secondary-200/50 dark:from-primary-800/50 dark:to-secondary-800/50 h-4 w-16 rounded-lg"></div>
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
    <>
      <Head>
        <title>{currentLang === 'fa' ? 'تورها' : 'Tours'} - Peykan Tourism</title>
        <meta name="description" content={currentLang === 'fa' ? 'تورهای تفریحی و گردشگری' : 'Tourism and travel tours'} />
      </Head>

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
              {currentLang === 'fa' ? 'تورهای تفریحی' : 'Adventure Tours'}
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              {currentLang === 'fa' 
                ? 'تجربه‌ای منحصر به فرد با بهترین تورهای گردشگری و ماجراجویی' 
                : 'Experience unique adventures with the best tourism and adventure tours'
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
                  placeholder={currentLang === 'fa' ? 'جستجو در تورها...' : 'Search tours...'}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-full"
                  />
                </div>
          </div>

              <div className="flex items-center gap-4">
                {/* Category Filter */}
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-4 py-2 bg-white/50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white"
                  >
                      <option value="">{currentLang === 'fa' ? 'همه دسته‌بندی‌ها' : 'All Categories'}</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                        {category.name}
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
                ? `${filteredTours.length} تور یافت شد` 
                : `Found ${filteredTours.length} tours`
              }
            </p>
          </motion.div>

          {/* Tours Grid/List */}
        {error ? (
          <motion.div 
            className="text-center py-12"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
          >
              <div className="text-red-500 text-lg mb-4">{error}</div>
              <Button onClick={fetchTours} variant="outline">
                {currentLang === 'fa' ? 'تلاش مجدد' : 'Try Again'}
              </Button>
            </motion.div>
          ) : filteredTours.length === 0 ? (
            <motion.div 
              className="text-center py-12"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              <div className="text-gray-500 text-lg mb-4">
                {currentLang === 'fa' ? 'هیچ توری یافت نشد' : 'No tours found'}
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
                  {filteredTours.map((tour, index) => (
                    <motion.div
                      key={tour.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                    >
                      <ProductCard
                        product={convertTourToProduct(tour)}
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
                  {filteredTours.map((tour, index) => (
                    <motion.div
                      key={tour.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                    >
                      <ProductCard
                        product={convertTourToProduct(tour)}
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
    </>
  );
} 