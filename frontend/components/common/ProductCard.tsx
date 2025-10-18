'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { 
  MapPin, 
  Clock, 
  Users, 
  Calendar,
  Music,
  Trophy,
  Drama,
  Sparkles,
  Briefcase,
  Palette,
  Ticket,
  ArrowRight
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/Card';
import OptimizedImage from './OptimizedImage';
import { getImageUrl } from '@/lib/utils';
import { useLocale } from 'next-intl';
import { useTranslations } from 'next-intl';

interface BaseProduct {
  id: string;
  slug: string;
  title?: string;
  description?: string;
  short_description?: string;
  image?: string;
  image_url?: string;
  rating?: number;
  average_rating?: number;
  review_count?: number;
}

interface TourProduct extends BaseProduct {
  type: 'tour';
  location?: string;
  duration_hours: number;
  starting_price?: number | null;
  next_schedule_date?: string | null;
  next_schedule_capacity_available?: number | null;
  next_schedule_capacity_total?: number | null;
  has_upcoming?: boolean;
  category?: { id: string; name: string } | string;
  category_slug?: string;
  category_name?: string;
  min_participants?: number;
  max_participants?: number;
  end_time?: string;
  rating?: number;
}

interface EventProduct extends BaseProduct {
  type: 'event';
  style: string;
  venue?: {
    id: string;
    name: string;
    city: string;
    total_capacity?: number;
    remaining_capacity?: number;
  };
  performances?: Array<{
    id: string;
    date: string;
    start_time?: string;
    end_time?: string;
  }>;
  artists?: Array<{
    id: string;
    name: string;
  }>;
  start_time?: string;
  end_time?: string;
  min_price?: number;
  ticket_types?: Array<{ price_modifier: number }>;
  age_restriction?: number;
  category?: { id: string; name: string };
  rating?: number;
  average_rating?: number;
  review_count?: number;
  is_active?: boolean;
}

type Product = TourProduct | EventProduct;

interface ProductCardProps {
  product: Product;
  viewMode: 'grid' | 'list';
  formatDate?: (date: string) => string;
  formatPrice?: (price: number, currency: string) => string;
}

const getStyleIcon = (style: string) => {
  switch (style) {
    case 'music': return <Music className="h-4 w-4" />;
    case 'sports': return <Trophy className="h-4 w-4" />;
    case 'theater': return <Drama className="h-4 w-4" />;
    case 'festival': return <Sparkles className="h-4 w-4" />;
    case 'conference': return <Briefcase className="h-4 w-4" />;
    case 'exhibition': return <Palette className="h-4 w-4" />;
    default: return <Ticket className="h-4 w-4" />;
  }
};

const getStyleColor = (style: string) => {
  switch (style) {
    case 'music': return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
    case 'sports': return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    case 'theater': return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
    case 'festival': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    case 'conference': return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
    case 'exhibition': return 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200';
    default: return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
  }
};

