'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, MapPin } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Checkbox } from '@/components/ui/checkbox';
import { useTranslations } from 'next-intl';
import LocationSelector from './LocationSelector';
import PricingGuide from './PricingGuide';

interface Location {
  id: string;
  name: string;
  description?: string;
  address: string;
  city: string;
  country: string;
  latitude?: number;
  longitude?: number;
  location_type: 'airport' | 'hotel' | 'station' | 'city_center' | 'port' | 'other';
}

interface DateLocationStepProps {
  pickupDate: string | null;
  dropoffDate: string | null;
  pickupTime: string | null;
  dropoffTime: string | null;
  pickupLocation: string;
  dropoffLocation: string;
  onDateChange: (field: 'pickup_date' | 'dropoff_date', value: string) => void;
  onTimeChange: (field: 'pickup_time' | 'dropoff_time', value: string) => void;
  onLocationChange: (field: 'pickup_location' | 'dropoff_location', value: string) => void;
  onNext: () => void;
  onBack?: () => void;
  isLoading?: boolean;
  errors?: {
    pickup_date?: string;
    dropoff_date?: string;
    pickup_time?: string;
    dropoff_time?: string;
    pickup_location?: string;
    dropoff_location?: string;
  };
  defaultPickupLocations?: Location[];
  defaultDropoffLocations?: Location[];
  allowCustomPickupLocation?: boolean;
  allowCustomDropoffLocation?: boolean;
  carRental?: {
    price_per_day: number;
    price_per_hour?: number;
    weekly_discount_percentage: number;
    monthly_discount_percentage: number;
    currency: string;
    min_rent_days: number;
    max_rent_days: number;
    mileage_limit_per_day: number;
    advance_booking_days: number;
    deposit_amount: number;
    allow_hourly_rental?: boolean;
    min_rent_hours?: number;
    max_hourly_rental_hours?: number;
  };
}

