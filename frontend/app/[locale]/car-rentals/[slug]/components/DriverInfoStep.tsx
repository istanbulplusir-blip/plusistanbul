'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import { User, CreditCard, Plus, X } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

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

interface DriverInfoStepProps {
  driverInfo: DriverInfo;
  onDriverInfoChange: (info: DriverInfo) => void;
  onNext: () => void;
  onBack?: () => void;
  isLoading?: boolean;
  errors?: {
    driver_name?: string;
    driver_license?: string;
    driver_phone?: string;
    driver_email?: string;
    additional_drivers?: string;
  };
}

export default function DriverInfoStep({
  driverInfo,
  onDriverInfoChange,
  onNext,
  onBack,
  isLoading = false,
  errors = {}
}: DriverInfoStepProps) {
  const t = useTranslations('carRentalBooking');
  const [isValid, setIsValid] = useState(false);

  // Validate form
  useEffect(() => {
    const valid = !!(
      driverInfo.driver_name.trim() &&
      driverInfo.driver_license.trim() &&
      driverInfo.driver_phone.trim() &&
      driverInfo.driver_email.trim() &&
      driverInfo.additional_drivers.every(driver => 
        driver.name.trim() && driver.license.trim() && driver.phone.trim()
      )
    );
    setIsValid(valid);
  }, [driverInfo]);

  const handleMainDriverChange = (field: keyof Omit<DriverInfo, 'additional_drivers'>, value: string) => {
    onDriverInfoChange({
      ...driverInfo,
      [field]: value
    });
  };

  const handleAdditionalDriverChange = (index: number, field: 'name' | 'license' | 'phone', value: string) => {
    const newAdditionalDrivers = [...driverInfo.additional_drivers];
    newAdditionalDrivers[index] = {
      ...newAdditionalDrivers[index],
      [field]: value
    };
    onDriverInfoChange({
      ...driverInfo,
      additional_drivers: newAdditionalDrivers
    });
  };

  const addAdditionalDriver = () => {
    onDriverInfoChange({
      ...driverInfo,
      additional_drivers: [
        ...driverInfo.additional_drivers,
        { name: '', license: '', phone: '' }
      ]
    });
  };

  const removeAdditionalDriver = (index: number) => {
    const newAdditionalDrivers = driverInfo.additional_drivers.filter((_, i) => i !== index);
    onDriverInfoChange({
      ...driverInfo,
      additional_drivers: newAdditionalDrivers
    });
  };

  const handleNext = () => {
    if (isValid) {
      onNext();
    }
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
          {t('driverInformation')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {t('driverInformationDesc')}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Main Driver Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="w-5 h-5 mr-2 text-blue-600" />
              {t('mainDriver')}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('fullName')} *
              </label>
              <Input
                type="text"
                placeholder={t('fullNamePlaceholder')}
                value={driverInfo.driver_name}
                onChange={(e) => handleMainDriverChange('driver_name', e.target.value)}
                className={errors.driver_name ? 'border-red-500' : ''}
              />
              {errors.driver_name && (
                <p className="text-red-500 text-sm mt-1">{errors.driver_name}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('driverLicense')} *
              </label>
              <Input
                type="text"
                placeholder={t('driverLicensePlaceholder')}
                value={driverInfo.driver_license}
                onChange={(e) => handleMainDriverChange('driver_license', e.target.value)}
                className={errors.driver_license ? 'border-red-500' : ''}
              />
              {errors.driver_license && (
                <p className="text-red-500 text-sm mt-1">{errors.driver_license}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('phoneNumber')} *
              </label>
              <Input
                type="tel"
                placeholder={t('phoneNumberPlaceholder')}
                value={driverInfo.driver_phone}
                onChange={(e) => handleMainDriverChange('driver_phone', e.target.value)}
                className={errors.driver_phone ? 'border-red-500' : ''}
              />
              {errors.driver_phone && (
                <p className="text-red-500 text-sm mt-1">{errors.driver_phone}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('emailAddress')} *
              </label>
              <Input
                type="email"
                placeholder={t('emailAddressPlaceholder')}
                value={driverInfo.driver_email}
                onChange={(e) => handleMainDriverChange('driver_email', e.target.value)}
                className={errors.driver_email ? 'border-red-500' : ''}
              />
              {errors.driver_email && (
                <p className="text-red-500 text-sm mt-1">{errors.driver_email}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Additional Drivers */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center">
                <User className="w-5 h-5 mr-2 text-green-600" />
                {t('additionalDrivers')}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={addAdditionalDriver}
                className="flex items-center"
              >
                <Plus className="w-4 h-4 mr-1" />
                {t('addDriver')}
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {driverInfo.additional_drivers.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                <User className="w-12 h-12 mx-auto mb-4 text-gray-300 dark:text-gray-600" />
                <p>{t('noAdditionalDrivers')}</p>
                <p className="text-sm">{t('noAdditionalDriversDesc')}</p>
              </div>
            ) : (
              driverInfo.additional_drivers.map((driver, index) => (
                <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {t('driver')} {index + 1}
                    </h4>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeAdditionalDriver(index)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {t('fullName')} *
                      </label>
                      <Input
                        type="text"
                        placeholder={t('fullNamePlaceholder')}
                        value={driver.name}
                        onChange={(e) => handleAdditionalDriverChange(index, 'name', e.target.value)}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {t('driverLicense')} *
                      </label>
                      <Input
                        type="text"
                        placeholder={t('driverLicensePlaceholder')}
                        value={driver.license}
                        onChange={(e) => handleAdditionalDriverChange(index, 'license', e.target.value)}
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {t('phoneNumber')} *
                      </label>
                      <Input
                        type="tel"
                        placeholder={t('phoneNumberPlaceholder')}
                        value={driver.phone}
                        onChange={(e) => handleAdditionalDriverChange(index, 'phone', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              ))
            )}

            {errors.additional_drivers && (
              <p className="text-red-500 text-sm">{errors.additional_drivers}</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Important Notes */}
      <Card className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800">
        <CardContent className="pt-6">
          <div className="flex items-start">
            <CreditCard className="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
            <div>
              <h4 className="font-medium text-yellow-800 dark:text-yellow-200 mb-2">
                {t('importantNotes')}
              </h4>
              <ul className="text-sm text-yellow-700 dark:text-yellow-300 space-y-1">
                <li>• {t('licenseRequirement')}</li>
                <li>• {t('ageRequirement')}</li>
                <li>• {t('documentRequirement')}</li>
                <li>• {t('additionalDriverNote')}</li>
              </ul>
            </div>
          </div>
        </CardContent>
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
          onClick={handleNext}
          disabled={!isValid || isLoading}
          className="ml-auto"
        >
          {isLoading ? t('loading') : t('next')}
        </Button>
      </div>
    </motion.div>
  );
}
