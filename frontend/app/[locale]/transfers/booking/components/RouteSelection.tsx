'use client';

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useTranslations } from 'next-intl';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, MapPin, Star, Clock, ArrowRight, AlertTriangle, RefreshCw, Percent, Car, TrendingUp, Award } from 'lucide-react';
import { useTransferBookingStore } from '@/lib/stores/transferBookingStore';
import { useToast } from '@/components/Toast';
import { useApiRetry } from '@/hooks/useRetry';
import * as transfersApi from '@/lib/api/transfers';
import { TransferRoute } from '@/lib/api/transfers';
import { TransferLocation } from '@/lib/types/api';
import dynamic from 'next/dynamic';
import { UI_CLASSES } from '@/lib/constants/ui';

// Dynamic import for MapLocationPicker to avoid SSR issues
const MapLocationPicker = dynamic(
  () => import('@/components/transfers/MapLocationPicker'),
  { 
    ssr: false,
    loading: () => (
      <div className="w-full h-64 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
        <div className="text-gray-500 dark:text-gray-400">در حال بارگذاری نقشه...</div>
      </div>
    )
  }
);

interface RouteSelectionProps {
  onNext: () => void;
}

export default function RouteSelection({ onNext }: RouteSelectionProps) {
  const t = useTranslations('transfers');
  const { addToast } = useToast();
  
  // Get booking state from store
  const {
    route_data,
    setRoute,
    setError,
    errors,
  } = useTransferBookingStore();

  // Local state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOrigin, setSelectedOrigin] = useState('');
  const [selectedDestination, setSelectedDestination] = useState('');
  const [routes, setRoutes] = useState<TransferRoute[]>([]);
  const [availableOrigins, setAvailableOrigins] = useState<string[]>([]);
  const [displayedRoutesCount, setDisplayedRoutesCount] = useState(3);
  const [availableDestinations, setAvailableDestinations] = useState<string[]>([]);
  
  // Map selection mode
  const [selectionMode, setSelectionMode] = useState<'list' | 'map'>('list');
  const [selectedOriginLocation, setSelectedOriginLocation] = useState<TransferLocation | null>(null);
  const [selectedDestinationLocation, setSelectedDestinationLocation] = useState<TransferLocation | null>(null);

  // Enhanced error handling with retry
  const {
    isLoading,
    retryCount,
    executeApiCall,
    reset: resetRetry
  } = useApiRetry<{ count: number; results: TransferRoute[] }>({
    maxAttempts: 3,
    delayMs: 1000,
    backoffMultiplier: 2
  });

  // Extract origins and destinations from routes - memoized to prevent unnecessary recalculations
  const extractOriginsAndDestinations = useCallback((routesData: TransferRoute[]) => {
    const origins = new Set<string>();
    const destinations = new Set<string>();
    
    routesData.forEach(route => {
      origins.add(route.origin);
      destinations.add(route.destination);
    });
    
    setAvailableOrigins(Array.from(origins).sort());
    setAvailableDestinations(Array.from(destinations).sort());
  }, []);

  // Fetch routes with enhanced error handling - memoized with stable dependencies
  const fetchRoutes = useCallback(async () => {
    try {
      setError('route', null);
      
      const result = await executeApiCall(
        () => transfersApi.getTransferRoutes(),
        (data) => {
          setRoutes(data.results);
          extractOriginsAndDestinations(data.results);
        },
        (error) => {
          const errorMessage = error.message || t('errorLoadingRoutes');
          setError('route', {
            code: 'ROUTES_FETCH_FAILED',
            message: errorMessage,
            details: error,
            retryable: true
          });
          
          addToast({
            type: 'error',
            title: t('errorLoadingRoutes'),
            message: errorMessage
          });
        }
      );
      
      return result;
    } catch {
      // Error already handled in onError callback
      return { count: 0, next: null, previous: null, results: [] };
    }
  }, [executeApiCall, setError, t, addToast, extractOriginsAndDestinations]);

  // Store fetchRoutes in ref to avoid infinite loop in useEffect
  const fetchRoutesRef = useRef(fetchRoutes);
  fetchRoutesRef.current = fetchRoutes;

  // Handle route selection
  const handleRouteSelect = useCallback((route: transfersApi.TransferRoute) => {
    setRoute(route);
    setError('route', null);
    onNext();
  }, [setRoute, setError, onNext]);

  // Handle retry
  const handleRetry = useCallback(() => {
    resetRetry();
    fetchRoutes();
  }, [resetRetry, fetchRoutes]);

  // Filter routes based on search and filters - memoized to prevent unnecessary recalculations
  const filteredRoutes = useMemo(() => {
    return routes.filter(route => {
      const matchesSearch = !searchTerm || 
        route.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        route.origin.toLowerCase().includes(searchTerm.toLowerCase()) ||
        route.destination.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesOrigin = !selectedOrigin || route.origin === selectedOrigin;
      const matchesDestination = !selectedDestination || route.destination === selectedDestination;
      
      return matchesSearch && matchesOrigin && matchesDestination;
    });
  }, [routes, searchTerm, selectedOrigin, selectedDestination]);

  // Check if route exists between two locations
  const checkRouteExists = useCallback(async (origin: TransferLocation, destination: TransferLocation) => {
    try {
      const response = await fetch('/api/v1/transfers/locations/check_route_availability/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          origin_id: origin.id.startsWith('temp-') ? null : origin.id,
          destination_id: destination.id.startsWith('temp-') ? null : destination.id,
          origin_name: origin.name,
          destination_name: destination.name
        })
      });

      if (response.ok) {
        const data = await response.json();
        return data;
      }
    } catch (error) {
      console.error('Error checking route availability:', error);
    }
    
    return { route_exists: false };
  }, []);

  // Map selection handlers
  const handleOriginLocationSelect = useCallback(async (location: TransferLocation) => {
    setSelectedOriginLocation(location);
    setSelectedOrigin(location.name);
    
        // هشدار برای مکان‌های خارجی
        if (location.id.startsWith('external-')) {
          addToast({
            type: 'warning',
            title: t('externalLocation'),
            message: t('externalLocationMessage', { location: location.name })
          });
        }
    
    // Create route data when both locations are selected
    if (selectedDestinationLocation) {
      // بررسی کن که آیا مسیر موجود است
      const routeCheck = await checkRouteExists(location, selectedDestinationLocation);
      
      if (routeCheck.route_exists) {
        // از مسیر موجود استفاده کن
        addToast({
          type: 'success',
          title: t('routeExists'),
          message: t('routeExistsMessage', { origin: location.name, destination: selectedDestinationLocation.name })
        });
        setRoute(routeCheck.route);
      } else {
        // مسیر موجود نیست - خطا نمایش دهید
        addToast({
          type: 'error',
          title: t('noVehiclesAvailable'),
          message: t('noVehiclesAvailableMessage')
        });
        // مسیر را تنظیم نکنید
        return;
      }
    }
  }, [selectedDestinationLocation, setRoute, t, addToast, checkRouteExists]);


  const handleDestinationLocationSelect = useCallback(async (location: TransferLocation) => {
    setSelectedDestinationLocation(location);
    setSelectedDestination(location.name);
    
        // هشدار برای مکان‌های خارجی
        if (location.id.startsWith('external-')) {
          addToast({
            type: 'warning',
            title: t('externalLocation'),
            message: t('externalLocationMessage', { location: location.name })
          });
        }
    
    // Create route data when both locations are selected
    if (selectedOriginLocation) {
      // بررسی کن که آیا مسیر موجود است
      const routeCheck = await checkRouteExists(selectedOriginLocation, location);
      
      if (routeCheck.route_exists) {
        // از مسیر موجود استفاده کن
        addToast({
          type: 'success',
          title: t('routeExists'),
          message: t('routeExistsMessage', { origin: selectedOriginLocation.name, destination: location.name })
        });
        setRoute(routeCheck.route);
      } else {
        // مسیر موجود نیست - خطا نمایش دهید
        addToast({
          type: 'error',
          title: t('noVehiclesAvailable'),
          message: t('noVehiclesAvailableMessage')
        });
        // مسیر را تنظیم نکنید
        return;
      }
    }
  }, [selectedOriginLocation, setRoute, t, addToast, checkRouteExists]);

  // Clear handlers
  const handleOriginLocationClear = useCallback(() => {
    setSelectedOriginLocation(null);
    setSelectedOrigin('');
  }, []);

  const handleDestinationLocationClear = useCallback(() => {
    setSelectedDestinationLocation(null);
    setSelectedDestination('');
  }, []);

  // View more routes handler
  const handleViewMoreRoutes = useCallback(() => {
    setDisplayedRoutesCount(prev => prev + 3);
  }, []);

  // Reset displayed routes count when filters change
  useEffect(() => {
    setDisplayedRoutesCount(3);
  }, [searchTerm, selectedOrigin, selectedDestination]);

  // Load routes on component mount - only once
  useEffect(() => {
    fetchRoutesRef.current();
  }, []); // Empty dependency array to run only once

  // Loading state with better UX
  if (isLoading) {
    return (
      <motion.div 
        className="space-y-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="text-center py-12">
          <motion.div
            className="relative mx-auto mb-6"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <div className="w-16 h-16 border-4 border-primary-200 dark:border-primary-800 rounded-full"></div>
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-primary-500 dark:border-t-primary-400 rounded-full animate-spin"></div>
          </motion.div>
          <motion.h3 
            className="text-xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-3"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            {t('loadingRoutes')}
          </motion.h3>
          <motion.p 
            className="text-gray-600 dark:text-gray-400"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            {retryCount > 0 && t('retryAttempt', { attempt: retryCount + 1, max: 3 })}
          </motion.p>
        </div>
        
        {/* Loading Skeleton */}
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <motion.div
              key={i}
              className="p-6 rounded-xl bg-gradient-to-r from-gray-100 via-gray-200 to-gray-100 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 * i }}
            >
              <div className="flex items-center justify-between">
                <div className="space-y-2 flex-1">
                  <div className="h-5 bg-gray-300 dark:bg-gray-600 rounded-lg w-3/4"></div>
                  <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded-lg w-1/2"></div>
                </div>
                <div className="w-20 h-8 bg-gray-300 dark:bg-gray-600 rounded-lg"></div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    );
  }

  // Enhanced error state with retry information
  if (errors.route) {
    return (
      <div className={UI_CLASSES.cardLarge}>
        <div className={UI_CLASSES.textCenter}>
          <div className={`mx-auto ${UI_CLASSES.flexCenter} h-16 w-16 rounded-full bg-red-100 dark:bg-red-900/20 mb-4`}>
            <AlertTriangle className={`${UI_CLASSES.iconMedium} text-red-600 dark:text-red-400`} />
          </div>
          
          <h3 className={`${UI_CLASSES.subtitle} mb-2`}>
            {t('errorLoadingRoutes')}
          </h3>
          
          <p className={`${UI_CLASSES.description} mb-4`}>
            {errors.route.message}
          </p>
          
          {retryCount > 0 && (
            <p className={`${UI_CLASSES.smallText} text-gray-500 dark:text-gray-400 mb-6`}>
              {t('retryAttempts', { attempts: retryCount, max: 3 })}
            </p>
          )}
          
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={handleRetry}
              className={UI_CLASSES.buttonPrimary}
            >
              <RefreshCw className={UI_CLASSES.iconSmall} />
              {t('retry')}
            </button>
            
            <button
              onClick={() => window.location.reload()}
              className={UI_CLASSES.buttonSecondary}
            >
              {t('refreshPage')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Helper function to render badges
  const renderBadges = (route: transfersApi.TransferRoute) => {
    const badges = [];
    
    if (route.is_popular) {
      badges.push(
        <motion.span 
          key="popular" 
          className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-gradient-to-r from-yellow-100 to-yellow-200 dark:from-yellow-900/30 dark:to-yellow-800/30 text-yellow-800 dark:text-yellow-200 border border-yellow-200/50 dark:border-yellow-700/50 shadow-sm"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          whileHover={{ scale: 1.05 }}
        >
          <Star className="w-3 h-3 mr-1.5 fill-current" />
          {t('popularBadge')}
        </motion.span>
      );
    }
    
    if (route.round_trip_discount_enabled) {
      badges.push(
        <motion.span 
          key="discount" 
          className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-gradient-to-r from-green-100 to-green-200 dark:from-green-900/30 dark:to-green-800/30 text-green-800 dark:text-green-200 border border-green-200/50 dark:border-green-700/50 shadow-sm"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          whileHover={{ scale: 1.05 }}
        >
          <Percent className="w-3 h-3 mr-1.5" />
          {t('discountBadge')}
        </motion.span>
      );
    }
    
    if (parseFloat(route.peak_hour_surcharge || '0') > 0 || parseFloat(route.midnight_surcharge || '0') > 0) {
      badges.push(
        <motion.span 
          key="surcharge" 
          className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-gradient-to-r from-orange-100 to-orange-200 dark:from-orange-900/30 dark:to-orange-800/30 text-orange-800 dark:text-orange-200 border border-orange-200/50 dark:border-orange-700/50 shadow-sm"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.3 }}
          whileHover={{ scale: 1.05 }}
        >
          <Clock className="w-3 h-3 mr-1.5" />
          {t('surchargeBadge')}
        </motion.span>
      );
    }
    
    return badges;
  };

  // Helper function to render route features
  const renderRouteFeatures = (route: transfersApi.TransferRoute) => {
    const features = [];
    
    if (route.round_trip_discount_enabled) {
      features.push(
        <div key="discount" className="flex items-center gap-2 text-sm text-green-600">
          <Percent className="w-4 h-4" />
          <span>{t('roundTripDiscountPercentage')}: {route.round_trip_discount_percentage}%</span>
        </div>
      );
    }
    
    if (parseFloat(route.peak_hour_surcharge || '0') > 0) {
      features.push(
        <div key="peak" className="flex items-center gap-2 text-sm text-orange-600">
          <Clock className="w-4 h-4" />
          <span>{t('peakHourSurcharge')}: {route.peak_hour_surcharge}%</span>
        </div>
      );
    }
    
    if (parseFloat(route.midnight_surcharge || '0') > 0) {
      features.push(
        <div key="midnight" className="flex items-center gap-2 text-sm text-purple-600">
          <Clock className="w-4 h-4" />
          <span>{t('midnightSurcharge')}: {route.midnight_surcharge}%</span>
        </div>
      );
    }
    
    return features;
  };

  return (
    <motion.div 
      className="space-y-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >
      {/* Header */}
      <motion.div 
        className="text-center"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <h2 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-3">
          {t('selectRouteAndVehicle')}
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          {t('step1')}
        </p>
      </motion.div>

      {/* Selection Mode Toggle */}
      <motion.div 
        className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-6"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.15 }}
      >
        <div className="flex justify-center">
          <div className="inline-flex bg-gray-100 dark:bg-gray-700 rounded-xl p-1">
            <button
              onClick={() => setSelectionMode('list')}
              className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
                selectionMode === 'list'
                  ? 'bg-white dark:bg-gray-600 text-primary-600 dark:text-primary-400 shadow-md'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
              }`}
            >
              <Search className="w-4 h-4 inline-block mr-2" />
              {t('selectFromList')}
            </button>
            <button
              onClick={() => setSelectionMode('map')}
              className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
                selectionMode === 'map'
                  ? 'bg-white dark:bg-gray-600 text-primary-600 dark:text-primary-400 shadow-md'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
              }`}
            >
              <MapPin className="w-4 h-4 inline-block mr-2" />
              {t('selectFromMap')}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Search and Filter */}
      {selectionMode === 'list' && (
        <motion.div 
          className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-8"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Search */}
          <motion.div 
            className="relative"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-primary-400 w-5 h-5" />
            <input
              type="text"
              placeholder={t('searchPlaceholder')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-4 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700/50 dark:text-white dark:placeholder:text-gray-400 transition-all duration-300 backdrop-blur-sm"
            />
          </motion.div>

          {/* Origin Filter */}
          <motion.select
            value={selectedOrigin}
            onChange={(e) => setSelectedOrigin(e.target.value)}
            className="px-4 py-4 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700/50 dark:text-white transition-all duration-300 backdrop-blur-sm"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <option value="">{t('allOrigins')}</option>
            {availableOrigins.map((origin: string) => (
              <option key={origin} value={origin}>{origin}</option>
            ))}
          </motion.select>

          {/* Destination Filter */}
          <motion.select
            value={selectedDestination}
            onChange={(e) => setSelectedDestination(e.target.value)}
            className="px-4 py-4 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700/50 dark:text-white transition-all duration-300 backdrop-blur-sm"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <option value="">{t('allDestinations')}</option>
            {availableDestinations.map((destination: string) => (
              <option key={destination} value={destination}>{destination}</option>
            ))}
          </motion.select>
        </div>

        {/* Clear Filters */}
        <motion.button
          onClick={() => {
            setSearchTerm('');
            setSelectedOrigin('');
            setSelectedDestination('');
          }}
          className="px-6 py-3 bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 text-gray-700 dark:text-gray-300 rounded-xl hover:from-gray-200 hover:to-gray-300 dark:hover:from-gray-600 dark:hover:to-gray-500 transition-all duration-300 font-medium shadow-sm hover:shadow-md"
          whileHover={{ scale: 1.05, y: -2 }}
          whileTap={{ scale: 0.95 }}
        >
          <span className="flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            {t('clearFilters')}
          </span>
        </motion.button>
      </motion.div>
      )}

      {/* Routes List */}
      {selectionMode === 'list' && (
      <motion.div 
        className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-8"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <motion.h3 
          className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent mb-6"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          {t('availableRoutes')} ({filteredRoutes.length})
        </motion.h3>

        <AnimatePresence mode="wait">
          {filteredRoutes.length === 0 ? (
            <motion.div 
              className="text-center py-12"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.6 }}
            >
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.1 }}
              >
                <MapPin className="w-20 h-20 text-gray-400 mx-auto mb-6" />
              </motion.div>
              <motion.h3 
                className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3"
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.2 }}
              >
                {t('noRoutesFound')}
              </motion.h3>
              <motion.p 
                className="text-gray-600 dark:text-gray-400 max-w-md mx-auto"
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.3 }}
              >
                {t('noRoutesFoundDescription')}
              </motion.p>
            </motion.div>
          ) : (
            <>
              <motion.div 
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.5 }}
              >
                {filteredRoutes.slice(0, displayedRoutesCount).map((route: transfersApi.TransferRoute, index: number) => (
                  <motion.div
                    key={route.id}
                    onClick={() => handleRouteSelect(route)}
                    className={`
                      p-6 border-2 rounded-2xl cursor-pointer transition-all duration-300 backdrop-blur-sm
                      ${route_data?.id === route.id
                        ? 'border-primary-500 bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 shadow-lg shadow-primary-500/25'
                        : 'border-gray-200/50 dark:border-gray-600/50 hover:border-primary-300 dark:hover:border-primary-400 hover:bg-gradient-to-br hover:from-gray-50 hover:to-gray-100 dark:hover:from-gray-700/50 dark:hover:to-gray-600/50 hover:shadow-lg'
                      }
                    `}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 * index }}
                    whileHover={{ scale: 1.02, y: -4 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {/* Route Info */}
                    <div className="mb-4">
                      {/* Title */}
                      <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-3 line-clamp-2">
                        {route.name || `${route.origin} → ${route.destination}`}
                      </h4>
                      
                      {/* Badges */}
                      <div className="flex flex-wrap gap-2 mb-3">
                        {renderBadges(route)}
                      </div>
                      
                      <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                        <MapPin className="w-4 h-4" />
                        <span>{route.origin}</span>
                        <ArrowRight className="w-4 h-4" />
                        <span>{route.destination}</span>
                      </div>
                      
                      {route.description && (
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                          {route.description}
                        </p>
                      )}
                    </div>

                    {/* Route Features */}
                    <div className="space-y-2 mb-3">
                      {renderRouteFeatures(route)}
                    </div>

                    {/* Vehicle Types Available */}
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-3">
                      <Car className="w-4 h-4" />
                      <span>{route.pricing.length} {t('vehicleType')} {t('available')}</span>
                    </div>

                    {/* Popularity Info */}
                    {route.is_popular && (
                      <div className="flex items-center gap-2 text-sm text-yellow-600 dark:text-yellow-400 mb-2">
                        <TrendingUp className="w-4 h-4" />
                        <span>{t('popularRoute')}</span>
                      </div>
                    )}

                    {/* Selection Indicator */}
                    {route_data?.id === route.id && (
                      <div className="mt-3 pt-3 border-t border-blue-200 dark:border-blue-400">
                        <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 text-sm">
                          <Award className="w-4 h-4" />
                          {t('selected')}
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </motion.div>
              
              {/* View More Button */}
              {filteredRoutes.length > displayedRoutesCount && (
                <motion.div 
                  className="flex justify-center mt-6"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <button
                    onClick={handleViewMoreRoutes}
                    className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-lg hover:from-primary-600 hover:to-secondary-600 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
                  >
                    {t('viewMore')} ({filteredRoutes.length - displayedRoutesCount} {t('remaining')})
                  </button>
                </motion.div>
              )}
            </>
          )}
        </AnimatePresence>
      </motion.div>
      )}

      {/* Map Selection */}
      {selectionMode === 'map' && (
        <motion.div 
          className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-8"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
                {t('selectOriginAndDestination')}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {t('selectOriginAndDestinationDescription')}
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('origin')}
                </label>
                <MapLocationPicker
                  selectedLocation={selectedOriginLocation}
                  onLocationSelect={handleOriginLocationSelect}
                  onLocationClear={handleOriginLocationClear}
                  placeholder={t('selectOriginFromMap')}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('destination')}
                </label>
                <MapLocationPicker
                  selectedLocation={selectedDestinationLocation}
                  onLocationSelect={handleDestinationLocationSelect}
                  onLocationClear={handleDestinationLocationClear}
                  placeholder={t('selectDestinationFromMap')}
                />
              </div>
            </div>
            
            {selectedOriginLocation && selectedDestinationLocation && (
              <motion.div 
                className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                    <div>
                      <div className="font-medium text-blue-900 dark:text-blue-100">
                        {selectedOriginLocation.name} → {selectedDestinationLocation.name}
                      </div>
                      <div className="text-sm text-blue-700 dark:text-blue-300">
                        {t('routeSelectedFromMap')}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={onNext}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                  >
{t('continue')}
                  </button>
                </div>
              </motion.div>
            )}
          </div>
        </motion.div>
      )}

      {/* Navigation */}
      {route_data && (
        <motion.div 
          className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 p-6"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-gradient-to-r from-success-500 to-success-600 rounded-full animate-pulse"></div>
              <span className="text-success-600 dark:text-success-400 font-medium">
                {t('routeSelected')}: {route_data.name || `${route_data.origin} → ${route_data.destination}`}
              </span>
            </div>
            <motion.button
              onClick={onNext}
              className="px-6 py-3 bg-gradient-to-r from-primary-500 to-secondary-500 hover:from-primary-600 hover:to-secondary-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-glow transition-all duration-300"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="flex items-center gap-2">
                {t('continueToVehicleSelection')}
                <ArrowRight className="w-5 h-5" />
              </span>
            </motion.button>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}