export default function DateLocationStep({
  pickupDate,
  dropoffDate,
  pickupTime,
  dropoffTime,
  pickupLocation,
  dropoffLocation,
  onDateChange,
  onTimeChange,
  onLocationChange,
  onNext,
  onBack,
  isLoading = false,
  errors = {},
  defaultPickupLocations = [],
  defaultDropoffLocations = [],
  allowCustomPickupLocation = true,
  allowCustomDropoffLocation = true,
  carRental
}: DateLocationStepProps) {
  const t = useTranslations('carRentalBooking');
  const [sameAsPickup, setSameAsPickup] = useState(false);

  // Update dropoff location when same as pickup is checked
  useEffect(() => {
    if (sameAsPickup && pickupLocation) {
      onLocationChange('dropoff_location', pickupLocation);
    }
  }, [sameAsPickup, pickupLocation, onLocationChange]);

  // Get minimum date (today)
  const getMinDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  // Get minimum dropoff date (pickup date or today)
  const getMinDropoffDate = () => {
    if (pickupDate) {
      return pickupDate;
    }
    return getMinDate();
  };

  // Get minimum pickup time (6 hours from now, but only if pickup date is today)
  const getMinPickupTime = () => {
    const today = new Date().toISOString().split('T')[0];
    if (pickupDate === today) {
      const now = new Date();
      const minTime = new Date(now.getTime() + 6 * 60 * 60 * 1000); // 6 hours from now
      return minTime.toTimeString().slice(0, 5);
    }
    return '00:00'; // No restriction for future dates
  };

  // Get minimum dropoff time (24 hours after pickup)
  const getMinDropoffTime = () => {
    if (pickupDate && pickupTime) {
      const pickupDateTime = new Date(`${pickupDate}T${pickupTime}`);
      const minDropoffDateTime = new Date(pickupDateTime.getTime() + 24 * 60 * 60 * 1000); // 24 hours after pickup
      return minDropoffDateTime.toTimeString().slice(0, 5);
    }
    return '00:00';
  };

  // Calculate rental duration
  const getRentalDuration = () => {
    if (pickupDate && dropoffDate && pickupTime && dropoffTime) {
      const pickup = new Date(`${pickupDate}T${pickupTime}`);
      const dropoff = new Date(`${dropoffDate}T${dropoffTime}`);
      const diffTime = Math.abs(dropoff.getTime() - pickup.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      const diffHours = Math.ceil(diffTime / (1000 * 60 * 60));
      return { days: diffDays, hours: diffHours };
    }
    return { days: 0, hours: 0 };
  };

  // Check if rental is hourly (same day or less than 24 hours)
  const isHourlyRental = () => {
    if (!pickupDate || !dropoffDate || !pickupTime || !dropoffTime) return false;
    
    const pickup = new Date(`${pickupDate}T${pickupTime}`);
    const dropoff = new Date(`${dropoffDate}T${dropoffTime}`);
    const diffTime = Math.abs(dropoff.getTime() - pickup.getTime());
    const diffHours = diffTime / (1000 * 60 * 60);
    
    return diffHours < 24;
  };

  // Check if form is valid
  const isFormValid = () => {
    if (!pickupDate || !dropoffDate || !pickupTime || !dropoffTime || !pickupLocation || !dropoffLocation) {
      return false;
    }

    if (errors.pickup_date || errors.dropoff_date || errors.pickup_time || errors.dropoff_time || errors.pickup_location || errors.dropoff_location) {
      return false;
    }

    // Check hourly rental validation
    if (isHourlyRental()) {
      if (!carRental?.allow_hourly_rental) {
        return false; // Hourly rental not allowed for this car
      }
      
      const duration = getRentalDuration();
      if (duration.hours < (carRental?.min_rent_hours || 2)) {
        return false; // Below minimum hourly rental
      }
      
      if (duration.hours > (carRental?.max_hourly_rental_hours || 8)) {
        return false; // Above maximum hourly rental
      }
    }

    return true;
  };

  // Get validation error message
  const getValidationError = () => {
    if (!pickupDate || !dropoffDate || !pickupTime || !dropoffTime || !pickupLocation || !dropoffLocation) {
      return t('fillAllFields');
    }

    // Check hourly rental validation
    if (isHourlyRental()) {
      if (!carRental?.allow_hourly_rental) {
        return t('hourlyRentalNotAvailable');
      }
      
      const duration = getRentalDuration();
      if (duration.hours < (carRental?.min_rent_hours || 2)) {
        return t('minimumHourlyRentalDuration', { hours: carRental?.min_rent_hours || 2 });
      }
      
      if (duration.hours > (carRental?.max_hourly_rental_hours || 8)) {
        return t('maximumHourlyRentalDuration', { hours: carRental?.max_hourly_rental_hours || 8 });
      }
    }

    return null;
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
          {t('selectDatesAndLocation')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {t('selectDatesAndLocationDesc')}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pickup Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <MapPin className="w-5 h-5 mr-2 text-blue-600" />
              {t('pickupInformation')}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('pickupDate')} *
              </label>
              <Input
                type="date"
                value={pickupDate || ''}
                onChange={(e) => onDateChange('pickup_date', e.target.value)}
                min={getMinDate()}
                className={errors.pickup_date ? 'border-red-500' : ''}
              />
              {errors.pickup_date && (
                <p className="text-red-500 text-sm mt-1">{errors.pickup_date}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('pickupTime')} *
              </label>
              <Input
                type="time"
                value={pickupTime || ''}
                onChange={(e) => onTimeChange('pickup_time', e.target.value)}
                min={getMinPickupTime()}
                className={errors.pickup_time ? 'border-red-500' : ''}
              />
              {errors.pickup_time && (
                <p className="text-red-500 text-sm mt-1">{errors.pickup_time}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('pickupLocation')} *
              </label>
              <LocationSelector
                value={pickupLocation}
                onChange={(location) => onLocationChange('pickup_location', location)}
                placeholder={t('selectPickupLocation')}
                locations={defaultPickupLocations || []}
                allowCustom={allowCustomPickupLocation}
                locationType="pickup"
                error={errors.pickup_location}
              />
            </div>
          </CardContent>
        </Card>

        {/* Dropoff Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <MapPin className="w-5 h-5 mr-2 text-green-600" />
              {t('dropoffInformation')}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('dropoffDate')} *
              </label>
              <Input
                type="date"
                value={dropoffDate || ''}
                onChange={(e) => onDateChange('dropoff_date', e.target.value)}
                min={getMinDropoffDate()}
                className={errors.dropoff_date ? 'border-red-500' : ''}
              />
              {errors.dropoff_date && (
                <p className="text-red-500 text-sm mt-1">{errors.dropoff_date}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('dropoffTime')} *
              </label>
              <Input
                type="time"
                value={dropoffTime || ''}
                onChange={(e) => onTimeChange('dropoff_time', e.target.value)}
                min={getMinDropoffTime()}
                className={errors.dropoff_time ? 'border-red-500' : ''}
              />
              {errors.dropoff_time && (
                <p className="text-red-500 text-sm mt-1">{errors.dropoff_time}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('dropoffLocation')} *
              </label>
              <LocationSelector
                value={dropoffLocation}
                onChange={(location) => onLocationChange('dropoff_location', location)}
                placeholder={t('selectDropoffLocation')}
                locations={defaultDropoffLocations || []}
                allowCustom={allowCustomDropoffLocation}
                locationType="dropoff"
                error={errors.dropoff_location}
              />
            </div>

            {/* Same as pickup location option */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="same-as-pickup"
                checked={sameAsPickup}
                onCheckedChange={(checked) => {
                  setSameAsPickup(checked as boolean);
                  if (checked) {
                    onLocationChange('dropoff_location', pickupLocation);
                  }
                }}
              />
              <label
                htmlFor="same-as-pickup"
                className="text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                {t('sameAsPickupLocation')}
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Pricing Guide */}
        {carRental && (
          <div className="lg:col-span-1">
            <PricingGuide 
              carRental={carRental} 
              rentalDays={getRentalDuration().days}
              rentalHours={getRentalDuration().hours}
              rentalType={isHourlyRental() ? 'hourly' : 'daily'}
            />
          </div>
        )}
      </div>

      {/* Validation Error Message */}
      {getValidationError() && (
        <Card className="bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800">
          <CardContent className="pt-6">
            <div className="flex items-center">
              <div className="w-5 h-5 text-red-600 mr-2">⚠️</div>
              <div className="text-red-800 dark:text-red-200 font-medium">
                {getValidationError()}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Rental Duration Summary */}
      {pickupDate && dropoffDate && pickupTime && dropoffTime && (
        <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Calendar className="w-5 h-5 text-blue-600 mr-2" />
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {t('rentalDuration')}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {isHourlyRental() ? (
                      <>
                        {getRentalDuration().hours} {t('hours')}
                        {carRental?.allow_hourly_rental && (
                          <span className="ml-2 text-green-600 dark:text-green-400">
                            ({t('hourlyRental')})
                          </span>
                        )}
                      </>
                    ) : (
                      <>
                        {getRentalDuration().days} {t('days')}
                        {getRentalDuration().hours > 0 && (
                          <span className="ml-2 text-gray-500">
                            + {getRentalDuration().hours} {t('hours')}
                          </span>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {t('pickup')}: {pickupDate} {pickupTime}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {t('dropoff')}: {dropoffDate} {dropoffTime}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Navigation Buttons */}
      <div className="flex justify-between pt-6">
        {onBack && (
          <Button
            type="button"
            variant="outline"
            onClick={onBack}
            disabled={isLoading}
          >
            {t('back')}
          </Button>
        )}
        
        <Button
          type="button"
          onClick={onNext}
          disabled={!isFormValid() || isLoading}
          className="ml-auto"
        >
          {isLoading ? t('loading') : t('next')}
        </Button>
      </div>
    </motion.div>
  );
}