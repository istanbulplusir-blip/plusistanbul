'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import { Car, Users, Settings, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import OptimizedImage from '@/components/common/OptimizedImage';
import { CarRental } from '@/lib/api/car-rentals';

interface VehicleSelectionStepProps {
  carRental: CarRental;
  onNext: () => void;
  onBack?: () => void;
  isLoading?: boolean;
  bookingInfo?: {
    pickup_date: string;
    dropoff_date: string;
    pickup_time: string;
    dropoff_time: string;
    pickup_location: string;
    dropoff_location: string;
    rental_type: 'hourly' | 'daily' | null;
    rental_days: number;
    rental_hours: number;
    total_hours: number;
  };
}

export default function VehicleSelectionStep({
  carRental,
  onNext,
  onBack,
  isLoading = false,
  bookingInfo
}: VehicleSelectionStepProps) {
  const t = useTranslations('carRentalBooking');

  const getFuelIcon = (fuelType: string) => {
    switch (fuelType) {
      case 'gasoline': return '⛽';
      case 'diesel': return '🚛';
      case 'hybrid': return '🔋';
      case 'electric': return '⚡';
      case 'lpg': return '🔥';
      default: return '⛽';
    }
  };


  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {t('confirmVehicle')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {t('confirmVehicleDesc')}
        </p>
      </div>

      <Card className="overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-2">
          {/* Vehicle Image */}
          <div className="relative h-64 lg:h-80">
            <OptimizedImage
              src={carRental.image_url || carRental.image || '/images/placeholder-car.jpg'}
              alt={carRental.title}
              fill
              className="w-full h-full object-cover"
              fallbackSrc="/images/placeholder-car.jpg"
            />
            <div className="absolute top-4 left-4">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-white/90 dark:bg-gray-800/90 text-gray-700 dark:text-gray-300 backdrop-blur-sm">
                {carRental.category.name}
              </span>
            </div>
          </div>

          {/* Vehicle Details */}
          <div className="p-6">
            <div className="mb-6">
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {carRental.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {carRental.short_description}
              </p>
              
              {/* Booking Summary */}
              {bookingInfo && (
                <Card className="mb-6 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
                  <div className="p-4">
                    <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-200 mb-3 flex items-center">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      {t('bookingSummary')}
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">{t('pickupDate')}:</span>
                        <span className="ml-2 font-medium">{bookingInfo.pickup_date}</span>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">{t('pickupTime')}:</span>
                        <span className="ml-2 font-medium">{bookingInfo.pickup_time}</span>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">{t('dropoffDate')}:</span>
                        <span className="ml-2 font-medium">{bookingInfo.dropoff_date}</span>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">{t('dropoffTime')}:</span>
                        <span className="ml-2 font-medium">{bookingInfo.dropoff_time}</span>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">{t('pickupLocation')}:</span>
                        <span className="ml-2 font-medium">{bookingInfo.pickup_location}</span>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">{t('dropoffLocation')}:</span>
                        <span className="ml-2 font-medium">{bookingInfo.dropoff_location}</span>
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-blue-200 dark:border-blue-700">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600 dark:text-gray-400">{t('rentalDuration')}:</span>
                        <span className="font-semibold text-blue-800 dark:text-blue-200">
                          {bookingInfo.rental_type === 'hourly' ? (
                            `${bookingInfo.rental_hours} ${t('hours')}`
                          ) : (
                            `${bookingInfo.rental_days} ${t('days')}`
                          )}
                        </span>
                      </div>
                    </div>
                  </div>
                </Card>
              )}
              
              {/* Vehicle Specifications */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="flex items-center space-x-2">
                  <Car className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  <div>
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {carRental.year} {carRental.brand} {carRental.model}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">Year & Model</div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Users className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  <div>
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {carRental.seats} {t('seats')}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">Capacity</div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getFuelIcon(carRental.fuel_type)}</span>
                  <div>
                    <div className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                      {carRental.fuel_type}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">Fuel Type</div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Settings className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  <div>
                    <div className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                      {carRental.transmission}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">Transmission</div>
                  </div>
                </div>
              </div>

              {/* Pricing */}
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {t('dailyRate')}
                  </span>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {formatPrice(parseFloat(carRental.price_per_day), carRental.currency)}
                  </span>
                </div>
                {carRental.price_per_hour && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {t('hourlyRate')}
                    </span>
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {formatPrice(parseFloat(carRental.price_per_hour), carRental.currency)}
                    </span>
                  </div>
                )}
                {carRental.pricing_summary && (carRental.pricing_summary.weekly_discount > 0 || carRental.pricing_summary.monthly_discount > 0) && (
                  <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                    <div className="text-xs text-green-600 dark:text-green-400">
                      {carRental.pricing_summary.weekly_discount > 0 && (
                        <div>{t('weeklyDiscount')}: -{carRental.pricing_summary.weekly_discount}%</div>
                      )}
                      {carRental.pricing_summary.monthly_discount > 0 && (
                        <div>{t('monthlyDiscount')}: -{carRental.pricing_summary.monthly_discount}%</div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Features */}
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  {t('includedFeatures')}
                </h4>
                <div className="flex flex-wrap gap-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    {t('basicInsurance')}
                  </span>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    {t('unlimitedMileage')}
                  </span>
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    {t('roadsideAssistance')}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-between pt-6">
        {onBack && (
          <Button
            variant="outline"
            onClick={onBack}
            disabled={isLoading}
          >
            {t('back')}
          </Button>
        )}
        
        <Button
          onClick={onNext}
          disabled={isLoading}
          className="ml-auto"
        >
          {isLoading ? t('loading') : t('next')}
        </Button>
      </div>
    </motion.div>
  );
}
