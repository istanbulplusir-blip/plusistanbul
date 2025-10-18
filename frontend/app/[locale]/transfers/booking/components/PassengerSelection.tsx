'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Users, Package, ArrowRight, ArrowLeft, Plus, Minus } from 'lucide-react';
import { useTransferBookingStore } from '@/lib/stores/transferBookingStore';

interface PassengerSelectionProps {
  onNext: () => void;
  onBack: () => void;
}

export default function PassengerSelection({ onNext, onBack }: PassengerSelectionProps) {
  const t = useTranslations('transfers');
  
  // Get booking state from store
  const {
    route_data,
    vehicle_type,
    passenger_count,
    luggage_count,
    setPassengers,
    isStepValid,
  } = useTransferBookingStore();

  // Local state for form inputs
  const [localPassengerCount, setLocalPassengerCount] = useState(passenger_count || 1);
  const [localLuggageCount, setLocalLuggageCount] = useState(luggage_count || 0);

  // Get vehicle capacity from route data
  const selectedVehiclePricing = route_data?.pricing?.find((p: { vehicle_type: string }) => p.vehicle_type === vehicle_type);
  const maxPassengers = selectedVehiclePricing?.max_passengers || 1;
  const maxLuggage = selectedVehiclePricing?.max_luggage || 0;

  // Handle passenger count change
  const handlePassengerChange = (newCount: number) => {
    if (newCount >= 1 && newCount <= maxPassengers) {
      setLocalPassengerCount(newCount);
      setPassengers(newCount, localLuggageCount);
    }
  };

  // Handle luggage count change
  const handleLuggageChange = (newCount: number) => {
    if (newCount >= 0 && newCount <= maxLuggage) {
      setLocalLuggageCount(newCount);
      setPassengers(localPassengerCount, newCount);
    }
  };

  // Handle next step
  const handleNext = () => {
    if (isStepValid('passengers')) {
      onNext();
    }
  };

  // Check if form is valid
  const isValid = isStepValid('passengers');

  if (!route_data || !vehicle_type) {
    return (
      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            {t('selectPassengers')}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {t('step4')}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
          <div className="text-center">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              {t('noVehicleSelected')}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {t('pleaseSelectVehicleFirst')}
            </p>
            <button
              onClick={onBack}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {t('backToVehicleSelection')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          {t('selectPassengers')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {t('step4')}
        </p>
        
        {/* Route and Vehicle Info */}
        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="flex items-center gap-2 text-blue-800 dark:text-blue-200 mb-2">
            <span className="font-medium">{route_data.origin}</span>
            <ArrowRight className="w-4 h-4" />
            <span className="font-medium">{route_data.destination}</span>
          </div>
          <div className="text-sm text-blue-700 dark:text-blue-300">
            {t('vehicle')}: {vehicle_type} • {t('maxCapacity')}: {maxPassengers} {t('passengers')}, {maxLuggage} {t('luggage')}
          </div>
        </div>
      </div>

      {/* Passenger Count */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('passengerCount')}
        </h3>
        
        <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
          <div className="flex items-center gap-3">
            <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100">{t('passengers')}</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {t('maxPassengers')}: {maxPassengers}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={() => handlePassengerChange(localPassengerCount - 1)}
              disabled={localPassengerCount <= 1}
              className={`
                w-8 h-8 rounded-full flex items-center justify-center transition-colors
                ${localPassengerCount <= 1
                  ? 'bg-gray-200 dark:bg-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                  : 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/50'
                }
              `}
            >
              <Minus className="w-4 h-4" />
            </button>
            
            <span className="text-xl font-bold text-gray-900 dark:text-gray-100 min-w-[2rem] text-center">
              {localPassengerCount}
            </span>
            
            <button
              onClick={() => handlePassengerChange(localPassengerCount + 1)}
              disabled={localPassengerCount >= maxPassengers}
              className={`
                w-8 h-8 rounded-full flex items-center justify-center transition-colors
                ${localPassengerCount >= maxPassengers
                  ? 'bg-gray-200 dark:bg-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                  : 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/50'
                }
              `}
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Luggage Count */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('luggageCount')}
        </h3>
        
        <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
          <div className="flex items-center gap-3">
            <Package className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100">{t('luggage')}</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {t('maxLuggage')}: {maxLuggage}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={() => handleLuggageChange(localLuggageCount - 1)}
              disabled={localLuggageCount <= 0}
              className={`
                w-8 h-8 rounded-full flex items-center justify-center transition-colors
                ${localLuggageCount <= 0
                  ? 'bg-gray-200 dark:bg-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                  : 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/50'
                }
              `}
            >
              <Minus className="w-4 h-4" />
            </button>
            
            <span className="text-xl font-bold text-gray-900 dark:text-gray-100 min-w-[2rem] text-center">
              {localLuggageCount}
            </span>
            
            <button
              onClick={() => handleLuggageChange(localLuggageCount + 1)}
              disabled={localLuggageCount >= maxLuggage}
              className={`
                w-8 h-8 rounded-full flex items-center justify-center transition-colors
                ${localLuggageCount >= maxLuggage
                  ? 'bg-gray-200 dark:bg-gray-600 text-gray-400 dark:text-gray-500 cursor-not-allowed'
                  : 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/50'
                }
              `}
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('summary')}
        </h3>
        
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
            <span className="text-gray-600 dark:text-gray-400">{t('passengers')}</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">{localPassengerCount}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
            <span className="text-gray-600 dark:text-gray-400">{t('luggage')}</span>
            <span className="font-medium text-gray-900 dark:text-gray-100">{localLuggageCount}</span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span className="text-gray-600 dark:text-gray-400">{t('totalCapacity')}</span>
            <span className="font-medium text-blue-600 dark:text-blue-400">
              {localPassengerCount}/{maxPassengers} {t('passengers')}, {localLuggageCount}/{maxLuggage} {t('luggage')}
            </span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <div className="flex justify-between">
          <button
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            {t('previous')}
          </button>
          <button
            onClick={handleNext}
            disabled={!isValid}
            className={`
              px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2
              ${isValid
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
              }
            `}
          >
            {t('next')}
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
} 