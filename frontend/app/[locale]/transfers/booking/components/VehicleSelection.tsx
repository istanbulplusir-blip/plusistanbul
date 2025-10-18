'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { Car, Users, Package, ArrowRight, ArrowLeft, CheckCircle, Award } from 'lucide-react';
import { useTransferBookingStore } from '@/lib/stores/transferBookingStore';
import { UI_CLASSES, COMPONENT_CLASSES } from '@/lib/constants/ui';

interface VehicleSelectionProps {
  onNext: () => void;
  onBack: () => void;
}

export default function VehicleSelection({ onNext, onBack }: VehicleSelectionProps) {
  const t = useTranslations('transfers');
  
  // Get booking state from store
  const {
    route_data,
    vehicle_type,
    setVehicleType,
    isStepValid,
  } = useTransferBookingStore();

  // Get available vehicles from route data
  const availableVehicles = route_data?.pricing ? 
    route_data.pricing.map((pricing) => ({
      id: pricing.id,
      name: pricing.vehicle_name || pricing.vehicle_type,
      type: pricing.vehicle_type,
      capacity: pricing.max_passengers,
      max_passengers: pricing.max_passengers,
      max_luggage: pricing.max_luggage,
      base_price: pricing.base_price,
      description: pricing.vehicle_description || `${pricing.max_passengers} passengers, ${pricing.max_luggage} luggage`,
      features: pricing.features || [],
      amenities: pricing.amenities || [],
      currency: 'USD', // Default currency
    })) : [];

  // Handle vehicle selection
  const handleVehicleSelect = (vehicleType: string) => {
    setVehicleType(vehicleType);
  };

  // Handle next step
  const handleNext = () => {
    if (isStepValid('vehicle')) {
      onNext();
    }
  };

  // Check if form is valid
  const isValid = isStepValid('vehicle');

  // Helper function to render features and amenities
  const renderFeatures = (features: string[]) => {
    if (!features || features.length === 0) return null;
    
    return (
      <div className={UI_CLASSES.marginTop}>
        <h5 className={`${UI_CLASSES.smallText} ${UI_CLASSES.marginBottom}`}>{t('features')}:</h5>
        <div className="flex flex-wrap gap-1">
          {features.map((feature, index) => (
            <span key={index} className={UI_CLASSES.badgeInfo}>
              {feature}
            </span>
          ))}
        </div>
      </div>
    );
  };

  // Helper function to render amenities
  const renderAmenities = (amenities: string[]) => {
    if (!amenities || amenities.length === 0) return null;
    
    return (
      <div className={UI_CLASSES.marginTop}>
        <h5 className={`${UI_CLASSES.smallText} ${UI_CLASSES.marginBottom}`}>{t('amenities')}:</h5>
        <div className="flex flex-wrap gap-1">
          {amenities.map((amenity, index) => (
            <span key={index} className={UI_CLASSES.badgeSuccess}>
              {amenity}
            </span>
          ))}
        </div>
      </div>
    );
  };

  // Helper function to get vehicle icon based on type
  const getVehicleIcon = (vehicleType: string) => {
    switch (vehicleType.toLowerCase()) {
      case 'sedan':
        return <Car className="w-5 h-5" />;
      case 'suv':
        return <Car className="w-5 h-5" />;
      case 'van':
        return <Car className="w-5 h-5" />;
      case 'sprinter':
        return <Car className="w-5 h-5" />;
      case 'bus':
        return <Car className="w-5 h-5" />;
      case 'limousine':
        return <Car className="w-5 h-5" />;
      default:
        return <Car className="w-5 h-5" />;
    }
  };

  if (!route_data) {
    return (
      <div className={UI_CLASSES.container}>
        <div className={UI_CLASSES.pageHeader}>
          <h2 className={UI_CLASSES.title}>
            {t('selectVehicle')}
          </h2>
          <p className={UI_CLASSES.description}>
            {t('step2')}
          </p>
        </div>

        <div className={UI_CLASSES.cardLarge}>
          <div className={UI_CLASSES.textCenter}>
            <Car className={`${UI_CLASSES.iconLarge} text-gray-400 mx-auto mb-4`} />
            <h3 className={UI_CLASSES.subtitle}>
              {t('noRouteSelected')}
            </h3>
            <p className={`${UI_CLASSES.description} mb-6`}>
              {t('pleaseSelectRouteFirst')}
            </p>
            <button
              onClick={onBack}
              className={UI_CLASSES.buttonSmall}
            >
              {t('backToRouteSelection')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (availableVehicles.length === 0) {
    return (
      <div className={UI_CLASSES.container}>
        <div className={UI_CLASSES.pageHeader}>
          <h2 className={UI_CLASSES.title}>
            {t('selectVehicle')}
          </h2>
          <p className={UI_CLASSES.description}>
            {t('step2')}
          </p>
        </div>

        <div className={UI_CLASSES.cardLarge}>
          <div className={UI_CLASSES.textCenter}>
            <Car className={`${UI_CLASSES.iconLarge} text-gray-400 mx-auto mb-4`} />
            <h3 className={UI_CLASSES.subtitle}>
              {t('noVehiclesAvailable')}
            </h3>
            <p className={`${UI_CLASSES.description} mb-6`}>
              {t('errorFetchingVehicles')}
            </p>
            <button
              onClick={onBack}
              className={UI_CLASSES.buttonSecondary}
            >
              {t('previous')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={UI_CLASSES.container}>
      {/* Header */}
      <div className={UI_CLASSES.pageHeader}>
        <h2 className={UI_CLASSES.title}>
          {t('selectVehicle')}
        </h2>
        <p className={UI_CLASSES.description}>
          {t('step2')}
        </p>
        
        {/* Route Info */}
        {route_data && (
          <div className={`${UI_CLASSES.marginTop} ${UI_CLASSES.padding} ${UI_CLASSES.bgAccent} rounded-lg`}>
            <div className={`${UI_CLASSES.flexStart} gap-2 text-blue-800 dark:text-blue-200`}>
              <span className="font-medium">{route_data.origin}</span>
              <ArrowRight className={UI_CLASSES.iconSmall} />
              <span className="font-medium">{route_data.destination}</span>
            </div>
            <div className={`${UI_CLASSES.smallText} text-blue-600 dark:text-blue-300 ${UI_CLASSES.marginTop}`}>
              {route_data.pricing.length} {t('vehicleType')} {t('available')}
            </div>
            
            {/* Route Features Summary */}
            {(route_data.round_trip_discount_enabled || parseFloat(route_data.peak_hour_surcharge || '0') > 0 || parseFloat(route_data.midnight_surcharge || '0') > 0) && (
              <div className={`${UI_CLASSES.marginTop} pt-2 border-t border-blue-200 dark:border-blue-400`}>
                <div className="flex flex-wrap gap-2 text-xs">
                  {route_data.round_trip_discount_enabled && (
                    <span className={UI_CLASSES.badgeSuccess}>
                      <span>{t('discountPercentage', { percentage: route_data.round_trip_discount_percentage || '0' })}</span>
                    </span>
                  )}
                  {parseFloat(route_data.peak_hour_surcharge || '0') > 0 && (
                    <span className={UI_CLASSES.badgeWarning}>
                      <span>{t('peakHours')}: {t('surchargePercentage', { percentage: route_data.peak_hour_surcharge || '0' })}</span>
                    </span>
                  )}
                  {parseFloat(route_data.midnight_surcharge || '0') > 0 && (
                    <span className={UI_CLASSES.badgePurple}>
                      <span>{t('timeSurcharge')}: {t('surchargePercentage', { percentage: route_data.midnight_surcharge || '0' })}</span>
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Vehicles List */}
      <div className={UI_CLASSES.sectionHeader}>
        <h3 className={UI_CLASSES.sectionTitle}>
          {t('availableVehicles')}
        </h3>

        <div className={UI_CLASSES.grid3}>
          {availableVehicles.map((vehicle) => (
            <div
              key={vehicle.id}
              onClick={() => handleVehicleSelect(vehicle.type)}
                              className={vehicle_type === vehicle.type ? COMPONENT_CLASSES.vehicleCardSelected : COMPONENT_CLASSES.vehicleCard}
            >
              {/* Vehicle Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  {getVehicleIcon(vehicle.type)}
                  <h4 className="font-medium text-gray-900 dark:text-gray-100">{vehicle.name}</h4>
                </div>
                {vehicle_type === vehicle.type && (
                  <CheckCircle className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                )}
              </div>

              {/* Vehicle Description */}
              {vehicle.description && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{vehicle.description}</p>
              )}

              {/* Vehicle Details */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 mb-3">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center space-x-2">
                    <Users className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                    <span className="text-gray-700 dark:text-gray-300 font-medium">{vehicle.max_passengers} {t('passengers')}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Package className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                    <span className="text-gray-700 dark:text-gray-300 font-medium">{vehicle.max_luggage} {t('luggage')}</span>
                  </div>
                </div>
              </div>

              {/* Features */}
              {renderFeatures(vehicle.features)}

              {/* Amenities */}
              {renderAmenities(vehicle.amenities)}

              {/* Price */}
              <div className="text-right mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                <div className="text-lg font-bold text-blue-600 dark:text-blue-400">
                  {vehicle.currency} {vehicle.base_price}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">{t('basePrice')}</div>
              </div>

              {/* Selection Indicator */}
              {vehicle_type === vehicle.type && (
                <div className="mt-3 pt-3 border-t border-blue-200 dark:border-blue-400">
                  <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 text-sm">
                    <Award className="w-4 h-4" />
                    {t('selected')}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Navigation */}
      <div className={COMPONENT_CLASSES.navigationContainer}>
        <button
          onClick={onBack}
          className={UI_CLASSES.buttonSecondary}
        >
          <ArrowLeft className={UI_CLASSES.iconSmall} />
          {t('previous')}
        </button>
        <button
          onClick={handleNext}
          disabled={!isValid}
          className={isValid ? UI_CLASSES.buttonPrimary : UI_CLASSES.buttonDisabled}
        >
          {t('next')}
          <ArrowRight className={UI_CLASSES.iconSmall} />
        </button>
      </div>
    </div>
  );
} 