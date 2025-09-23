'use client';

import { useState, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { Calendar, Clock, Users, Star, AlertCircle, CheckCircle2, TrendingUp } from 'lucide-react';
import { EventPerformance } from '@/lib/types/api';

interface PerformanceSelectorProps {
  performances: EventPerformance[];
  selectedPerformance: EventPerformance | null;
  onPerformanceSelect: (performance: EventPerformance) => void;
  formatDate: (date: string) => string;
  formatTime: (time: string) => string;
  formatPrice: (price: number, currency: string) => string;
}

export default function PerformanceSelector({
  performances,
  selectedPerformance,
  onPerformanceSelect,
  formatDate,
  formatTime,
  formatPrice
}: PerformanceSelectorProps) {
  const t = useTranslations('eventDetail');
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');

  const getAvailabilityStatus = useCallback((performance: EventPerformance) => {
    const occupancyRate = ((performance.max_capacity - performance.available_capacity) / performance.max_capacity) * 100;
    
    if (occupancyRate >= 95) return 'sold_out';
    if (occupancyRate >= 80) return 'few_left';
    if (occupancyRate >= 50) return 'filling_up';
    return 'available';
  }, []);

  const getStatusColor = useCallback((status: string) => {
    switch (status) {
      case 'sold_out': return 'bg-red-100 text-red-800 border-red-200';
      case 'few_left': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'filling_up': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-green-100 text-green-800 border-green-200';
    }
  }, []);

  const getStatusIcon = useCallback((status: string) => {
    switch (status) {
      case 'sold_out': return <AlertCircle className="h-4 w-4" />;
      case 'few_left': return <TrendingUp className="h-4 w-4" />;
      case 'filling_up': return <Users className="h-4 w-4" />;
      default: return <CheckCircle2 className="h-4 w-4" />;
    }
  }, []);

  const getStatusText = useCallback((status: string) => {
    switch (status) {
      case 'sold_out': return t('soldOut');
      case 'few_left': return t('fewTicketsLeft');
      case 'filling_up': return t('fillingUp');
      default: return t('available');
    }
  }, [t]);

  const isPerformanceSelectable = useCallback((performance: EventPerformance) => {
    return performance.is_available && performance.available_capacity > 0;
  }, []);

  // Group performances by date for calendar view
  const performancesByDate = performances.reduce((acc, performance) => {
    const date = performance.date;
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(performance);
    return acc;
  }, {} as Record<string, EventPerformance[]>);

  if (performances.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8 text-center">
        <Calendar className="h-12 w-12 text-gray-300 dark:text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">{t('noPerformancesAvailable')}</h3>
        <p className="text-gray-600 dark:text-gray-400">{t('checkBackLater')}</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-2">
              {t('selectPerformance')}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {performances.length} {t('performancesAvailable')}
            </p>
          </div>
          
          {/* View Mode Toggle */}
          <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'list'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
            >
              {t('listView')}
            </button>
            <button
              onClick={() => setViewMode('calendar')}
              className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'calendar'
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
            >
              {t('calendarView')}
            </button>
          </div>
        </div>
      </div>

      {/* Performance List */}
      <div className="p-6">
        {viewMode === 'list' ? (
          <div className="space-y-4">
            {performances.map((performance) => {
              const status = getAvailabilityStatus(performance);
              const isSelectable = isPerformanceSelectable(performance);
              const isSelected = selectedPerformance?.id === performance.id;
              // Use backend-provided min_price
              const minPrice = performance.min_price ?? 0;

              return (
                <div
                  key={performance.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${
                    isSelected 
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 ring-2 ring-blue-200 dark:ring-blue-400' 
                      : isSelectable 
                        ? 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 hover:shadow-md' 
                        : 'border-gray-200 dark:border-gray-600 opacity-60 cursor-not-allowed'
                  }`}
                  onClick={() => isSelectable && onPerformanceSelect(performance)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-3">
                        <div className="flex items-center text-gray-900 dark:text-gray-100">
                          <Calendar className="h-5 w-5 mr-2" />
                          <span className="font-medium">
                            {formatDate(performance.date)}
                          </span>
                        </div>
                        
                        <div className="flex items-center text-gray-600 dark:text-gray-400">
                          <Clock className="h-4 w-4 mr-1" />
                          <span>{formatTime(performance.start_time)}</span>
                        </div>

                        {performance.is_special && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            <Star className="h-3 w-3 mr-1" />
                            {t('specialPerformance')}
                          </span>
                        )}
                      </div>

                                             <div className="flex items-center space-x-6 text-sm text-gray-600 dark:text-gray-400">
                         <div className="flex items-center">
                           <Users className="h-4 w-4 mr-1" />
                           <span>
                             {performance.available_capacity.toLocaleString()} / {performance.max_capacity.toLocaleString()} {t('available')}
                           </span>
                         </div>
                         
                         <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(status)}`}>
                           {getStatusIcon(status)}
                           <span className="ml-1">{getStatusText(status)}</span>
                         </div>
                       </div>
                    </div>

                                         <div className="text-right ml-4">
                       <div className="text-lg font-bold text-gray-900 dark:text-gray-100">
                         {formatPrice(minPrice, 'USD')}
                       </div>
                       <div className="text-sm text-gray-500 dark:text-gray-400">{t('fromPrice')}</div>
                     </div>
                  </div>

                                     {/* Progress Bar */}
                   <div className="mt-3">
                     <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                       <span>{t('capacity')}</span>
                       <span>
                         {((performance.max_capacity - performance.available_capacity) / performance.max_capacity * 100).toFixed(0)}% {t('sold')}
                       </span>
                     </div>
                     <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                       <div
                         className={`h-2 rounded-full transition-all ${
                           status === 'sold_out' ? 'bg-red-500' :
                           status === 'few_left' ? 'bg-orange-500' :
                           status === 'filling_up' ? 'bg-yellow-500' : 'bg-green-500'
                         }`}
                         style={{
                           width: `${((performance.max_capacity - performance.available_capacity) / performance.max_capacity) * 100}%`
                         }}
                       />
                     </div>
                   </div>
                </div>
              );
            })}
          </div>
        ) : (
          /* Calendar View */
                     <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
             {Object.entries(performancesByDate).map(([date, dayPerformances]) => (
               <div key={date} className="border border-gray-200 dark:border-gray-600 rounded-lg overflow-hidden">
                 <div className="bg-gray-50 dark:bg-gray-700 px-4 py-3 border-b border-gray-200 dark:border-gray-600">
                   <h3 className="font-medium text-gray-900 dark:text-gray-100">
                     {formatDate(date)}
                   </h3>
                 </div>
                 
                 <div className="p-4 space-y-3">
                   {dayPerformances.map((performance) => {
                     const status = getAvailabilityStatus(performance);
                     const isSelectable = isPerformanceSelectable(performance);
                     const isSelected = selectedPerformance?.id === performance.id;
                     // Use backend-provided min_price
                     const minPrice = performance.min_price ?? 0;

                     return (
                       <div
                         key={performance.id}
                         className={`p-3 rounded-lg border cursor-pointer transition-all ${
                           isSelected 
                             ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                             : isSelectable 
                               ? 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500' 
                               : 'border-gray-200 dark:border-gray-600 opacity-60 cursor-not-allowed'
                         }`}
                         onClick={() => isSelectable && onPerformanceSelect(performance)}
                       >
                         <div className="flex items-center justify-between mb-2">
                           <div className="flex items-center text-sm font-medium text-gray-900 dark:text-gray-100">
                             <Clock className="h-4 w-4 mr-1" />
                             {formatTime(performance.start_time)}
                           </div>
                           
                           {performance.is_special && (
                             <Star className="h-4 w-4 text-purple-500" />
                           )}
                         </div>
                         
                         <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-2">
                           <span>{performance.available_capacity} {t('available')}</span>
                           <span className="font-medium">{formatPrice(minPrice, 'USD')}</span>
                         </div>
                         
                         <div className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getStatusColor(status)}`}>
                           {getStatusIcon(status)}
                           <span className="ml-1">{getStatusText(status)}</span>
                         </div>
                       </div>
                     );
                   })}
                 </div>
               </div>
             ))}
           </div>
        )}
      </div>
    </div>
  );
} 