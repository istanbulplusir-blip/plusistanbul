'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  MapPin, 
  User, 
  Car, 
  Shield, 
  CheckCircle,
  CreditCard,
  FileText
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { CarRental } from '@/lib/api/car-rentals';

interface SelectedOption {
  id: string;
  quantity: number;
  name?: string;
  price?: string | number;
  description?: string;
}

interface DriverInfo {
  driver_name: string;
  driver_license: string;
  driver_phone: string;
  driver_email: string;
  additional_drivers: Array<{
    name: string;
    license: string;
    phone: string;
  }>;
}

interface BookingSummaryStepProps {
  carRental: CarRental;
  pickupDate: string;
  dropoffDate: string;
  pickupTime: string;
  dropoffTime: string;
  pickupLocation: string;
  dropoffLocation: string;
  driverInfo: DriverInfo;
  selectedOptions: SelectedOption[];
  basicInsurance: boolean;
  comprehensiveInsurance: boolean;
  specialRequirements: string;
  pricingBreakdown: {
    base_price: number;
    daily_rate: number;
    hourly_rate: number;
    weekly_discount: number;
    monthly_discount: number;
    options_total: number;
    insurance_total: number;
    final_price: number;
    rental_type: 'hourly' | 'daily' | null;
    rental_days: number;
    rental_hours: number;
    total_hours: number;
  } | null;
  currency: string;
  onConfirm: () => void;
  onBack?: () => void;
  isLoading?: boolean;
}

