/**
 * Unified customer information form component.
 */

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useCustomerData } from '../../lib/hooks/useCustomerData';
import { CustomerInfo } from '../../lib/services/CustomerDataService';
import { Button } from '../ui/Button';

interface CustomerInfoFormProps {
  initialData?: Partial<CustomerInfo>;
  onSave?: (data: CustomerInfo) => void;
  onNext?: (data: CustomerInfo) => void;
  showSaveButton?: boolean;
  showNextButton?: boolean;
  className?: string;
}

export const CustomerInfoForm: React.FC<CustomerInfoFormProps> = ({
  initialData,
  onSave,
  onNext,
  showSaveButton = false,
  showNextButton = true,
  className = ''
}) => {
  const t = useTranslations('checkout');
  const { customerData, isLoading, error, saveCustomerData } = useCustomerData();
  
  const [formData, setFormData] = useState<CustomerInfo>({
    full_name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    country: '',
    postal_code: '',
    special_requests: ''
  });

  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  // Initialize form data
  useEffect(() => {
    if (customerData) {
      setFormData({ ...customerData, ...initialData });
    }
  }, [customerData, initialData]);

  const handleInputChange = (field: keyof CustomerInfo, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setValidationErrors([]);
  };

  const validateForm = (): boolean => {
    const errors: string[] = [];

    if (!formData.full_name.trim()) {
      errors.push(t('fullName') + ' ' + t('isRequired'));
    }

    if (!formData.email.trim()) {
      errors.push(t('email') + ' ' + t('isRequired'));
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.push(t('invalidEmail'));
    }

    if (!formData.phone.trim()) {
      errors.push(t('phone') + ' ' + t('isRequired'));
    }

    if (!formData.address.trim()) {
      errors.push(t('address') + ' ' + t('isRequired'));
    }

    setValidationErrors(errors);
    return errors.length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    try {
      await saveCustomerData(formData);
      onSave?.(formData);
    } catch (err) {
      console.error('Error saving customer data:', err);
    }
  };

  const handleNext = () => {
    if (!validateForm()) return;
    onNext?.(formData);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <ul className="text-red-600 text-sm space-y-1">
            {validationErrors.map((error, index) => (
              <li key={index}>• {error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Form Fields */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Full Name */}
        <div className="md:col-span-2">
          <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
            {t('fullName')} *
          </label>
          <input
            type="text"
            id="full_name"
            value={formData.full_name}
            onChange={(e) => handleInputChange('full_name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t('fullName')}
            required
          />
        </div>

        {/* Email */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
            {t('email')} *
          </label>
          <input
            type="email"
            id="email"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t('email')}
            required
          />
        </div>

        {/* Phone */}
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
            {t('phone')} *
          </label>
          <input
            type="tel"
            id="phone"
            value={formData.phone}
            onChange={(e) => handleInputChange('phone', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t('phone')}
            required
          />
        </div>

        {/* Address */}
        <div className="md:col-span-2">
          <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
            {t('address')} *
          </label>
          <textarea
            id="address"
            value={formData.address}
            onChange={(e) => handleInputChange('address', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t('address')}
            rows={3}
            required
          />
        </div>

        {/* City */}
        <div>
          <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-2">
            {t('city')}
          </label>
          <input
            type="text"
            id="city"
            value={formData.city}
            onChange={(e) => handleInputChange('city', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t('city')}
          />
        </div>

        {/* Country */}
        <div>
          <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-2">
            {t('country')}
          </label>
          <input
            type="text"
            id="country"
            value={formData.country}
            onChange={(e) => handleInputChange('country', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t('country')}
          />
        </div>

        {/* Postal Code */}
        <div>
          <label htmlFor="postal_code" className="block text-sm font-medium text-gray-700 mb-2">
            {t('postalCode')}
          </label>
          <input
            type="text"
            id="postal_code"
            value={formData.postal_code}
            onChange={(e) => handleInputChange('postal_code', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t('postalCode')}
          />
        </div>

        {/* Special Requests */}
        <div className="md:col-span-2">
          <label htmlFor="special_requests" className="block text-sm font-medium text-gray-700 mb-2">
            {t('specialRequests')}
          </label>
          <textarea
            id="special_requests"
            value={formData.special_requests}
            onChange={(e) => handleInputChange('special_requests', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={t('specialRequestsPlaceholder')}
            rows={3}
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-4">
        {showSaveButton && (
          <Button
            type="button"
            onClick={handleSave}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? t('saving') : t('save')}
          </Button>
        )}
        
        {showNextButton && (
          <Button
            type="button"
            onClick={handleNext}
            disabled={isLoading}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {isLoading ? t('processing') : t('next')}
          </Button>
        )}
      </div>
    </div>
  );
};
