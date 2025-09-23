'use client';

import { useState, useCallback } from 'react';
import { Clock, MapPin, Route, List, Image as ImageIcon, FileText, CheckCircle, Info, Star } from 'lucide-react';
import { useTranslations } from 'next-intl';
import OptimizedImage from '@/components/common/OptimizedImage';
import { getImageUrl } from '@/lib/utils';

interface TourItineraryItem {
  id: string;
  title: string;
  description: string;
  order: number;
  duration_minutes: number;
  location: string;
  image?: string;
}

interface TourItineraryProps {
  itinerary: TourItineraryItem[];
  rules?: string;
  required_items?: string;
  highlights?: string;
  booking_cutoff_hours?: number;
  min_participants?: number;
  max_participants?: number;
  tour_type?: string;
  transport_type?: string;
}

export default function TourItinerary({ 
  itinerary, 
  rules, 
  required_items, 
  highlights,
  booking_cutoff_hours,
  min_participants,
  max_participants,
  tour_type,
  transport_type
}: TourItineraryProps) {
  const [viewMode, setViewMode] = useState<'list' | 'highlights' | 'gallery' | 'rules' | 'required' | 'booking'>('list');
  const t = useTranslations('TourDetail');

  const formatDuration = useCallback((minutes: number) => {
    if (minutes < 60) {
      return `${minutes} ${t('minutes')}`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    if (remainingMinutes === 0) {
      return `${hours} ${t('hours')}`;
    }
    return t('hoursAndMinutes', { hours, minutes: remainingMinutes });
  }, [t]);



  if (itinerary.length === 0 && !rules && !required_items && !highlights) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 sm:p-8 text-center">
        <Route className="h-12 w-12 text-gray-300 dark:text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">{t('itineraryNotAvailable')}</h3>
        <p className="text-gray-600 dark:text-gray-400">{t('itineraryNotAvailableDesc')}</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 sm:p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
              {t('itineraryTitle')}
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              {t('stepsInItinerary', { count: itinerary.length })}
            </p>
          </div>
          
          {/* View Mode Toggle - Mobile Optimized */}
          <div className="flex flex-wrap gap-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => setViewMode('list')}
              className={`px-2 sm:px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-all duration-200 ${
                viewMode === 'list'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              <List className="h-3 w-3 sm:h-4 sm:w-4 inline mr-1" />
              <span className="hidden sm:inline">{t('listView')}</span>
              <span className="sm:hidden">List</span>
            </button>
            <button
              onClick={() => setViewMode('highlights')}
              className={`px-2 sm:px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-all duration-200 ${
                viewMode === 'highlights'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              <Star className="h-3 w-3 sm:h-4 sm:w-4 inline mr-1" />
              <span className="hidden sm:inline">{t('highlights')}</span>
              <span className="sm:hidden">Highlights</span>
            </button>
            <button
              onClick={() => setViewMode('gallery')}
              className={`px-2 sm:px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-all duration-200 ${
                viewMode === 'gallery'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              <ImageIcon className="h-3 w-3 sm:h-4 sm:w-4 inline mr-1" />
              <span className="hidden sm:inline">{t('galleryView')}</span>
              <span className="sm:hidden">Gallery</span>
            </button>
            <button
              onClick={() => setViewMode('rules')}
              className={`px-2 sm:px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-all duration-200 ${
                viewMode === 'rules'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              <FileText className="h-3 w-3 sm:h-4 sm:w-4 inline mr-1" />
              <span className="hidden sm:inline">{t('rules')}</span>
              <span className="sm:hidden">Rules</span>
            </button>
            <button
              onClick={() => setViewMode('required')}
              className={`px-2 sm:px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-all duration-200 ${
                viewMode === 'required'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              <CheckCircle className="h-3 w-3 sm:h-4 sm:w-4 inline mr-1" />
              <span className="hidden sm:inline">{t('requiredItems')}</span>
              <span className="sm:hidden">Items</span>
            </button>
            <button
              onClick={() => setViewMode('booking')}
              className={`px-2 sm:px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium transition-all duration-200 ${
                viewMode === 'booking'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              <Info className="h-3 w-3 sm:h-4 sm:w-4 inline mr-1" />
              <span className="hidden sm:inline">{t('bookingInformation')}</span>
              <span className="sm:hidden">Info</span>
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 sm:p-6">
        {viewMode === 'list' ? (
          /* List View - Mobile Optimized */
          <div className="space-y-4">
            {itinerary.map((item) => (
              <div
                key={item.id}
                className="border border-gray-200 dark:border-gray-600 rounded-xl p-4 hover:shadow-md transition-all duration-200 bg-gray-50/50 dark:bg-gray-700/50"
              >
                <div className="flex flex-col sm:flex-row sm:items-start gap-4">
                  {/* Order Number */}
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-full flex items-center justify-center text-sm font-semibold">
                      {item.order}
                    </div>
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 mb-3">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {item.title}
                      </h3>
                      
                      <div className="flex items-center text-gray-600 dark:text-gray-400">
                        <Clock className="h-4 w-4 mr-1" />
                        <span className="text-sm">{formatDuration(item.duration_minutes)}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center text-gray-600 dark:text-gray-400 mb-3">
                      <MapPin className="h-4 w-4 mr-1" />
                      <span className="text-sm">{item.location}</span>
                    </div>
                    
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-sm sm:text-base">
                      {item.description}
                    </p>
                  </div>
                  
                  {/* Image */}
                  {item.image && (
                    <div className="flex-shrink-0">
                      <OptimizedImage
                        src={getImageUrl(item.image)}
                        alt={item.title}
                        width={80}
                        height={80}
                        className="w-16 h-16 sm:w-20 sm:h-20 object-cover rounded-lg"
                        fallbackSrc="/images/tour-image.jpg"
                      />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : viewMode === 'highlights' ? (
          /* Highlights View - Mobile Optimized */
          <div className="space-y-6">
            <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-xl p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-4 flex items-center">
                <Star className="h-5 w-5 mr-2" />
                {t('highlights')}
              </h3>
              
              {highlights ? (
                <div className="prose prose-yellow dark:prose-invert max-w-none">
                  <div className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap text-sm sm:text-base">
                    {highlights}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Star className="h-12 w-12 text-gray-300 dark:text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    {t('highlightsNotAvailable')}
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : viewMode === 'gallery' ? (
          /* Gallery View - Mobile Optimized */
          <div>
            {/* Filter items with images */}
            {(() => {
              const itemsWithImages = itinerary.filter(item => item.image);
              
              if (itemsWithImages.length === 0) {
                return (
                  <div className="text-center py-12">
                    <ImageIcon className="h-16 w-16 text-gray-300 dark:text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                      {t('noImagesAvailable')}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      {t('noImagesAvailableDesc')}
                    </p>
                  </div>
                );
              }
              
              return (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                  {itemsWithImages.map((item) => (
                    <div
                      key={item.id}
                      className="group cursor-pointer overflow-hidden rounded-xl border border-gray-200 dark:border-gray-600 hover:shadow-lg transition-all duration-300 bg-white dark:bg-gray-800"
                    >
                      {/* Image */}
                      <div className="aspect-video relative overflow-hidden">
                        <OptimizedImage
                          src={getImageUrl(item.image!)}
                          alt={item.title}
                          width={400}
                          height={225}
                          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                          fallbackSrc="/images/tour-image.jpg"
                        />
                        
                        {/* Overlay */}
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-300 flex items-center justify-center">
                          <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                            <ImageIcon className="h-8 w-8 text-white" />
                          </div>
                        </div>
                        
                        {/* Order Badge */}
                        <div className="absolute top-3 left-3">
                          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-full px-2 py-1 text-xs font-semibold text-gray-900 dark:text-gray-100">
                            {item.order}
                          </div>
                        </div>
                      </div>
                      
                      {/* Content */}
                      <div className="p-4">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2 line-clamp-2">
                          {item.title}
                        </h3>
                        
                        <div className="flex items-center text-gray-600 dark:text-gray-400 mb-2">
                          <MapPin className="h-4 w-4 mr-1" />
                          <span className="text-sm truncate">{item.location}</span>
                        </div>
                        
                        <div className="flex items-center text-gray-600 dark:text-gray-400 mb-3">
                          <Clock className="h-4 w-4 mr-1" />
                          <span className="text-sm">{formatDuration(item.duration_minutes)}</span>
                        </div>
                        
                        <p className="text-gray-700 dark:text-gray-300 text-sm line-clamp-3 leading-relaxed">
                          {item.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              );
            })()}
          </div>
        ) : viewMode === 'rules' ? (
          /* Rules & Regulations View - Mobile Optimized */
          <div className="space-y-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-4 flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                {t('rules')}
              </h3>
              
              {rules ? (
                <div className="prose prose-blue dark:prose-invert max-w-none">
                  <div className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap text-sm sm:text-base">
                    {rules}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-300 dark:text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    {t('rulesNotAvailable')}
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : viewMode === 'required' ? (
          /* Required Items View - Mobile Optimized */
          <div className="space-y-6">
            <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-green-900 dark:text-green-100 mb-4 flex items-center">
                <CheckCircle className="h-5 w-5 mr-2" />
                {t('requiredItems')}
              </h3>
              
              {required_items ? (
                <div className="prose prose-green dark:prose-invert max-w-none">
                  <div className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap text-sm sm:text-base">
                    {required_items}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 text-gray-300 dark:text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    {t('requiredItemsNotAvailable')}
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Booking Information View - Mobile Optimized */
          <div className="space-y-6">
            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 sm:p-6">
              <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-100 mb-4 flex items-center">
                <Info className="h-5 w-5 mr-2" />
                {t('bookingInformation')}
              </h3>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                {/* Tour Type */}
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
                  <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2 text-sm sm:text-base">
                    {t('tourType')}
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
                    {tour_type === 'day' ? t('dailyTour') : t('nightTour')}
                  </p>
                </div>

                {/* Transport Type */}
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
                  <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2 text-sm sm:text-base">
                    {t('transportType')}
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
                    {transport_type === 'boat' ? t('boat') : 
                     transport_type === 'air' ? t('air') : t('ground')}
                  </p>
                </div>

                {/* Booking Cutoff */}
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
                  <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2 text-sm sm:text-base">
                    {t('bookingCutoff')}
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
                    {booking_cutoff_hours ? `${booking_cutoff_hours} ${t('hours')} ${t('beforeTour')}` : t('noCutoffSpecified')}
                  </p>
                </div>

                {/* Participants */}
                <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-600 shadow-sm">
                  <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2 text-sm sm:text-base">
                    {t('participants')}
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400 text-sm sm:text-base">
                    {min_participants && max_participants ? 
                      `${min_participants}-${max_participants} ${t('people')}` :
                      min_participants ? 
                        `${t('minParticipants')}: ${min_participants} ${t('people')}` :
                        max_participants ?
                          `${t('maxParticipants')}: ${max_participants} ${t('people')}` :
                          t('noLimitSpecified')
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
