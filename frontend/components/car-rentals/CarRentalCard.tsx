'use client';

import React from 'react';
import Link from 'next/link';
import { 
  Car, 
  Users, 
  MapPin,
  Star,
  ArrowRight,
  Shield,
  Settings
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import OptimizedImage from '@/components/common/OptimizedImage';
import { getImageUrl } from '@/lib/utils';
import { useLocale } from 'next-intl';
import { useTranslations } from 'next-intl';
import { CarRental } from '@/lib/api/car-rentals';

interface CarRentalCardProps {
  carRental: CarRental;
  viewMode: 'grid' | 'list';
  formatPrice?: (price: number, currency: string) => string;
}

const getFuelIcon = (fuelType: string) => {
  switch (fuelType) {
    case 'gasoline':
      return '⛽';
    case 'diesel':
      return '🚛';
    case 'hybrid':
      return '🔋';
    case 'electric':
      return '⚡';
    case 'lpg':
      return '🔥';
    default:
      return '⛽';
  }
};

const getTransmissionIcon = (transmission: string) => {
  switch (transmission) {
    case 'manual':
      return '🔄';
    case 'automatic':
      return '⚙️';
    case 'semi_automatic':
      return '🔧';
    default:
      return '⚙️';
  }
};

export default function CarRentalCard({
  carRental,
  viewMode,
  formatPrice = (price, currency) => `${currency} ${price.toFixed(2)}`
}: CarRentalCardProps) {
  const locale = useLocale();
  const t = useTranslations('CarRentals');
  const isRTL = locale === 'fa';

  const getCarImage = () => {
    if (carRental.image_url) {
      return carRental.image_url;
    }
    if (carRental.image) {
      return getImageUrl(carRental.image);
    }
    return '/images/placeholder-car.jpg';
  };

  const getCarTitle = () => {
    return carRental.title || `${carRental.brand} ${carRental.model}`;
  };

  const getProductLink = () => {
    return `/${locale}/car-rentals/${carRental.slug}`;
  };

  const getPriceDisplay = () => {
    const price = parseFloat(carRental.price_per_day);
    return formatPrice(price, carRental.currency);
  };

  const getPricingSummary = () => {
    if (carRental.pricing_summary) {
      const { min_price, weekly_discount, monthly_discount } = carRental.pricing_summary;
      
      if (weekly_discount > 0 || monthly_discount > 0) {
        return (
          <div className="text-sm text-green-600 dark:text-green-400">
            {t('from')} {formatPrice(min_price, carRental.currency)}/day
            {weekly_discount > 0 && (
              <span className="ml-1 text-xs bg-green-100 dark:bg-green-900 px-2 py-1 rounded">
                -{weekly_discount}% {t('weekly')}
              </span>
            )}
          </div>
        );
      }
    }
    return (
      <div className="text-sm text-gray-700 dark:text-gray-400 font-medium">
        {getPriceDisplay()}/day
      </div>
    );
  };

  const getStatusBadges = () => {
    const badges = [];
    
    // Availability badge (highest priority)
    if (!carRental.is_available) {
      badges.push(
        <span key="unavailable" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 border border-red-200 dark:border-red-700">
          <span className="w-2 h-2 bg-red-500 rounded-full mr-1" />
          {t('notAvailable')}
        </span>
      );
    }
    
    if (carRental.is_featured) {
      badges.push(
        <span key="featured" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
          <Star className="w-3 h-3 mr-1" />
          {t('featured')}
        </span>
      );
    }
    
    if (carRental.is_popular) {
      badges.push(
        <span key="popular" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">
          <Users className="w-3 h-3 mr-1" />
          {t('popular')}
        </span>
      );
    }
    
    if (carRental.is_special) {
      badges.push(
        <span key="special" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
          <Shield className="w-3 h-3 mr-1" />
          {t('special')}
        </span>
      );
    }
    
    return badges;
  };

  // List view
  if (viewMode === 'list') {
    return (
      <Link 
        href={carRental.is_available ? getProductLink() : '#'} 
        className={`block group w-full ${!carRental.is_available ? 'cursor-not-allowed' : ''}`}
        onClick={(e) => !carRental.is_available && e.preventDefault()}
      >
        <Card className={`relative w-full rounded-xl shadow-md transition-all duration-300 border border-gray-200 dark:border-gray-700 overflow-hidden bg-white dark:bg-gray-900 ${
          carRental.is_available 
            ? 'hover:shadow-lg hover:scale-[1.01]' 
            : 'opacity-60 grayscale'
        }`}>
          <div className="flex flex-col md:flex-row">
            {/* Image Section */}
            <div className="relative w-full md:w-80 h-48 md:h-64 overflow-hidden">
              <OptimizedImage
                src={getCarImage()}
                alt={getCarTitle()}
                fill
                className="w-full h-full object-cover transition-all duration-300 group-hover:scale-105"
                fallbackSrc="/images/placeholder-car.jpg"
              />
              
              {/* Status Badges */}
              <div className="absolute top-3 left-3 flex flex-wrap gap-1">
                {getStatusBadges()}
              </div>
            </div>
            
            {/* Content Section */}
            <div className="flex-1 p-6">
              <div className="flex flex-col h-full">
                {/* Header */}
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                    {getCarTitle()}
                  </h3>
                  
                  <p className="text-gray-700 dark:text-gray-300 text-sm mb-4 line-clamp-2">
                    {carRental.short_description}
                  </p>
                  
                  {/* Car Details */}
                  <div className="flex flex-wrap gap-4 text-sm text-gray-700 dark:text-gray-400 mb-4">
                    <div className="flex items-center">
                      <Car className="w-4 h-4 mr-1" />
                      {carRental.year} {carRental.brand} {carRental.model}
                    </div>
                    <div className="flex items-center">
                      <Users className="w-4 h-4 mr-1" />
                      {carRental.seats} {t('seats')}
                    </div>
                    <div className="flex items-center">
                      <span className="mr-1">{getFuelIcon(carRental.fuel_type)}</span>
                      {carRental.fuel_type}
                    </div>
                    <div className="flex items-center">
                      <span className="mr-1">{getTransmissionIcon(carRental.transmission)}</span>
                      {carRental.transmission}
                    </div>
                  </div>
                  
                  {/* Location */}
                  <div className="flex items-center text-sm text-gray-600 dark:text-gray-400 mb-4">
                    <MapPin className="w-4 h-4 mr-1 text-gray-500 dark:text-gray-400" />
                    <span className="font-medium">{carRental.city}, {carRental.country}</span>
                  </div>
                </div>
                
                {/* Footer */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {getPriceDisplay()}
                    </div>
                    {getPricingSummary()}
                  </div>
                  
                  <div className="flex items-center text-blue-600 dark:text-blue-400 group-hover:text-blue-700 dark:group-hover:text-blue-300 transition-colors">
                    <span className="text-sm font-medium mr-2">{t('viewDetails')}</span>
                    <ArrowRight className={`w-4 h-4 transition-transform group-hover:translate-x-1 ${isRTL ? 'rotate-180' : ''}`} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </Link>
    );
  }

  // Grid view (Modern Card Design)
  return (
    <Link 
      href={carRental.is_available ? getProductLink() : '#'} 
      className={`block group w-full ${!carRental.is_available ? 'cursor-not-allowed' : ''}`}
      onClick={(e) => !carRental.is_available && e.preventDefault()}
    >
      <Card className={`relative w-full rounded-2xl shadow-lg transition-all duration-300 border border-gray-200 dark:border-gray-700 overflow-hidden bg-white dark:bg-gray-900 min-h-[420px] ${
        carRental.is_available 
          ? 'hover:shadow-xl hover:scale-[1.01] hover:-translate-y-0.5' 
          : 'opacity-60 grayscale'
      }`}>
        {/* Modern Gradient Background - More subtle for light mode */}
        <div className="absolute inset-0 bg-gradient-to-br from-gray-50/30 via-white to-blue-50/20 dark:from-gray-800 dark:via-gray-900 dark:to-gray-800" />
        
        {/* Image Section */}
        <div className="relative h-64 overflow-hidden">
          <OptimizedImage
            src={getCarImage()}
            alt={getCarTitle()}
            fill
            className="w-full h-full object-cover transition-all duration-300 group-hover:scale-105"
            fallbackSrc="/images/placeholder-car.jpg"
          />
          
          {/* Status Badges */}
          <div className="absolute top-3 left-3 flex flex-wrap gap-1">
            {getStatusBadges()}
          </div>
          
          {/* Category Badge */}
          <div className="absolute top-3 right-3">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-white/90 dark:bg-gray-800/90 text-gray-700 dark:text-gray-300 backdrop-blur-sm">
              {carRental.category.name}
            </span>
          </div>
        </div>
        
        {/* Content Section */}
        <CardContent className="p-6">
          {/* Header */}
          <div className="mb-4 relative z-10">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-1">
              {getCarTitle()}
            </h3>
            
            <p className="text-gray-700 dark:text-gray-300 text-sm mb-3 line-clamp-2">
              {carRental.short_description}
            </p>
          </div>
          
          {/* Car Details */}
          <div className="grid grid-cols-2 gap-3 mb-4 relative z-10">
            <div className="flex items-center text-sm text-gray-700 dark:text-gray-400">
              <Car className="w-4 h-4 mr-2 text-gray-600 dark:text-gray-400" />
              <span className="truncate font-medium">{carRental.year}</span>
            </div>
            <div className="flex items-center text-sm text-gray-700 dark:text-gray-400">
              <Users className="w-4 h-4 mr-2 text-gray-600 dark:text-gray-400" />
              <span className="font-medium">{carRental.seats} {t('seats')}</span>
            </div>
            <div className="flex items-center text-sm text-gray-700 dark:text-gray-400">
              <span className="mr-2 text-lg">{getFuelIcon(carRental.fuel_type)}</span>
              <span className="capitalize font-medium">{carRental.fuel_type}</span>
            </div>
            <div className="flex items-center text-sm text-gray-700 dark:text-gray-400">
              <Settings className="w-4 h-4 mr-2 text-gray-600 dark:text-gray-400" />
              <span className="capitalize font-medium">{carRental.transmission}</span>
            </div>
          </div>
          
          {/* Location */}
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400 mb-4 relative z-10">
            <MapPin className="w-4 h-4 mr-2 text-gray-500 dark:text-gray-400" />
            <span className="truncate font-medium">{carRental.city}, {carRental.country}</span>
          </div>
          
          {/* Pricing */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700 relative z-10">
            <div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {getPriceDisplay()}
              </div>
              {getPricingSummary()}
            </div>
            
            <div className="flex items-center text-blue-600 dark:text-blue-400 group-hover:text-blue-700 dark:group-hover:text-blue-300 transition-colors">
              <ArrowRight className={`w-5 h-5 transition-transform group-hover:translate-x-1 ${isRTL ? 'rotate-180' : ''}`} />
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