export default function ProductCard({
  product,
  viewMode,
  formatDate
}: ProductCardProps) {
  const locale = useLocale();
  const isRTL = locale === 'fa';
  const t = useTranslations('common');

  // Helper for stars
  const renderStars = (rating: number = 0) => (
    <div className="flex gap-0.5">
      {[...Array(5)].map((_, i) => (
        <svg key={i} className={`w-4 h-4 ${i < rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300 dark:text-gray-600'}`} viewBox="0 0 20 20"><polygon points="10,1 12.59,7.36 19.51,7.64 14,12.14 15.82,18.99 10,15.27 4.18,18.99 6,12.14 0.49,7.64 7.41,7.36" /></svg>
      ))}
    </div>
  );

  // Get product image with better fallback handling
  const getProductImage = () => {
    const imageSource = product.image_url || product.image;
    
    if (imageSource) {
      // Use the validated image URL function which handles all cases
      return getImageUrl(imageSource);
    }
    
    // Return appropriate fallback based on product type
    if (product.type === 'tour') {
      return '/images/tour-image.jpg';
    } else if (product.type === 'event') {
      return '/images/event-image.jpg';
    }

    // Default fallback
    return '/images/placeholder-car.jpg';
  };

  // Get product title
  const getProductTitle = () => {
    return product.title || t('noTitle');
  };

  // Get product description
  const getProductDescription = () => {
    if (product.type === 'tour') {
      return product.description || 'No description available';
    }
    return product.short_description || 'No description available';
  };

  // Get product price
  const getProductPrice = () => {
    if (product.type === 'tour') {
      const tour = product as TourProduct;
      if (tour.starting_price != null) {
        return `${t('from')} ${tour.starting_price}`;
      }
      return tour.starting_price ? `${t('from')} ${tour.starting_price}` : t('priceNotAvailable');
    }

    const event = product as EventProduct;
    if (event.min_price) {
      return `${t('from')} ${event.min_price}`;
    }
    return t('priceNotAvailable');
  };





  // Get product link
  const getProductLink = () => {
    if (product.type === 'tour') {
      return `/tours/${product.slug}`;
    }
    return `/events/${product.slug}`;
  };

  // --- LIST VIEW (Modern Mobile-First Design) ---
  if (viewMode === 'list') {
    if (product.type === 'tour') {
      const tour = product as TourProduct;
      return (
        <Link href={getProductLink()} className="block group w-full">
          <Card className={`relative w-full rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border-0 overflow-hidden bg-white dark:bg-gray-900 hover:scale-[1.01] hover:-translate-y-0.5 min-h-[180px] sm:min-h-[200px] flex ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}>
            {/* Modern Gradient Background */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-50/30 via-white to-blue-50/20 dark:from-gray-800 dark:via-gray-900 dark:to-gray-800" />
            
            
            {/* Image Section - 1/4 width */}
            <div className={`relative w-1/4 h-full min-h-[180px] sm:min-h-[200px] md:min-h-[220px] flex-shrink-0 overflow-hidden ${isRTL ? 'order-3' : 'order-1'}`}>
              <Image
                src={getProductImage()}
                alt={getProductTitle()}
                fill
                className="object-cover transition-all duration-300 group-hover:scale-105"
                sizes="(max-width: 640px) 25vw, (max-width: 768px) 25vw, (max-width: 1024px) 25vw, 25vw"
                priority={false}
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';
                  target.src = product.type === 'tour'
                    ? `${backendUrl}/media/defaults/tour-default.png`
                    : `${backendUrl}/media/defaults/event-default.png`;
                }}
              />
              
              {/* Modern Overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300" />
              
              {/* Status Badge */}
              {tour.next_schedule_capacity_available === 0 && (
                <div className="absolute top-2 left-2 z-20">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold bg-red-500 text-white shadow-md">
                    Sold Out
                  </span>
                </div>
              )}
              
              {/* Category Badge */}
              {(tour.category || tour.category_name) && (
                <div className="absolute top-2 left-2 z-20">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-white/20 backdrop-blur-md text-white shadow-md border border-white/30">
                    <MapPin className="h-2.5 w-2.5 mr-1" />
                    {typeof tour.category === 'string' ? tour.category : 
                     tour.category?.name || tour.category_name}
                  </span>
                </div>
              )}
            </div>
            
            {/* Content Section - 1/2 width */}
            <div className={`flex flex-col justify-between w-1/2 p-4 min-w-0 relative z-10 ${isRTL ? 'order-2' : 'order-2'}`}>
              {/* Header */}
              <div className="mb-3">
                <h3 className={`text-lg font-bold text-gray-900 dark:text-white mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300 line-clamp-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                  {getProductTitle()}
                </h3>
                
                {/* Rating & Reviews */}
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex items-center">
                    {renderStars(tour.rating || 0)}
                    <span className="ml-1 text-xs font-medium text-gray-600 dark:text-gray-400">
                      {tour.rating ? tour.rating.toFixed(1) : '0.0'}
                    </span>
                  </div>
                  {tour.review_count && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      ({tour.review_count})
                    </span>
                  )}
                </div>
              </div>
              
              {/* Details Grid */}
              <div className="grid grid-cols-1 gap-2 mb-3">
                <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                  <Clock className="h-3.5 w-3.5 text-blue-500" />
                  <span className="font-medium">{tour.duration_hours} {t('hours')}</span>
                </div>
                
                <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                  <Users className="h-3.5 w-3.5 text-green-500" />
                  <span>
                                    {tour.min_participants && tour.max_participants ? 
                  `${tour.min_participants}-${tour.max_participants} ${t('people')}` :
                  tour.max_participants ? `${t('max')} ${tour.max_participants} ${t('people')}` : t('unlimited')
                }
                  </span>
                </div>
                
                {tour.location && (
                  <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                    <MapPin className="h-3.5 w-3.5 text-red-500" />
                    <span className="truncate">{tour.location}</span>
                  </div>
                )}
              </div>
              
              {/* Next Schedule Info - Compact */}
              {tour.next_schedule_date && (
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-2 mb-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-blue-700 dark:text-blue-300">
                      Next Available
                    </span>
                    <span className="text-xs text-blue-600 dark:text-blue-400">
                      {new Date(tour.next_schedule_date).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                  
                  {/* Capacity Progress */}
                  {typeof tour.next_schedule_capacity_available === 'number' && typeof tour.next_schedule_capacity_total === 'number' && (
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-blue-600 dark:text-blue-400">
                        <span>
                          {tour.next_schedule_capacity_available > 0 ? 
                            `${tour.next_schedule_capacity_available} of ${tour.next_schedule_capacity_total} Available` : 
                            'Sold Out'
                          }
                        </span>
                      </div>
                      <div className="w-full bg-blue-200 dark:bg-blue-800 rounded-full h-1.5">
                        <div 
                          className={`h-1.5 rounded-full transition-all duration-300 ${
                            tour.next_schedule_capacity_available > 0 ? 'bg-blue-500' : 'bg-red-500'
                          }`}
                          style={{ 
                            width: `${Math.max(0, Math.min(100, ((tour.next_schedule_capacity_total - tour.next_schedule_capacity_available) / tour.next_schedule_capacity_total) * 100))}%` 
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              )}
              
              {/* Action Button */}
              <div className="flex items-center justify-end">
                <div className="flex items-center text-blue-600 dark:text-blue-400 font-medium group-hover:gap-1 transition-all duration-300">
                  <span className="text-xs">View Details</span>
                  <ArrowRight className="h-3 w-3 ml-1 group-hover:translate-x-0.5 transition-transform duration-300" />
                </div>
              </div>
            </div>
            
            {/* Price Section - 1/4 width */}
            <div className={`w-1/4 p-6 bg-gradient-to-br from-primary-50/90 to-secondary-50/90 dark:from-primary-900/90 dark:to-secondary-900/90 backdrop-blur-sm flex flex-col justify-center items-center border-l border-primary-200/30 dark:border-primary-700/30 ${isRTL ? 'order-1 border-l-0 border-r' : 'order-3'}`}>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600 dark:text-primary-400 mb-2">
                  {getProductPrice()}
                </div>
                <div className="text-sm text-primary-500 dark:text-primary-300 font-medium mb-2">{t('from')}</div>
                <div className={`text-xs px-3 py-1 rounded-full font-medium ${
                  tour.next_schedule_capacity_available === 0 
                    ? 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300' 
                    : 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300'
                }`}>
                  {tour.next_schedule_capacity_available === 0 ? 'Sold Out' : 'Available'}
                </div>
              </div>
            </div>
          </Card>
        </Link>
      );
    } else {
      // Event list view - Modern Design
      const event = product as EventProduct;
      return (
        <Link href={getProductLink()} className="block group w-full">
          <Card className={`relative w-full rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border-0 overflow-hidden bg-white dark:bg-gray-900 hover:scale-[1.01] hover:-translate-y-0.5 min-h-[180px] sm:min-h-[200px] flex ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}>
            {/* Modern Gradient Background */}
            <div className="absolute inset-0 bg-gradient-to-r from-purple-50/30 via-white to-pink-50/20 dark:from-gray-800 dark:via-gray-900 dark:to-gray-800" />
            
            
            {/* Image Section - 1/4 width */}
            <div className={`relative w-1/4 h-full min-h-[180px] sm:min-h-[200px] md:min-h-[220px] flex-shrink-0 overflow-hidden ${isRTL ? 'order-3' : 'order-1'}`}>
              <Image
                src={getProductImage()}
                alt={getProductTitle()}
                fill
                className="object-cover transition-all duration-300 group-hover:scale-105"
                sizes="(max-width: 640px) 25vw, (max-width: 768px) 25vw, (max-width: 1024px) 25vw, 25vw"
                priority={false}
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';
                  target.src = `${backendUrl}/media/defaults/event-default.png`;
                }}
              />
              
              {/* Modern Overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300" />
              
              {/* Style Badge */}
              <div className="absolute top-2 left-2 z-20">
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStyleColor(event.style || 'music')} shadow-md`}>
                  {getStyleIcon(event.style || 'music')}
                  <span className="ml-1">{event.style || 'Event'}</span>
                </span>
              </div>
              
              {/* Venue Badge */}
              {event.venue && (
                <div className="absolute top-8 left-2 z-20">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-white/20 backdrop-blur-md text-white shadow-md border border-white/30">
                    <MapPin className="h-2.5 w-2.5 mr-1" />
                    {event.venue.name}
                  </span>
                </div>
              )}
            </div>
            
            {/* Content Section - 1/2 width */}
            <div className={`flex flex-col justify-between w-1/2 p-4 min-w-0 relative z-10 ${isRTL ? 'order-2' : 'order-2'}`}>
              {/* Header */}
              <div className="mb-3">
                <h3 className={`text-lg font-bold text-gray-900 dark:text-white mb-2 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors duration-300 line-clamp-2 ${isRTL ? 'text-right' : 'text-left'}`}>
                  {getProductTitle()}
                </h3>
                
                {/* Rating & Reviews */}
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex items-center">
                    {renderStars(event.rating || 0)}
                    <span className="ml-1 text-xs font-medium text-gray-600 dark:text-gray-400">
                      {event.rating ? event.rating.toFixed(1) : '0.0'}
                    </span>
                  </div>
                  {event.review_count && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      ({event.review_count})
                    </span>
                  )}
                </div>
              </div>
              
              {/* Details Grid */}
              <div className="grid grid-cols-1 gap-2 mb-3">
                <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                  <Calendar className="h-3.5 w-3.5 text-purple-500" />
                  <span className="font-medium">
                    {event.performances && event.performances[0] ? 
                      (formatDate ? formatDate(event.performances[0].date) : new Date(event.performances[0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })) : 
                      'Date TBD'
                    }
                  </span>
                </div>
                
                {event.venue && (
                  <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                    <MapPin className="h-3.5 w-3.5 text-red-500" />
                    <span className="truncate">{event.venue.city || event.venue.name}</span>
                  </div>
                )}
                
                {event.venue && event.venue.total_capacity && (
                  <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                    <Users className="h-3.5 w-3.5 text-green-500" />
                    <span>Capacity: {event.venue.total_capacity}</span>
                  </div>
                )}
              </div>
              
              {/* Performance Info - Compact */}
              {event.performances && event.performances[0] && (
                <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-2 mb-2">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-purple-700 dark:text-purple-300">
                      Event Date
                    </span>
                    <span className="text-xs text-purple-600 dark:text-purple-400">
                      {new Date(event.performances[0].date).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                  
                  {/* Time Info */}
                  {event.performances[0].start_time && (
                    <div className="flex items-center gap-2 text-xs text-purple-600 dark:text-purple-400">
                      <Clock className="h-3 w-3" />
                      <span>
                        {event.performances[0].start_time}
                        {event.performances[0].end_time && ` - ${event.performances[0].end_time}`}
                      </span>
                    </div>
                  )}
                </div>
              )}
              
              {/* Action Button */}
              <div className="flex items-center justify-end">
                <div className="flex items-center text-purple-600 dark:text-purple-400 font-medium group-hover:gap-1 transition-all duration-300">
                  <span className="text-xs">View Details</span>
                  <ArrowRight className="h-3 w-3 ml-1 group-hover:translate-x-0.5 transition-transform duration-300" />
                </div>
              </div>
            </div>
            
            {/* Price Section - 1/4 width */}
            <div className={`w-1/4 p-6 bg-gradient-to-br from-primary-50/90 to-secondary-50/90 dark:from-primary-900/90 dark:to-secondary-900/90 backdrop-blur-sm flex flex-col justify-center items-center border-l border-primary-200/30 dark:border-primary-700/30 ${isRTL ? 'order-1 border-l-0 border-r' : 'order-3'}`}>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600 dark:text-primary-400 mb-2">
                  {getProductPrice()}
                </div>
                <div className="text-sm text-primary-500 dark:text-primary-300 font-medium mb-2">{t('from')}</div>
                <div className={`text-xs px-3 py-1 rounded-full font-medium ${
                  event.is_active 
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300' 
                    : 'bg-gray-100 text-gray-700 dark:bg-gray-900/50 dark:text-gray-300'
                }`}>
                  {event.is_active ? 'Active' : 'Inactive'}
                </div>
              </div>
            </div>
          </Card>
        </Link>
      );
    }
  }

  // --- GRID VIEW (Modern Card Design) ---
  return (
    <Link href={getProductLink()} className="block group w-full">
      <Card className="relative w-full rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border-0 overflow-hidden bg-white dark:bg-gray-900 hover:scale-[1.01] hover:-translate-y-0.5 min-h-[420px]">
        {/* Modern Gradient Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/20 via-white to-purple-50/10 dark:from-gray-800 dark:via-gray-900 dark:to-gray-800" />
        
        
        {/* Image Section */}
        <div className="relative h-64 overflow-hidden">
          <OptimizedImage
            src={getProductImage()}
            alt={getProductTitle()}
            fill
            className="w-full h-full object-cover transition-all duration-300 group-hover:scale-105"
            fallbackSrc={product.type === 'tour' 
              ? '/images/tour-image.jpg' 
              : '/images/event-image.jpg'
            }
            sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
            priority={false}
          />
          
          {/* Modern Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300" />
          
          {/* Top Badges */}
          <div className="absolute top-2 left-2 z-20 flex flex-col gap-1">
            {product.type === 'tour' ? (
              (product as TourProduct).category || (product as TourProduct).category_name ? (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-white/20 backdrop-blur-md text-white shadow-md border border-white/30">
                  <MapPin className="h-2.5 w-2.5 mr-1" />
                  {(() => {
                    const tour = product as TourProduct;
                    const category = tour.category;
                    if (typeof category === 'string') {
                      return category;
                    } else if (category && typeof category === 'object') {
                      return category.name;
                    } else if (tour.category_name) {
                      return tour.category_name;
                    }
                    return 'Category';
                  })()}
                </span>
              ) : null
            ) : (
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStyleColor((product as EventProduct).style || 'music')} shadow-md`}>
                {getStyleIcon((product as EventProduct).style || 'music')}
                <span className="ml-1">{(product as EventProduct).style || 'Event'}</span>
              </span>
            )}
          </div>
          
          {/* Price Badge on Image */}
          <div className="absolute bottom-3 right-3 z-20">
            <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-sm rounded-xl px-3 py-2 shadow-lg border border-white/20 dark:border-gray-700/20">
              <div className="text-sm font-bold text-primary-600 dark:text-primary-400">
                {getProductPrice()}
              </div>
            </div>
          </div>
        </div>

        {/* Content Section */}
        <CardContent className="p-4 flex flex-col h-full relative z-10">
          <div className="flex-1">
            <h3 className={`text-base font-bold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-300 line-clamp-2 mb-2 ${isRTL ? 'text-right' : 'text-left'}`}>
              {getProductTitle()}
            </h3>
            
            <p className={`text-gray-600 dark:text-gray-300 text-xs mb-3 line-clamp-2 ${isRTL ? 'text-right' : 'text-left'}`}>
              {getProductDescription()}
            </p>

            {/* Rating & Reviews */}
            <div className="flex items-center gap-2 mb-3">
              <div className="flex items-center">
                {renderStars(product.rating || 0)}
                <span className="ml-1 text-xs font-medium text-gray-600 dark:text-gray-400">
                  {product.rating ? product.rating.toFixed(1) : '0.0'}
                </span>
              </div>
              {product.review_count && (
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  ({product.review_count})
                </span>
              )}
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-1 gap-2 mb-3">
              <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                {product.type === 'tour' ? (
                  <>
                    <Clock className="h-3.5 w-3.5 text-blue-500" />
                    <span className="font-medium">{(product as TourProduct).duration_hours} {t('hours')}</span>
                  </>
                ) : (
                  <>
                    <Calendar className="h-3.5 w-3.5 text-purple-500" />
                    <span className="font-medium">
                      {(product as EventProduct).performances && (product as EventProduct).performances![0] ? 
                        (formatDate ? formatDate((product as EventProduct).performances![0].date) : new Date((product as EventProduct).performances![0].date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })) : 
                        'Date TBD'
                      }
                    </span>
                  </>
                )}
              </div>
              
              {product.type === 'tour' ? (
                <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                  <Users className="h-3.5 w-3.5 text-green-500" />
                  <span>
                    {(product as TourProduct).min_participants && (product as TourProduct).max_participants ? 
                                      `${(product as TourProduct).min_participants}-${(product as TourProduct).max_participants} ${t('people')}` :
                (product as TourProduct).max_participants ? `${t('max')} ${(product as TourProduct).max_participants} ${t('people')}` : t('unlimited')
                    }
                  </span>
                </div>
              ) : (
                (product as EventProduct).venue && (
                  <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                    <MapPin className="h-3.5 w-3.5 text-red-500" />
                    <span className="truncate">{(product as EventProduct).venue!.name}</span>
                  </div>
                )
              )}
            </div>
          </div>
          
          {/* Action Button */}
          <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {product.type === 'tour' ? (
                (() => {
                  const tour = product as TourProduct;
                  if (typeof tour.next_schedule_capacity_available === 'number' && typeof tour.next_schedule_capacity_total === 'number') {
                    return tour.next_schedule_capacity_available > 0 ? 
                      `${tour.next_schedule_capacity_available} of ${tour.next_schedule_capacity_total} Available` : 
                      'Sold Out';
                  }
                  return tour.next_schedule_capacity_available === 0 ? 'Sold Out' : 'Available';
                })()
              ) : (
                ((product as EventProduct).is_active ? 'Active' : 'Inactive')
              )}
            </div>
            <div className="flex items-center text-blue-600 dark:text-blue-400 font-medium group-hover:gap-1 transition-all duration-300">
              <span className="text-xs">View Details</span>
              <ArrowRight className="h-3 w-3 ml-1 group-hover:translate-x-0.5 transition-transform duration-300" />
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}