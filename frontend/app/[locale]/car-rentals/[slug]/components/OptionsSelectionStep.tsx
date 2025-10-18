'use client';

import React from 'react';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import { Plus, Minus, Shield } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { CarRentalOption } from '@/lib/api/car-rentals';

interface SelectedOption {
  id: string;
  quantity: number;
  name?: string;
  price?: string | number;
  description?: string;
}

interface OptionsSelectionStepProps {
  options: CarRentalOption[];
  selectedOptions: SelectedOption[];
  basicInsurance: boolean;
  comprehensiveInsurance: boolean;
  onOptionsChange: (options: SelectedOption[]) => void;
  onInsuranceChange: (basic: boolean, comprehensive: boolean) => void;
  onNext: () => void;
  onBack?: () => void;
  isLoading?: boolean;
  currency: string;
  rentalDays: number;
  carRentalData?: {
    id: string;
    title: string;
    brand: string;
    model: string;
    year: number;
    seats: number;
    fuel_type: string;
    transmission: string;
    pickup_location: string;
    dropoff_location: string;
    comprehensive_insurance_price?: string;
  };
}

export default function OptionsSelectionStep({
  options,
  selectedOptions,
  basicInsurance,
  comprehensiveInsurance,
  onOptionsChange,
  onInsuranceChange,
  onNext,
  onBack,
  isLoading = false,
  currency,
  rentalDays,
  carRentalData
}: OptionsSelectionStepProps) {
  const t = useTranslations('carRentalBooking');

  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const calculateOptionPrice = (option: CarRentalOption, quantity: number) => {
    if (option.price_type === 'fixed') {
      return parseFloat(option.price) * quantity;
    } else if (option.price_type === 'daily') {
      return parseFloat(option.price) * quantity * rentalDays;
    } else if (option.price_type === 'percentage') {
      // This would need base price calculation
      return 0;
    }
    return 0;
  };

  const handleOptionToggle = (option: CarRentalOption) => {
    const existingIndex = selectedOptions.findIndex(opt => opt.id === option.id);
    
    if (existingIndex >= 0) {
      // Remove option
      const newOptions = selectedOptions.filter(opt => opt.id !== option.id);
      onOptionsChange(newOptions);
    } else {
      // Add option
      const newOptions = [...selectedOptions, {
        id: option.id,
        quantity: 1,
        name: option.name,
        price: parseFloat(option.price),
        price_type: option.price_type,
        price_percentage: option.price_percentage,
        description: option.description
      }];
      onOptionsChange(newOptions);
    }
  };

  const handleQuantityChange = (optionId: string, quantity: number) => {
    const option = options.find(opt => opt.id === optionId);
    if (!option) return;

    const maxQuantity = option.max_quantity || 1;
    const newQuantity = Math.max(0, Math.min(quantity, maxQuantity));

    if (newQuantity === 0) {
      // Remove option
      const newOptions = selectedOptions.filter(opt => opt.id !== optionId);
      onOptionsChange(newOptions);
    } else {
      // Update quantity
      const newOptions = selectedOptions.map(opt => 
        opt.id === optionId 
          ? { ...opt, quantity: newQuantity, price: calculateOptionPrice(option, newQuantity) }
          : opt
      );
      onOptionsChange(newOptions);
    }
  };

  const getTotalOptionsPrice = () => {
    return selectedOptions.reduce((total, option) => total + (typeof option.price === 'string' ? parseFloat(option.price) : option.price || 0), 0);
  };

  const getInsurancePrice = () => {
    if (carRentalData?.comprehensive_insurance_price) {
      return parseFloat(carRentalData.comprehensive_insurance_price);
    }
    return 0;
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
          {t('selectOptions')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {t('selectOptionsDesc')}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Available Options */}
        <Card>
          <CardHeader>
            <CardTitle>{t('availableOptions')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {options.length > 0 ? (
              options.map((option) => {
                const isSelected = selectedOptions.some(opt => opt.id === option.id);
                const selectedOption = selectedOptions.find(opt => opt.id === option.id);
                const quantity = selectedOption?.quantity || 0;

                return (
                  <div key={option.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          {option.name}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {option.description}
                        </p>
                      </div>
                      <div className="text-right ml-4">
                        <div className="text-lg font-bold text-gray-900 dark:text-white">
                          {formatPrice(calculateOptionPrice(option, 1), currency)}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {option.price_type === 'daily' ? t('perDay') : t('oneTime')}
                        </div>
                      </div>
                    </div>

                    {isSelected && (
                      <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          {t('quantity')}:
                        </span>
                        <div className="flex items-center space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleQuantityChange(option.id, quantity - 1)}
                            disabled={quantity <= 0}
                          >
                            <Minus className="w-4 h-4" />
                          </Button>
                          <span className="w-8 text-center text-sm font-medium">
                            {quantity}
                          </span>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleQuantityChange(option.id, quantity + 1)}
                            disabled={quantity >= (option.max_quantity || 1)}
                          >
                            <Plus className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    )}

                    <Button
                      variant={isSelected ? "default" : "outline"}
                      size="sm"
                      onClick={() => handleOptionToggle(option)}
                      className="w-full mt-3"
                    >
                      {isSelected ? t('remove') : t('add')}
                    </Button>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                {t('noOptionsAvailable')}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Insurance & Summary */}
        <div className="space-y-6">
          {/* Insurance Options */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="w-5 h-5 mr-2 text-blue-600" />
                {t('insuranceOptions')}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={basicInsurance}
                    onChange={(e) => onInsuranceChange(e.target.checked, comprehensiveInsurance)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <div className="ml-3">
                    <div className="font-medium text-gray-900 dark:text-white">
                      {t('basicInsurance')}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {t('basicInsuranceDesc')}
                    </div>
                  </div>
                </div>
                <span className="text-green-600 font-medium">{t('included')}</span>
              </div>

              <div className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={comprehensiveInsurance}
                    onChange={(e) => onInsuranceChange(basicInsurance, e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <div className="ml-3">
                    <div className="font-medium text-gray-900 dark:text-white">
                      {t('comprehensiveInsurance')}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {t('comprehensiveInsuranceDesc')}
                    </div>
                  </div>
                </div>
                <span className="text-gray-900 dark:text-white font-medium">
                  {formatPrice(getInsurancePrice(), currency)}/day
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Options Summary */}
          <Card>
            <CardHeader>
              <CardTitle>{t('optionsSummary')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
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
                
                {comprehensiveInsurance && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">
                      {t('comprehensiveInsurance')}
                    </span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {formatPrice(getInsurancePrice(), currency)}
                    </span>
                  </div>
                )}
                
                {selectedOptions.length === 0 && !comprehensiveInsurance && (
                  <div className="text-center py-4 text-gray-500 dark:text-gray-400">
                    {t('noOptionsSelected')}
                  </div>
                )}

                <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
                  <div className="flex justify-between font-bold text-lg">
                    <span>{t('total')}</span>
                    <span>{formatPrice(getTotalOptionsPrice() + (comprehensiveInsurance ? getInsurancePrice() : 0), currency)}</span>
                  </div>
                </div>
              </div>
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
