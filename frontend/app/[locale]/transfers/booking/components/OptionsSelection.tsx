'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Package, ArrowRight, ArrowLeft, CheckCircle } from 'lucide-react';
import { useTransferBookingStore } from '@/lib/stores/transferBookingStore';
import { useTransferOptions } from '@/lib/hooks/useTransfers';
import { TransferOption } from '@/lib/api/transfers';

interface OptionsSelectionProps {
  onNext: () => void;
  onBack: () => void;
}

export default function OptionsSelection({ onNext, onBack }: OptionsSelectionProps) {
  const t = useTranslations('transfers');
  
  // Get booking state from store
  const {
    route_data,
    route_id,
    vehicle_type,
    selected_options,
    setOptions,
    isStepValid,
  } = useTransferBookingStore();

  // Fetch options from API - pass route_id to get route-specific options
  const { data: optionsResponse, error: optionsError, isLoading: optionsLoading } = useTransferOptions(route_id || undefined);
  
  console.log('OptionsSelection - route_id:', route_id);
  console.log('OptionsSelection - optionsResponse:', optionsResponse);
  console.log('OptionsSelection - optionsError:', optionsError);
  console.log('OptionsSelection - optionsLoading:', optionsLoading);
  
  // Local state for form inputs
  const [localSelectedOptions, setLocalSelectedOptions] = useState(
    selected_options || []
  );
  const [availableOptions, setAvailableOptions] = useState<TransferOption[]>([]);
  const [loading, setLoading] = useState(true);

  // Get available options from API
  useEffect(() => {
    console.log('OptionsSelection useEffect - optionsResponse changed:', optionsResponse);
    console.log('OptionsSelection useEffect - optionsLoading:', optionsLoading);
    console.log('OptionsSelection useEffect - optionsError:', optionsError);
    
    if (optionsLoading) {
      setLoading(true);
      return;
    }
    
    if (optionsError) {
      console.error('Error loading transfer options:', optionsError);
      setAvailableOptions([]);
      setLoading(false);
      return;
    }
    
    if (optionsResponse && Array.isArray(optionsResponse)) {
      // Filter to only show global options (those without a specific route)
      const globalOptions = optionsResponse.filter(option => !option.route);
      setAvailableOptions(globalOptions);
      console.log('Loaded transfer options:', optionsResponse.length, 'Global options:', globalOptions.length);
      console.log('Global options details:', globalOptions);
    } else {
      console.log('No options response or not an array:', optionsResponse);
      setAvailableOptions([]);
    }
    setLoading(false);
  }, [optionsResponse, optionsLoading, optionsError]);

  // Handle option selection (checkbox style)
  const handleOptionToggle = (optionId: string) => {
    const existingIndex = localSelectedOptions.findIndex(opt => opt.option_id === optionId);
    const newSelectedOptions = [...localSelectedOptions];
    
    if (existingIndex >= 0) {
      // Remove option if already selected
      newSelectedOptions.splice(existingIndex, 1);
    } else {
      // Find the option details from available options
      const optionDetails = availableOptions.find((opt: TransferOption) => opt.id === optionId);
      const unitPrice = optionDetails?.price || undefined;
      
      // Add option with complete details
      newSelectedOptions.push({ 
        option_id: optionId, 
        quantity: 1,
        name: optionDetails?.name,
        price: unitPrice,
        description: optionDetails?.description
      });
    }
    
    setLocalSelectedOptions(newSelectedOptions);
    setOptions(newSelectedOptions);
  };

  // Change quantity with respect to max_quantity
  const changeQuantity = (optionId: string, delta: number) => {
    const optionDetails = availableOptions.find((opt: TransferOption) => opt.id === optionId);
    const maxQty = typeof optionDetails?.max_quantity === 'number' ? optionDetails.max_quantity : undefined;
    const newSelectedOptions = localSelectedOptions.map((opt) => ({ ...opt }));
    const idx = newSelectedOptions.findIndex((o) => o.option_id === optionId);
    if (idx === -1) return;
    let nextQty = (newSelectedOptions[idx].quantity || 1) + delta;
    if (nextQty < 1) nextQty = 1;
    if (typeof maxQty === 'number' && nextQty > maxQty) nextQty = maxQty;
    newSelectedOptions[idx].quantity = nextQty;
    setLocalSelectedOptions(newSelectedOptions);
    setOptions(newSelectedOptions);
  };

  // Check if option is selected
  const isOptionSelected = (optionId: string) => {
    return localSelectedOptions.some(opt => opt.option_id === optionId);
  };

  // Handle next step
  const handleNext = () => {
    if (isStepValid('options')) {
      onNext();
    }
  };

  // Check if form is valid
  const isValid = isStepValid('options');

  if (!route_data || !vehicle_type) {
    return (
      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            {t('selectOptions')}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {t('step5')}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
          <div className="text-center">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
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

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            {t('selectOptions')}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {t('step5')}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 dark:border-blue-400 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">{t('loading')}</p>
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
          {t('selectOptions')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {t('step5')}
        </p>
        
        {/* Route and Vehicle Info */}
        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="flex items-center gap-2 text-blue-800 dark:text-blue-200 mb-2">
            <span className="font-medium">{route_data.origin}</span>
            <ArrowRight className="w-4 h-4" />
            <span className="font-medium">{route_data.destination}</span>
          </div>
          <div className="text-sm text-blue-700 dark:text-blue-300">
            {t('vehicle')}: {vehicle_type}
          </div>
        </div>
        
        {/* Debug Info */}
        <div className="mt-4 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Debug Info:</h4>
          <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            <p>Route ID: {route_id || 'None'}</p>
            <p>Loading: {optionsLoading ? 'Yes' : 'No'}</p>
            <p>Error: {optionsError ? 'Yes' : 'No'}</p>
            <p>Response: {optionsResponse ? `${optionsResponse.length} items` : 'None'}</p>
            <p>Available Options: {availableOptions.length}</p>
          </div>
          <button
            onClick={async () => {
              try {
                const response = await fetch('http://localhost:8000/api/v1/transfers/options/');
                const data = await response.json();
                console.log('Manual API test result:', data);
                alert(`API test successful! Found ${data.results?.length || 0} options`);
              } catch (error) {
                console.error('Manual API test failed:', error);
                alert(`API test failed: ${error}`);
              }
            }}
            className="mt-2 px-3 py-1 bg-green-500 text-white rounded text-sm"
          >
            Test API
          </button>
        </div>
      </div>

      {/* Available Options */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('availableOptions')}
        </h3>

        {availableOptions.length === 0 ? (
          <div className="text-center py-8">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              {t('noOptionsAvailable')}
            </h4>
            <p className="text-gray-600 dark:text-gray-400">
              {t('noOptionsDescription')}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {availableOptions.map((option) => {
              const isSelected = isOptionSelected(option.id);
              
              return (
                <div
                  key={option.id}
                  className={`
                    p-4 border rounded-lg transition-all
                    ${isSelected
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400'
                    }
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-medium text-gray-900 dark:text-gray-100">{option.name}</h4>
                        {isSelected && (
                          <CheckCircle className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        )}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{option.description}</p>
                      <div className="text-sm text-gray-700 dark:text-gray-300">
                        <span className="font-semibold text-blue-600 dark:text-blue-400">${Number(option.price).toFixed(2)}</span>
                        <span className="ml-1 text-gray-500 dark:text-gray-400">/ unit</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3 ml-4">
                      {!isSelected ? (
                        <button
                          onClick={() => handleOptionToggle(option.id)}
                          className="w-8 h-8 rounded-full flex items-center justify-center transition-colors bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600 hover:text-gray-700 dark:hover:text-gray-300"
                        >
                          <div className="w-4 h-4 border-2 border-current rounded-sm"></div>
                        </button>
                      ) : (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => changeQuantity(option.id, -1)}
                            className="w-8 h-8 rounded-full flex items-center justify-center bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/50"
                          >
                            −
                          </button>
                          <span className="min-w-[2rem] text-center font-semibold text-gray-900 dark:text-gray-100">{(localSelectedOptions.find((o)=>o.option_id===option.id)?.quantity) || 1}</span>
                          <button
                            onClick={() => changeQuantity(option.id, 1)}
                            className="w-8 h-8 rounded-full flex items-center justify-center bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/50"
                          >
                            +
                          </button>
                          <button
                            onClick={() => handleOptionToggle(option.id)}
                            className="ml-2 px-3 py-1 rounded border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700"
                          >
                            {t('remove')}
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Selected Options Summary */}
      {localSelectedOptions.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            {t('selectedOptions')}
          </h3>
          
          <div className="space-y-3">
            {localSelectedOptions.map((selectedOption) => {
              const option = availableOptions.find(opt => opt.id === selectedOption.option_id);
              if (!option) return null;
              
              return (
                <div key={selectedOption.option_id} className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                  <div>
                    <span className="font-medium text-gray-900 dark:text-gray-100">{option.name}</span>
                  </div>
                  <span className="font-medium text-gray-900 dark:text-gray-100">
                    ${Number(option.price).toFixed(2)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

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