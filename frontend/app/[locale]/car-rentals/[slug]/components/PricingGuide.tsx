'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Calculator, Clock, Calendar, Percent, DollarSign } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { useTranslations } from 'next-intl';

interface PricingGuideProps {
  carRental: {
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
  rentalDays: number;
  rentalHours?: number;
  rentalType?: 'hourly' | 'daily' | null;
  className?: string;
}

export default function PricingGuide({ carRental, rentalDays, rentalHours = 0, rentalType = null, className = '' }: PricingGuideProps) {
  const t = useTranslations('carRentalBooking');

  // Calculate pricing based on rental duration
  const calculatePricing = () => {
    const { price_per_day, price_per_hour, weekly_discount_percentage, monthly_discount_percentage } = carRental;
    
    let basePrice = 0;
    let discount = 0;
    let discountType = '';
    let pricingType = 'daily';
    
    if (rentalType === 'hourly' && price_per_hour) {
      // Hourly pricing
      basePrice = price_per_hour * rentalHours;
      pricingType = 'hourly';
    } else {
      // Daily pricing
      if (rentalDays >= 30) {
        // Monthly discount
        basePrice = price_per_day * rentalDays;
        discount = (basePrice * monthly_discount_percentage) / 100;
        discountType = 'monthly';
      } else if (rentalDays >= 7) {
        // Weekly discount
        basePrice = price_per_day * rentalDays;
        discount = (basePrice * weekly_discount_percentage) / 100;
        discountType = 'weekly';
      } else {
        // Daily rate
        basePrice = price_per_day * rentalDays;
      }
    }
    
    const finalPrice = basePrice - discount;
    
    return {
      basePrice,
      discount,
      finalPrice,
      discountType,
      pricingType,
      pricePerDay: rentalDays > 0 ? finalPrice / rentalDays : 0,
      pricePerHour: rentalHours > 0 ? finalPrice / rentalHours : 0
    };
  };

  const pricing = calculatePricing();
  const { currency } = carRental;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`space-y-4 ${className}`}
    >
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <CardTitle className="flex items-center text-blue-800 dark:text-blue-200">
            <Calculator className="w-5 h-5 mr-2" />
            {t('pricingGuide')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Current Selection */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center">
                {pricing.pricingType === 'hourly' ? (
                  <Clock className="w-4 h-4 text-gray-500 mr-2" />
                ) : (
                  <Calendar className="w-4 h-4 text-gray-500 mr-2" />
                )}
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {t('selectedDuration')}
                </span>
              </div>
              <Badge variant="outline" className="text-blue-600 border-blue-600">
                {pricing.pricingType === 'hourly' ? (
                  `${rentalHours} ${rentalHours === 1 ? t('hour') : t('hours')}`
                ) : (
                  `${rentalDays} ${rentalDays === 1 ? t('day') : t('days')}`
                )}
              </Badge>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500 dark:text-gray-400">{t('basePrice')}:</span>
                <div className="font-semibold text-gray-900 dark:text-white">
                  {pricing.basePrice.toFixed(2)} {currency}
                </div>
                <div className="text-xs text-gray-400">
                  {pricing.pricingType === 'hourly' ? (
                    `${carRental.price_per_hour?.toFixed(2)} ${currency} × ${rentalHours} ${t('hours')}`
                  ) : (
                    `${carRental.price_per_day.toFixed(2)} ${currency} × ${rentalDays} ${t('days')}`
                  )}
                </div>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">{t('finalPrice')}:</span>
                <div className="font-semibold text-green-600 dark:text-green-400">
                  {pricing.finalPrice.toFixed(2)} {currency}
                </div>
                <div className="text-xs text-gray-400">
                  {pricing.pricingType === 'hourly' ? (
                    `${pricing.pricePerHour.toFixed(2)} ${currency} ${t('perHour')}`
                  ) : (
                    `${pricing.pricePerDay.toFixed(2)} ${currency} ${t('perDay')}`
                  )}
                </div>
              </div>
            </div>
            
            {pricing.discount > 0 && (
              <div className="mt-3 p-2 bg-green-50 dark:bg-green-900/20 rounded border border-green-200 dark:border-green-800">
                <div className="flex items-center">
                  <Percent className="w-4 h-4 text-green-600 mr-2" />
                  <span className="text-sm text-green-700 dark:text-green-300">
                    {t('discountApplied')}: {pricing.discount.toFixed(2)} {currency} 
                    ({pricing.discountType === 'weekly' ? carRental.weekly_discount_percentage : carRental.monthly_discount_percentage}%)
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Pricing Breakdown */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center">
              <DollarSign className="w-4 h-4 mr-2" />
              {t('pricingBreakdown')}
            </h4>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">{t('pricePerDay')}:</span>
                <span className="font-medium">{carRental.price_per_day} {currency}</span>
              </div>
              
              {carRental.price_per_hour && (
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">{t('pricePerHour')}:</span>
                  <span className="font-medium">{carRental.price_per_hour} {currency}</span>
                </div>
              )}
              
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">{t('effectivePricePerDay')}:</span>
                <span className="font-medium text-green-600 dark:text-green-400">
                  {pricing.pricePerDay.toFixed(2)} {currency}
                </span>
              </div>
            </div>
          </div>

          {/* Discount Information */}
          {(carRental.weekly_discount_percentage > 0 || carRental.monthly_discount_percentage > 0) && (
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center">
                <Percent className="w-4 h-4 mr-2" />
                {t('discountsAvailable')}
              </h4>
              
              <div className="space-y-2 text-sm">
                {carRental.weekly_discount_percentage > 0 && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">
                      {t('weeklyDiscount')} (7+ {t('days')}):
                    </span>
                    <Badge variant="secondary" className="text-green-600 bg-green-100 dark:bg-green-900/20">
                      {carRental.weekly_discount_percentage}%
                    </Badge>
                  </div>
                )}
                
                {carRental.monthly_discount_percentage > 0 && (
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600 dark:text-gray-400">
                      {t('monthlyDiscount')} (30+ {t('days')}):
                    </span>
                    <Badge variant="secondary" className="text-green-600 bg-green-100 dark:bg-green-900/20">
                      {carRental.monthly_discount_percentage}%
                    </Badge>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Rental Limits */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center">
              <Clock className="w-4 h-4 mr-2" />
              {t('rentalLimits')}
            </h4>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">{t('minRentalDays')}:</span>
                <span className="font-medium">{carRental.min_rent_days}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">{t('maxRentalDays')}:</span>
                <span className="font-medium">{carRental.max_rent_days}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">{t('dailyMileageLimit')}:</span>
                <span className="font-medium">{carRental.mileage_limit_per_day} km</span>
              </div>
              
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">{t('advanceBookingDays')}:</span>
                <span className="font-medium">{carRental.advance_booking_days} {t('days')}</span>
              </div>
              
              {/* Hourly Rental Limits */}
              {carRental.allow_hourly_rental && (
                <>
                  <div className="border-t border-gray-200 dark:border-gray-700 pt-2 mt-2">
                    <div className="text-xs text-gray-500 dark:text-gray-400 mb-2 font-medium">
                      {t('hourlyRental')} {t('rentalLimits')}
                    </div>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">{t('minimumHourlyRental')}:</span>
                    <span className="font-medium">{carRental.min_rent_hours || 2} {t('hours')}</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">{t('maximumHourlyRental')}:</span>
                    <span className="font-medium">{carRental.max_hourly_rental_hours || 8} {t('hours')}</span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Deposit Information */}
          {carRental.deposit_amount > 0 && (
            <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-3 border border-yellow-200 dark:border-yellow-800">
              <div className="flex items-center">
                <DollarSign className="w-4 h-4 text-yellow-600 mr-2" />
                <span className="text-sm text-yellow-700 dark:text-yellow-300">
                  {t('depositRequired')}: {carRental.deposit_amount} {currency}
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
