'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLocale } from 'next-intl';
import { 
  Search, 
  Grid, 
  List
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import CarRentalCard from '@/components/car-rentals/CarRentalCard';
import CarRentalFilters from '@/components/car-rentals/CarRentalFilters';
import { useCarRentals, useCarRentalSearch } from '@/lib/hooks/useCarRentals';
import { CarRentalSearchParams } from '@/lib/api/car-rentals';
import Head from 'next/head';

export default function CarRentalsPage() {
  const currentLang = useLocale();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'price_asc' | 'price_desc' | 'year_desc' | 'name_asc' | 'name_desc' | 'created_at_desc'>('created_at_desc');
  const [filters, setFilters] = useState<CarRentalSearchParams>({});
  const [isSearching, setIsSearching] = useState(false);

  // Use search hook when filters are applied, otherwise use regular list hook
  const hasFilters = Object.values(filters).some(value => 
    value !== undefined && value !== null && value !== ''
  ) || searchTerm.trim() !== '';

  const searchParams = useMemo(() => ({
    ...filters,
    query: searchTerm.trim() || undefined,
    sort_by: sortBy
  }), [filters, searchTerm, sortBy]);

  const { 
    data: searchData, 
    error: searchError, 
    isLoading: isSearchLoading 
  } = useCarRentalSearch(hasFilters ? searchParams : { sort_by: sortBy });

  const { 
    data: listData, 
    error: listError, 
    isLoading: isListLoading 
  } = useCarRentals(hasFilters ? undefined : { ordering: sortBy, page_size: 50 });

  const data = hasFilters ? searchData : listData;
  const error = hasFilters ? searchError : listError;
  const isLoading = hasFilters ? isSearchLoading : isListLoading;

  const carRentals = data?.results || [];
  const totalCount = data?.count || 0;

  const handleFiltersChange = useCallback((newFilters: CarRentalSearchParams) => {
    setFilters(newFilters);
  }, []);

  const handleSearch = useCallback(() => {
    setIsSearching(true);
    // The search will be triggered automatically by the hook
    setTimeout(() => setIsSearching(false), 1000);
  }, []);

  const handleSortChange = useCallback((newSortBy: typeof sortBy) => {
    setSortBy(newSortBy);
  }, []);

  const formatPrice = useCallback((price: number, currency: string) => {
    return new Intl.NumberFormat(currentLang === 'fa' ? 'fa-IR' : 'en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  }, [currentLang]);

  const sortOptions = [
    { value: 'created_at_desc', label: 'Newest First' },
    { value: 'price_asc', label: 'Price: Low to High' },
    { value: 'price_desc', label: 'Price: High to Low' },
    { value: 'year_desc', label: 'Newest Cars' },
    { value: 'name_asc', label: 'Name: A to Z' },
    { value: 'name_desc', label: 'Name: Z to A' },
  ];

  return (
    <>
      <Head>
        <title>Car Rentals - Peykan Tourism</title>
        <meta name="description" content="Find the perfect car rental for your trip. Choose from economy, luxury, SUV, and convertible cars." />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {/* Header Section */}
        <div className="bg-white dark:bg-gray-800 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                Car Rentals
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
                Find the perfect car for your journey
              </p>
              
              {/* Search Bar */}
              <div className="max-w-2xl mx-auto">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <Input
                    type="text"
                    placeholder="Search by brand, model, or location..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 pr-4 py-3 text-lg"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col xl:flex-row gap-8">
            {/* Filters Sidebar - Hidden on mobile, visible on desktop */}
            <div className="hidden xl:block xl:w-80 flex-shrink-0">
              <div className="sticky top-8">
                <CarRentalFilters
                  filters={filters}
                  onFiltersChange={handleFiltersChange}
                  onSearch={handleSearch}
                  isLoading={isSearching}
                />
              </div>
            </div>

            {/* Main Content */}
            <div className="flex-1">
              {/* Mobile Filters - Show on mobile and tablet */}
              <div className="xl:hidden mb-6">
                <CarRentalFilters
                  filters={filters}
                  onFiltersChange={handleFiltersChange}
                  onSearch={handleSearch}
                  isLoading={isSearching}
                />
              </div>

              {/* Results Header */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
                <div className="mb-4 sm:mb-0">
                  <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {totalCount > 0 ? `${totalCount} cars available` : 'No cars found'}
                  </h2>
                  {searchTerm && (
                  <p className="text-gray-600 dark:text-gray-400 mt-1">
                    Results for &quot;{searchTerm}&quot;
                  </p>
                  )}
                </div>

                {/* View Controls */}
                <div className="flex items-center space-x-4">
                  {/* Sort Dropdown */}
                  <div className="flex items-center space-x-2">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Sort by:
                    </label>
                    <select
                      value={sortBy}
                      onChange={(e) => handleSortChange(e.target.value as typeof sortBy)}
                      className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                    >
                      {sortOptions.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* View Mode Toggle */}
                  <div className="flex items-center border border-gray-300 dark:border-gray-600 rounded-md">
                    <Button
                      variant={viewMode === 'grid' ? 'default' : 'ghost'}
                      size="sm"
                      onClick={() => setViewMode('grid')}
                      className="rounded-r-none"
                    >
                      <Grid className="w-4 h-4" />
                    </Button>
                    <Button
                      variant={viewMode === 'list' ? 'default' : 'ghost'}
                      size="sm"
                      onClick={() => setViewMode('list')}
                      className="rounded-l-none"
                    >
                      <List className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Loading State */}
              {isLoading && (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-3 text-gray-600 dark:text-gray-400">Loading cars...</span>
                </div>
              )}

              {/* Error State */}
              {error && (
                <div className="text-center py-12">
                  <div className="text-red-600 dark:text-red-400 mb-4">
                    Failed to load car rentals. Please try again.
                  </div>
                  <Button onClick={() => window.location.reload()}>
                    Retry
                  </Button>
                </div>
              )}

              {/* Empty State */}
              {!isLoading && !error && carRentals.length === 0 && (
                <div className="text-center py-12">
                  <div className="text-gray-500 dark:text-gray-400 mb-4">
                    No car rentals found matching your criteria.
                  </div>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setFilters({});
                      setSearchTerm('');
                    }}
                  >
                    Clear Filters
                  </Button>
                </div>
              )}

              {/* Results Grid/List */}
              {!isLoading && !error && carRentals.length > 0 && (
                <AnimatePresence mode="wait">
                  <motion.div
                    key={viewMode}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                    className={
                      viewMode === 'grid'
                        ? 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6'
                        : 'space-y-6'
                    }
                  >
                    {carRentals.map((carRental) => (
                      <CarRentalCard
                        key={carRental.id}
                        carRental={carRental}
                        viewMode={viewMode}
                        formatPrice={formatPrice}
                      />
                    ))}
                  </motion.div>
                </AnimatePresence>
              )}

              {/* Load More Button (if pagination is needed) */}
              {!isLoading && !error && carRentals.length > 0 && (data as { next?: string })?.next && (
                <div className="text-center mt-8">
                  <Button
                    variant="outline"
                    onClick={() => {
                      // Implement pagination logic here
                      console.log('Load more cars');
                    }}
                  >
                    Load More Cars
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
