'use client';

import React, { useState } from 'react';
import { ShieldOff, TrendingDown, AlertCircle, Info, Clock, MapPin, Calendar } from 'lucide-react';
import { useTranslations } from 'next-intl';

export type ProductType = 'tour' | 'event' | 'transfer' | 'car_rental';

export interface CancellationPolicy {
  hours_before: number;
  refund_percentage: number;
  description?: string;
}

interface ProductCancellationPolicyProps {
  policies: CancellationPolicy[];
  productType: ProductType;
  productData?: {
    title?: string;
    date?: string;
    time?: string;
    location?: string;
    duration?: string;
    venue?: string;
  };
  showDetails?: boolean;
  onToggleDetails?: () => void;
  className?: string;
}

export default function ProductCancellationPolicy({
  policies,
  productType,
  productData,
  showDetails = false,
  onToggleDetails,
  className = ''
}: ProductCancellationPolicyProps) {
  const t = useTranslations('cancellationPolicy');
  const [expanded, setExpanded] = useState(false);

  // Product-specific configurations
  const productConfig = {
    tour: {
      icon: MapPin,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      timeLabel: t('beforeTourStart'),
      contextInfo: productData?.date ? t('tourDate', { date: new Date(productData.date).toLocaleDateString('fa-IR') }) : undefined
    },
    event: {
      icon: Calendar,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      timeLabel: t('beforeEvent'),
      contextInfo: productData?.venue ? t('eventVenue', { venue: productData.venue }) : undefined
    },
    transfer: {
      icon: Clock,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      timeLabel: t('beforeService'),
      contextInfo: productData?.duration ? t('transferDuration', { duration: productData.duration }) : undefined
    },
    car_rental: {
      icon: Calendar,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      timeLabel: t('beforeService'),
      contextInfo: productData?.duration ? t('rentalDuration', { duration: productData.duration }) : undefined
    }
  };

  const config = productConfig[productType];
  const IconComponent = config.icon;

  if (!policies || policies.length === 0) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 ${className}`}>
        <div className="flex items-center text-yellow-600 dark:text-yellow-500 mb-2">
          <AlertCircle className="h-5 w-5 mr-2" />
          <h3 className="text-lg font-semibold">
            {t(`${productType}Title`)}
          </h3>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {t(`${productType}NoPolicy`)}
        </p>
      </div>
    );
  }

  // Sort policies by hours_before (most flexible first)
  const sortedPolicies = [...policies].sort((a, b) => b.hours_before - a.hours_before);

  // Get the most flexible policy for summary
  const mostFlexiblePolicy = sortedPolicies[0];

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header */}
      <div className={`p-4 border-b border-gray-200/50 dark:border-gray-700/50 ${config.bgColor}/50 dark:bg-gray-700/50  rounded-t-lg`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <IconComponent className={`h-5 w-5 mr-2 ${config.color}`} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {t(`${productType}Title`)}
            </h3>
          </div>
          
          {onToggleDetails && (
            <button
              onClick={onToggleDetails}
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium"
            >
              {showDetails ? t('hideDetails') : t('showDetails')}
            </button>
          )}
        </div>

        {/* Product Context Info */}
        {config.contextInfo && (
          <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {config.contextInfo}
          </div>
        )}
      </div>

      <div className="p-4">
        {/* Policy Summary Toggle */}
        <button
          type="button"
          onClick={() => setExpanded(!expanded)}
          className="flex items-center justify-between w-full text-left"
        >
          <div className="flex items-center">
            <ShieldOff className="h-5 w-5 text-gray-600 dark:text-gray-400 mr-2" />
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {mostFlexiblePolicy.refund_percentage === 100 ? t('freeCancellation') : t('conditionalCancellation')}
            </span>
            <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
              ({policies.length} {t('rules', { count: policies.length })})
            </span>
          </div>
          <div className="flex items-center">
            <TrendingDown 
              className={`h-4 w-4 text-gray-400 transition-transform ${
                expanded ? 'rotate-180' : ''
              }`}
            />
          </div>
        </button>
            
        {expanded && (
          <div className="mt-4 space-y-4">
            {sortedPolicies.map((policy, index) => (
              <div key={index} className="border-t pt-4 first:border-t-0 first:pt-0">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100">
                      {policy.hours_before === 0 ? t('sameDay') : 
                       policy.hours_before < 24 ? t('hoursBeforeService', { hours: policy.hours_before, timeLabel: config.timeLabel }) :
                       t('daysBeforeService', { days: Math.floor(policy.hours_before / 24), timeLabel: config.timeLabel })}
                    </h4>
                    {policy.description && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {policy.description}
                      </p>
                    )}
                  </div>
                  <div className="ml-4">
                    <span className={`font-medium px-3 py-1 rounded-full text-sm ${
                      policy.refund_percentage === 0 
                        ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        : policy.refund_percentage === 100
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    }`}>
                      {policy.refund_percentage === 0 ? t('noRefund') :
                       policy.refund_percentage === 100 ? t('fullRefund') :
                       t('partialRefund', { percentage: policy.refund_percentage })}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Quick Info */}
        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="flex items-start">
            <Info className="h-4 w-4 text-gray-500 dark:text-gray-400 mr-2 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-gray-600 dark:text-gray-400">
              <p className="font-medium mb-1">
                {t(`${productType}ImportantNotes`)}
              </p>
              <ul className="space-y-1 text-xs">
                <li>• {t('note1')}</li>
                <li>• {t('note2')}</li>
                <li>• {t('note3')}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
