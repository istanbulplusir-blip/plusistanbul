'use client';

import React, { useEffect } from 'react';
import { useTranslations } from 'next-intl';

import { MapPin, Calendar, Clock, Users, ArrowLeft, CheckCircle, Star, Percent, Car } from 'lucide-react';
import { useTransferBookingStore } from '@/lib/stores/transferBookingStore';
import { useCart } from '@/lib/hooks/useCart';
import PriceSummary from '@/components/common/PriceSummary';

interface BookingSummaryProps {
  onBack: () => void;
  onConfirm?: () => void;
}

export default function BookingSummary({ onBack }: BookingSummaryProps) {
  const t = useTranslations('transfers');
  // Get booking state from store
  const {
    route_data,
    vehicle_type,
    trip_type,
    outbound_date,
    outbound_time,
    return_date,
    return_time,
    passenger_count,
    luggage_count,
    selected_options,
    contact_name,
    contact_phone,
    special_requirements,
    pricing_breakdown,
    calculatePrice,
    is_calculating_price,
    price_calculation_error,
  } = useTransferBookingStore();

  // Get option details from store or pricing breakdown
  const getOptionDetails = (optionId: string) => {
    // First try to get from store (selected_options with details)
    const storedOption = selected_options.find(opt => opt.option_id === optionId);
    
    if (storedOption?.name) {
      console.log(`Found option details in store for ${optionId}:`, storedOption);
      return {
        option_id: optionId,
        name: storedOption.name,
        price: storedOption.price || 0,
        quantity: storedOption.quantity,
        total: (storedOption.price || 0) * storedOption.quantity
      };
    }
    
    // Second try to get from pricing breakdown
    const optionDetails = pricing_breakdown?.price_breakdown?.options_breakdown?.find(
      (opt: { id: string }) => opt.id === optionId
    );
    
    if (optionDetails) {
      console.log(`Found option details in pricing breakdown for ${optionId}:`, optionDetails);
      return optionDetails;
    }
    
    // Fallback: if options_breakdown is not available but options_total > 0,
    // we can estimate the price per option
    if (pricing_breakdown?.price_breakdown?.options_total && selected_options.length > 0) {
      const estimatedPricePerOption = pricing_breakdown.price_breakdown.options_total / selected_options.length;
      console.log(`Using estimated price for ${optionId}: ${estimatedPricePerOption}`);
      return {
        option_id: optionId,
        name: storedOption?.name || `Option ${optionId.slice(0, 8)}...`,
        price: estimatedPricePerOption,
        quantity: storedOption?.quantity || 1,
        total: estimatedPricePerOption * (storedOption?.quantity || 1)
      };
    }
    
    console.log(`No option details found for ${optionId}`);
    return null;
  };

  // Cart integration
  const { } = useCart();

  // Calculate price when component mounts
  useEffect(() => {
    if (route_data && vehicle_type && outbound_date && outbound_time) {
      // Only calculate if pricing_breakdown is null or if we need to recalculate
      if (!pricing_breakdown || Object.keys(pricing_breakdown).length === 0) {
        calculatePrice();
      }
    }
  }, [route_data, vehicle_type, outbound_date, outbound_time, return_date, return_time, passenger_count, luggage_count, selected_options, calculatePrice, pricing_breakdown]);

  // Additional effect to ensure pricing is calculated when needed
  useEffect(() => {
    if (route_data && vehicle_type && outbound_date && outbound_time && !pricing_breakdown) {
      calculatePrice();
    }
  }, [pricing_breakdown, route_data, vehicle_type, outbound_date, outbound_time, calculatePrice]);



  // Helper function to get time category and surcharge info
  const getTimeInfo = (time: string) => {
    const hour = parseInt(time.split(':')[0]);
    if (7 <= hour && hour <= 9 || 17 <= hour && hour <= 19) {
      return { category: t('peakHours'), surcharge: route_data?.peak_hour_surcharge || '0' };
    } else if (22 <= hour && hour <= 23 || 0 <= hour && hour <= 6) {
      return { category: t('midnightHours'), surcharge: route_data?.midnight_surcharge || '0' };
    } else {
      return { category: t('normalHours'), surcharge: '0' };
    }
  };

  // Helper function to render route badges
  const renderRouteBadges = () => {
    const badges = [];
    
    if (route_data?.is_popular) {
      badges.push(
        <span key="popular" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200">
          <Star className="w-3 h-3 mr-1" />
          {t('popularBadge')}
        </span>
      );
    }
    
    if (route_data?.round_trip_discount_enabled) {
      badges.push(
        <span key="discount" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200">
          <Percent className="w-3 h-3 mr-1" />
          {t('discountBadge')}
        </span>
      );
    }
    
    if (parseFloat(route_data?.peak_hour_surcharge || '0') > 0 || parseFloat(route_data?.midnight_surcharge || '0') > 0) {
      badges.push(
        <span key="surcharge" className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200">
          <Clock className="w-3 h-3 mr-1" />
          {t('surchargeBadge')}
        </span>
      );
    }
    
    return badges;
  };

  // Helper function to render vehicle features
  const renderVehicleFeatures = () => {
    const vehiclePricing = route_data?.pricing.find((p: { vehicle_type: string }) => p.vehicle_type === vehicle_type);
    if (!vehiclePricing?.features || vehiclePricing.features.length === 0) return null;
    
    return (
      <div className="mt-3">
        <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{t('vehicleFeatures')}:</h5>
        <div className="flex flex-wrap gap-1">
          {vehiclePricing.features.map((feature: string, index: number) => (
            <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200">
              {feature}
            </span>
          ))}
        </div>
      </div>
    );
  };

  // Helper function to render vehicle amenities
  const renderVehicleAmenities = () => {
    const vehiclePricing = route_data?.pricing.find((p: { vehicle_type: string }) => p.vehicle_type === vehicle_type);
    if (!vehiclePricing?.amenities || vehiclePricing.amenities.length === 0) return null;
    
    return (
      <div className="mt-3">
        <h5 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{t('vehicleAmenities')}:</h5>
        <div className="flex flex-wrap gap-1">
          {vehiclePricing.amenities.map((amenity: string, index: number) => (
            <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200">
              {amenity}
            </span>
          ))}
        </div>
      </div>
    );
  };

  if (!route_data || !vehicle_type) {
    return (
      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            {t('bookingSummary')}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {t('step7')}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
          <div className="text-center">
            <CheckCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              {t('incompleteBooking')}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {t('pleaseCompletePreviousSteps')}
            </p>
            <button
              onClick={onBack}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {t('backToPreviousStep')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Get vehicle pricing info
  const vehiclePricing = route_data.pricing.find((p: { vehicle_type: string }) => p.vehicle_type === vehicle_type);
  const outboundTimeInfo = outbound_time ? getTimeInfo(outbound_time) : { category: '', surcharge: '0' };
  const returnTimeInfo = return_time && return_time !== '' ? getTimeInfo(return_time as string) : null;

  // Create fallback pricing breakdown if API data is not available
  const getFallbackPricingBreakdown = () => {
    if (!vehiclePricing) return null;
    
    const basePrice = Number(vehiclePricing.base_price) || 0;
    
    // Calculate outbound surcharge
    let outboundSurcharge = 0;
    const peakHourSurcharge = parseFloat(route_data.peak_hour_surcharge || '0');
    if (peakHourSurcharge > 0) {
      const hour = parseInt(outbound_time?.split(':')[0] || '0');
      if ((hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19)) {
        outboundSurcharge = (basePrice * peakHourSurcharge) / 100;
      }
    }
    
    // Calculate midnight surcharge
    let midnightSurcharge = 0;
    const midnightSurchargePercent = parseFloat(route_data.midnight_surcharge || '0');
    if (midnightSurchargePercent > 0) {
      const hour = parseInt(outbound_time?.split(':')[0] || '0');
      if (hour >= 22 || hour <= 6) {
        midnightSurcharge = (basePrice * midnightSurchargePercent) / 100;
      }
    }
    
    // Calculate return surcharge
    let returnSurcharge = 0;
    if (return_time && peakHourSurcharge > 0) {
      const hour = parseInt(return_time.split(':')[0]);
      if ((hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19)) {
        returnSurcharge = (basePrice * peakHourSurcharge) / 100;
      }
    }
    
    // Calculate round trip discount
    let roundTripDiscount = 0;
    if (trip_type === 'round_trip' && route_data.round_trip_discount_enabled) {
      const discountPercent = parseFloat(route_data.round_trip_discount_percentage || '0');
      roundTripDiscount = (basePrice * discountPercent) / 100;
    }
    
    // Calculate options total
    const optionsTotal = selected_options.reduce((total, opt) => {
      const optionDetails = getOptionDetails(opt.option_id);
      if (optionDetails && 'total' in optionDetails) {
        return total + (optionDetails.total || 0);
      } else if (optionDetails) {
        return total + ((optionDetails.price || 0) * (opt.quantity || 1));
      }
      return total;
    }, 0);
    
    const subtotal = basePrice + outboundSurcharge + midnightSurcharge + returnSurcharge + optionsTotal - roundTripDiscount;
    
    return {
      base_price: basePrice,
      outbound_surcharge: outboundSurcharge,
      return_surcharge: returnSurcharge,
      round_trip_discount: roundTripDiscount,
      options_total: optionsTotal,
      final_price: subtotal,
      subtotal: subtotal
    };
  };

  // Use API data or fallback data
  const effectivePricingBreakdown = pricing_breakdown || {
    price_breakdown: getFallbackPricingBreakdown(),
    options_breakdown: selected_options.map(opt => {
      const optionDetails = getOptionDetails(opt.option_id);
      let total = 0;
      if (optionDetails && 'total' in optionDetails) {
        total = optionDetails.total || 0;
      } else if (optionDetails) {
        total = (optionDetails.price || 0) * (opt.quantity || 1);
      }
      return {
        option_id: opt.option_id,
        name: optionDetails?.name || `Option ${opt.option_id.slice(0, 8)}...`,
        price: optionDetails?.price || 0,
        quantity: opt.quantity,
        total: total
      };
    })
  };



  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          {t('bookingSummary')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {t('step7')}
        </p>
      </div>

      {/* Route Information */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('routeInformation')}
        </h3>
        
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <MapPin className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <div className="flex-1">
              <div className="font-medium text-gray-900 dark:text-gray-100">
                {route_data.origin} → {route_data.destination}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {vehiclePricing ? `${vehiclePricing.base_price} USD` : t('priceOnRequest')}
              </div>
              {renderRouteBadges().length > 0 && (
                <div className="flex gap-1 mt-2">
                  {renderRouteBadges()}
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Calendar className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <div>
              <div className="font-medium text-gray-900 dark:text-gray-100">
                {t('tripType')}: {trip_type === 'one_way' ? t('oneWay') : t('roundTrip')}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {outbound_date} at {outbound_time}
                {trip_type === 'round_trip' && return_date && return_time && (
                  <span> • {t('return')}: {return_date} at {return_time}</span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <div>
              <div className="font-medium text-gray-900 dark:text-gray-100">
                {t('passengers')}: {passenger_count} • {t('luggage')}: {luggage_count}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {t('vehicle')}: {vehiclePricing?.vehicle_name || vehicle_type}
              </div>
            </div>
          </div>

          {/* Route Features */}
          {(route_data.round_trip_discount_enabled || parseFloat(route_data.peak_hour_surcharge || '0') > 0 || parseFloat(route_data.midnight_surcharge || '0') > 0) && (
            <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{t('routeFeatures')}:</h4>
              <div className="space-y-2">
                {route_data.round_trip_discount_enabled && (
                  <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
                    <Percent className="w-4 h-4" />
                    <span>{t('roundTripDiscountPercentage')}: {route_data.round_trip_discount_percentage}%</span>
                  </div>
                )}
                {parseFloat(route_data.peak_hour_surcharge || '0') > 0 && (
                  <div className="flex items-center gap-2 text-sm text-orange-600 dark:text-orange-400">
                    <Clock className="w-4 h-4" />
                    <span>{t('peakHourSurcharge')}: {route_data.peak_hour_surcharge}%</span>
                  </div>
                )}
                {parseFloat(route_data.midnight_surcharge || '0') > 0 && (
                  <div className="flex items-center gap-2 text-sm text-purple-600 dark:text-purple-400">
                    <Clock className="w-4 h-4" />
                    <span>{t('midnightSurcharge')}: {route_data.midnight_surcharge}%</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Vehicle Details */}
          {vehiclePricing && (
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{t('vehicleDetails')}:</h4>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <Car className="w-4 h-4" />
                  <span>{vehiclePricing.vehicle_name || vehicle_type}</span>
                </div>
                {vehiclePricing.vehicle_description && (
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {vehiclePricing.vehicle_description}
                  </div>
                )}
                {renderVehicleFeatures()}
                {renderVehicleAmenities()}
              </div>
            </div>
          )}

          {/* Time Information */}
          <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/30 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{t('timeInfo')}:</h4>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <Clock className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span className="text-gray-600 dark:text-gray-400">{t('outboundTime')}: {outbound_time} ({outboundTimeInfo.category})</span>
                {parseFloat(outboundTimeInfo.surcharge) > 0 && (
                  <span className="text-orange-600 dark:text-orange-400 text-xs">+{outboundTimeInfo.surcharge}%</span>
                )}
              </div>
              {returnTimeInfo && (
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="w-4 h-4 text-green-600 dark:text-green-400" />
                  <span className="text-gray-600 dark:text-gray-400">{t('returnTime')}: {return_time} ({returnTimeInfo.category})</span>
                  {parseFloat(returnTimeInfo.surcharge) > 0 && (
                    <span className="text-orange-600 dark:text-orange-400 text-xs">+{returnTimeInfo.surcharge}%</span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Contact Information */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('contactInformation')}
        </h3>
        
        <div className="space-y-3">
          <div>
            <span className="font-medium text-gray-900 dark:text-gray-100">{t('contactName')}:</span>
            <div className="text-gray-600 dark:text-gray-400">{contact_name}</div>
          </div>
          <div>
            <span className="font-medium text-gray-900 dark:text-gray-100">{t('contactPhone')}:</span>
            <div className="text-gray-600 dark:text-gray-400">{contact_phone}</div>
          </div>
          {special_requirements && (
            <div>
              <span className="font-medium text-gray-900 dark:text-gray-100">{t('specialRequirements')}:</span>
              <div className="text-gray-600 dark:text-gray-400">{special_requirements}</div>
            </div>
          )}
        </div>
      </div>

      {/* Selected Options */}
      {selected_options.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            {t('selectedOptions')}
          </h3>
          
          <div className="space-y-2">
            {selected_options.map((option) => {
              const optionDetails = getOptionDetails(option.option_id);
              return (
                <div key={option.option_id} className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                  <div className="flex-1">
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                      {optionDetails?.name || `Option ${option.option_id.slice(0, 8)}...`}
                    </span>
                    {optionDetails && (
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {t('quantity')}: {'quantity' in optionDetails ? optionDetails.quantity : 1} × USD {Number(optionDetails.price).toFixed(2)}
                      </div>
                    )}
                    {!optionDetails && (
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {t('optionDetailsNotAvailable')}
                      </div>
                    )}
                  </div>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    USD {optionDetails && 'total' in optionDetails ? optionDetails.total.toFixed(2) : '0.00'}
                  </span>
                </div>
              );
            })}
          </div>
          
          {/* Show total options price if available */}
          {effectivePricingBreakdown?.price_breakdown?.options_total && (
            <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-600">
              <div className="flex justify-between items-center">
                <span className="font-medium text-gray-700 dark:text-gray-300">{t('optionsTotal')}:</span>
                <span className="font-bold text-gray-900 dark:text-gray-100">
                  USD {effectivePricingBreakdown.price_breakdown.options_total.toFixed(2)}
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Pricing Breakdown */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('pricingBreakdown')}
        </h3>
        
        {is_calculating_price ? (
          <div className="text-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 dark:border-blue-400 mx-auto"></div>
            <p className="mt-2 text-gray-600 dark:text-gray-400">{t('calculatingPrice')}</p>
          </div>
        ) : price_calculation_error ? (
          <div className="text-center py-4">
            <p className="text-red-600 dark:text-red-400">{t('priceCalculationError')}</p>
            <button
              onClick={calculatePrice}
              className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {t('retryCalculation')}
            </button>
          </div>
        ) : effectivePricingBreakdown ? (
          <div className="space-y-6">
            {/* Normalized Pricing Breakdown - Main Content */}
            <PriceSummary
              title={t('pricingBreakdown')}
              breakdown={(function () {
                const pb = effectivePricingBreakdown?.price_breakdown;
                if (!pb) return null;
                
                // Use the exact values from the backend without manual calculations
                const base = Number(pb.base_price || 0);
                const outS = Number(pb.outbound_surcharge || 0);
                const retS = Number(pb.return_surcharge || 0);
                const rtd = Number(pb.round_trip_discount || 0);
                const options = Number(pb.options_total || 0);
                
                // Calculate subtotal manually since it's not provided by backend
                const subtotal = base + outS + retS + options - rtd;
                const final_price = Number(pb.final_price || 0);
                
                return {
                  base_price: base,
                  modifiers: {
                    outbound_surcharge: outS,
                    return_surcharge: retS,
                    round_trip_discount: rtd,
                  },
                  options_total: options,
                  fees_total: 0,
                  taxes_total: 0,
                  subtotal,
                  final_price,
                  currency: 'USD',
                };
              })()}
              formatPrice={(price: number) => `USD ${price.toFixed(2)}`}
            />
          </div>
        ) : (
          <div className="text-center py-4">
            <p className="text-gray-600 dark:text-gray-400">{t('priceNotCalculated')}</p>
            <button
              onClick={calculatePrice}
              className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {t('calculatePrice')}
            </button>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <div className="flex justify-start">
          <button
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            {t('previous')}
          </button>
        </div>
      </div>
    </div>
  );
} 