export default function BookingSummaryStep({
  carRental,
  pickupDate,
  dropoffDate,
  pickupTime,
  dropoffTime,
  pickupLocation,
  dropoffLocation,
  driverInfo,
  selectedOptions,
  basicInsurance,
  comprehensiveInsurance,
  specialRequirements,
  pricingBreakdown,
  currency,
  onConfirm,
  onBack,
  isLoading = false
}: BookingSummaryStepProps) {
  const t = useTranslations('carRentalBooking');

  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatTime = (timeString: string) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // const rentalDays = Math.ceil((new Date(dropoffDate).getTime() - new Date(pickupDate).getTime()) / (1000 * 60 * 60 * 24));

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
          {t('reviewBooking')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {t('reviewBookingDesc')}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Booking Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Vehicle Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Car className="w-5 h-5 mr-2 text-blue-600" />
                {t('vehicleInformation')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-start space-x-4">
                <div className="w-20 h-20 bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                  <Car className="w-8 h-8 text-gray-600 dark:text-gray-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {carRental.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-2">
                    {carRental.year} {carRental.brand} {carRental.model}
                  </p>
                  <div className="flex flex-wrap gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <span>{carRental.seats} {t('seats')}</span>
                    <span>•</span>
                    <span className="capitalize">{carRental.fuel_type}</span>
                    <span>•</span>
                    <span className="capitalize">{carRental.transmission}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Rental Period */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="w-5 h-5 mr-2 text-green-600" />
                {t('rentalPeriod')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="flex items-center mb-2">
                    <MapPin className="w-4 h-4 text-blue-600 mr-2" />
                    <span className="font-medium text-gray-900 dark:text-white">
                      {t('pickup')}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    <div>{formatDate(pickupDate)}</div>
                    <div>{formatTime(pickupTime)}</div>
                    <div className="mt-1">{pickupLocation}</div>
                  </div>
                </div>
                <div>
                  <div className="flex items-center mb-2">
                    <MapPin className="w-4 h-4 text-red-600 mr-2" />
                    <span className="font-medium text-gray-900 dark:text-white">
                      {t('dropoff')}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    <div>{formatDate(dropoffDate)}</div>
                    <div>{formatTime(dropoffTime)}</div>
                    <div className="mt-1">{dropoffLocation}</div>
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('rentalDuration')}
                  </span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {pricingBreakdown?.rental_type === 'hourly' ? (
                      <>
                        {pricingBreakdown.rental_hours} {t('hours')}
                        {pricingBreakdown.total_hours > pricingBreakdown.rental_hours && (
                          <span className="text-xs text-gray-500 ml-1">
                            ({pricingBreakdown.total_hours.toFixed(1)} {t('totalHours')})
                          </span>
                        )}
                      </>
                    ) : (
                      <>
                        {pricingBreakdown?.rental_days || 0} {t('days')}
                        {pricingBreakdown?.rental_hours && pricingBreakdown.rental_hours > 0 && (
                          <span className="text-xs text-gray-500 ml-1">
                            + {pricingBreakdown.rental_hours} {t('hours')}
                          </span>
                        )}
                      </>
                    )}
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {pricingBreakdown?.rental_type === 'hourly' ? t('hourlyRental') : t('dailyRental')}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Driver Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <User className="w-5 h-5 mr-2 text-purple-600" />
                {t('driverInformation')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {t('mainDriver')}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    <div>{driverInfo.driver_name}</div>
                    <div>{driverInfo.driver_phone}</div>
                    <div>{driverInfo.driver_email}</div>
                    <div className="mt-1 text-xs">
                      {t('license')}: {driverInfo.driver_license}
                    </div>
                  </div>
                </div>

                {driverInfo.additional_drivers.length > 0 && (
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white mb-2">
                      {t('additionalDrivers')} ({driverInfo.additional_drivers.length})
                    </div>
                    <div className="space-y-2">
                      {driverInfo.additional_drivers.map((driver, index) => (
                        <div key={index} className="text-sm text-gray-600 dark:text-gray-400">
                          <div>{driver.name}</div>
                          <div className="text-xs">
                            {t('license')}: {driver.license} • {driver.phone}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Selected Options */}
          {selectedOptions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CheckCircle className="w-5 h-5 mr-2 text-orange-600" />
                  {t('selectedOptions')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {selectedOptions.map((option) => (
                    <div key={option.id} className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">
                        {option.name} x{option.quantity}
                      </span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {formatPrice(typeof option.price === 'string' ? parseFloat(option.price) : option.price || 0, currency)}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Insurance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="w-5 h-5 mr-2 text-indigo-600" />
                {t('insurance')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('basicInsurance')}
                  </span>
                  <span className="text-green-600 font-medium">
                    {basicInsurance ? t('included') : t('notSelected')}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">
                    {t('comprehensiveInsurance')}
                  </span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {comprehensiveInsurance ? t('selected') : t('notSelected')}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Special Requirements */}
          {specialRequirements && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-gray-600" />
                  {t('specialRequirements')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {specialRequirements}
                </p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Pricing Summary */}
        <div className="lg:col-span-1">
          <Card className="sticky top-8">
            <CardHeader>
              <CardTitle className="flex items-center">
                <CreditCard className="w-5 h-5 mr-2 text-green-600" />
                {t('pricingSummary')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {pricingBreakdown ? (
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">
                      {pricingBreakdown.rental_type === 'hourly' ? (
                        <>
                          {t('basePrice')} ({pricingBreakdown.rental_hours} {t('hours')})
                        </>
                      ) : (
                        <>
                          {t('basePrice')} ({pricingBreakdown.rental_days} {t('days')})
                        </>
                      )}
                    </span>
                    <span className="text-gray-900 dark:text-white font-medium">
                      {formatPrice(pricingBreakdown.base_price, currency)}
                    </span>
                  </div>

                  {pricingBreakdown.options_total > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">
                        {t('options')}
                      </span>
                      <span className="text-gray-900 dark:text-white">
                        {formatPrice(pricingBreakdown.options_total, currency)}
                      </span>
                    </div>
                  )}

                  {pricingBreakdown.insurance_total > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">
                        {t('insurance')}
                      </span>
                      <span className="text-gray-900 dark:text-white">
                        {formatPrice(pricingBreakdown.insurance_total, currency)}
                      </span>
                    </div>
                  )}

                  {(pricingBreakdown.weekly_discount > 0 || pricingBreakdown.monthly_discount > 0) && (
                    <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                      {pricingBreakdown.weekly_discount > 0 && (
                        <div className="flex justify-between text-sm text-green-600">
                          <span>{t('weeklyDiscount')}</span>
                          <span>-{formatPrice(pricingBreakdown.weekly_discount, currency)}</span>
                        </div>
                      )}
                      {pricingBreakdown.monthly_discount > 0 && (
                        <div className="flex justify-between text-sm text-green-600">
                          <span>{t('monthlyDiscount')}</span>
                          <span>-{formatPrice(pricingBreakdown.monthly_discount, currency)}</span>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex justify-between text-lg font-bold">
                      <span>{t('total')}</span>
                      <span className="text-green-600">
                        {formatPrice(pricingBreakdown.final_price, currency)}
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  {t('calculatingPrice')}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

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
          onClick={onConfirm}
          disabled={isLoading || !pricingBreakdown}
          className="ml-auto"
          size="lg"
        >
          {isLoading ? t('processing') : t('confirmBooking')}
        </Button>
      </div>
    </motion.div>
  );
}
