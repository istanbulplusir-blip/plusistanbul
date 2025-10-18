'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useLocale } from 'next-intl';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronDown, 
  ChevronUp,
  Search,
  MapPin,
  Car,
  DollarSign,
  RotateCcw,
  Settings
} from 'lucide-react';
import { FunnelIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent } from '@/components/ui/Card';
import { CarRentalSearchParams } from '@/lib/api/car-rentals';
import { useCarRentalFilters } from '@/lib/hooks/useCarRentals';

interface CarRentalFiltersProps {
  filters: CarRentalSearchParams;
  onFiltersChange: (filters: CarRentalSearchParams) => void;
  onSearch: () => void;
  isLoading?: boolean;
}

export default function CarRentalFilters({
  filters,
  onFiltersChange,
  onSearch,
  isLoading = false
}: CarRentalFiltersProps) {
  const t = useTranslations('CarRentals');
  const locale = useLocale();
  const isRTL = locale === 'fa';
  const [isExpanded, setIsExpanded] = useState(false);
  const [localFilters, setLocalFilters] = useState<CarRentalSearchParams>(filters);
  const [isClient, setIsClient] = useState(false);
  
  const { data: filterData } = useCarRentalFilters();

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleFilterChange = (key: keyof CarRentalSearchParams, value: string | number | undefined) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleSearch = () => {
    onSearch();
  };

  const clearFilters = () => {
    const clearedFilters: CarRentalSearchParams = {};
    setLocalFilters(clearedFilters);
    onFiltersChange(clearedFilters);
  };

  const hasActiveFilters = Object.values(filters).some(value => 
    value !== undefined && value !== null && value !== ''
  );

  // Don't render anything until client-side hydration is complete
  if (!isClient) {
    return (
      <div className="w-full">
        <div className="lg:hidden mb-4">
          <Button
            variant="outline"
            className={`w-full flex items-center justify-center gap-2 ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}
            disabled
          >
            <FunnelIcon className="w-4 h-4" />
            {t('filters')}
            <ChevronDown className="w-4 h-4" />
          </Button>
        </div>
        <div className="xl:block">
          <Card className="w-full shadow-lg border border-gray-200 dark:border-gray-700">
            <CardContent className="p-4 sm:p-6">
              <div className="animate-pulse">
                <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
                <div className="space-y-4">
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded"></div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Mobile FunnelIcon Toggle - Only show on mobile */}
      <div className="lg:hidden mb-4">
        <Button
          onClick={() => setIsExpanded(!isExpanded)}
          variant="outline"
          className={`w-full flex items-center justify-center gap-2 ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}
        >
          <FunnelIcon className="w-4 h-4" />
          {t('filters')}
          {hasActiveFilters && (
            <span className={`px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full ${isRTL ? 'mr-2' : 'ml-2'}`}>
              {Object.values(filters).filter(v => v !== undefined && v !== null && v !== '').length}
            </span>
          )}
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </Button>
      </div>

      {/* FunnelIcon Content - Always visible on desktop, toggleable on mobile */}
      <div className="xl:block">
        <AnimatePresence>
          {(isExpanded || typeof window === 'undefined') && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <Card className="w-full shadow-lg border border-gray-200 dark:border-gray-700">
                <CardContent className="p-4 sm:p-6">
                  {/* Header */}
                  <div className={`flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 ${isRTL ? 'text-right' : 'text-left'}`}>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {t('filters')}
                    </h3>
                    <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}>
                      <Button
                        onClick={clearFilters}
                        variant="outline"
                        size="sm"
                        disabled={!hasActiveFilters}
                        className={`${isRTL ? 'flex-row-reverse' : 'flex-row'}`}
                      >
                        <RotateCcw className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                        {t('clearFilters')}
                      </Button>
                      <Button
                        onClick={handleSearch}
                        disabled={isLoading}
                        className="bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        <Search className={`w-4 h-4 ${isRTL ? 'ml-2' : 'mr-2'}`} />
                        {t('search')}
                      </Button>
                    </div>
                  </div>

                  {/* Search Bar */}
                  <div className="mb-6">
                    <div className="relative">
                      <Search className={`absolute top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 ${isRTL ? 'right-3' : 'left-3'}`} />
                      <Input
                        type="text"
                        placeholder={t('searchPlaceholder')}
                        value={localFilters.query || ''}
                        onChange={(e) => handleFilterChange('query', e.target.value)}
                        className={`w-full pl-10 pr-4 py-3 text-lg border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${isRTL ? 'text-right' : 'text-left'}`}
                      />
                    </div>
                  </div>

                  {/* FunnelIcon Grid - Responsive */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
                    {/* Location FunnelIcons */}
                    <div className="space-y-4">
                      <div className={`flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}>
                        <MapPin className="w-4 h-4" />
                        {t('location')}
                      </div>
                      
                      {/* City */}
                      <div>
                        <label className={`block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                          {t('city')}
                        </label>
                        <select
                          value={localFilters.city || ''}
                          onChange={(e) => handleFilterChange('city', e.target.value || undefined)}
                          className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${isRTL ? 'text-right' : 'text-left'}`}
                        >
                          <option value="">{t('allCities')}</option>
                          {filterData?.cities?.map((city, index) => (
                            <option key={`city-${city}-${index}`} value={city}>
                              {city}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Country */}
                      <div>
                        <label className={`block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                          {t('country')}
                        </label>
                        <select
                          value={localFilters.country || ''}
                          onChange={(e) => handleFilterChange('country', e.target.value || undefined)}
                          className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${isRTL ? 'text-right' : 'text-left'}`}
                        >
                          <option value="">{t('allCountries')}</option>
                          {filterData?.countries?.map((country, index) => (
                            <option key={`country-${country}-${index}`} value={country}>
                              {country}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Vehicle FunnelIcons */}
                    <div className="space-y-4">
                      <div className={`flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}>
                        <Car className="w-4 h-4" />
                        {t('vehicle')}
                      </div>
                      
                      {/* Brand */}
                      <div>
                        <label className={`block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                          {t('brand')}
                        </label>
                        <select
                          value={localFilters.brand || ''}
                          onChange={(e) => handleFilterChange('brand', e.target.value || undefined)}
                          className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${isRTL ? 'text-right' : 'text-left'}`}
                        >
                          <option value="">{t('allBrands')}</option>
                          {filterData?.brands?.map((brand, index) => (
                            <option key={`brand-${brand}-${index}`} value={brand}>
                              {brand}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Category */}
                      <div>
                        <label className={`block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                          {t('category')}
                        </label>
                        <select
                          value={localFilters.category || ''}
                          onChange={(e) => handleFilterChange('category', e.target.value || undefined)}
                          className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${isRTL ? 'text-right' : 'text-left'}`}
                        >
                          <option value="">{t('allCategories')}</option>
                          {filterData?.categories?.map((category) => (
                            <option key={category.id} value={category.slug}>
                              {category.name}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Specifications */}
                    <div className="space-y-4">
                      <div className={`flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}>
                        <Settings className="w-4 h-4" />
                        {t('specifications')}
                      </div>
                      
                      {/* Fuel Type */}
                      <div>
                        <label className={`block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                          {t('fuelType')}
                        </label>
                        <select
                          value={localFilters.fuel_type || ''}
                          onChange={(e) => handleFilterChange('fuel_type', e.target.value || undefined)}
                          className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${isRTL ? 'text-right' : 'text-left'}`}
                        >
                          <option value="">{t('allFuelTypes')}</option>
                          {filterData?.fuel_types?.map((fuelType, index) => (
                            <option key={`fuel-${fuelType}-${index}`} value={fuelType}>
                              {fuelType}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Transmission */}
                      <div>
                        <label className={`block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                          {t('transmission')}
                        </label>
                        <select
                          value={localFilters.transmission || ''}
                          onChange={(e) => handleFilterChange('transmission', e.target.value || undefined)}
                          className={`w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${isRTL ? 'text-right' : 'text-left'}`}
                        >
                          <option value="">{t('allTransmissions')}</option>
                          {filterData?.transmissions?.map((transmission, index) => (
                            <option key={`transmission-${transmission}-${index}`} value={transmission}>
                              {transmission}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>

                    {/* Price Range */}
                    <div className="space-y-4">
                      <div className={`flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}>
                        <DollarSign className="w-4 h-4" />
                        {t('priceRange')}
                      </div>
                      
                      {/* Min Price */}
                      <div>
                        <label className={`block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                          {t('minPrice')}
                        </label>
                        <Input
                          type="number"
                          placeholder={t('minPrice')}
                          value={localFilters.min_price || ''}
                          onChange={(e) => handleFilterChange('min_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                          className={`w-full ${isRTL ? 'text-right' : 'text-left'}`}
                        />
                      </div>

                      {/* Max Price */}
                      <div>
                        <label className={`block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                          {t('maxPrice')}
                        </label>
                        <Input
                          type="number"
                          placeholder={t('maxPrice')}
                          value={localFilters.max_price || ''}
                          onChange={(e) => handleFilterChange('max_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                          className={`w-full ${isRTL ? 'text-right' : 'text-left'}`}
                        />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}