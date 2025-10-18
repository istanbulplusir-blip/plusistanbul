'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useLocale } from 'next-intl';
import { cn } from '@/lib/utils';
import { AgentCustomer } from '@/lib/types/api';

interface CustomerFormProps {
  customer?: AgentCustomer | null;
  onSubmit: (data: Record<string, unknown>) => void;
  onCancel: () => void;
  loading?: boolean;
}

export default function CustomerForm({
  customer,
  onSubmit,
  onCancel,
  loading = false
}: CustomerFormProps) {
  const t = useTranslations('agent');
  const locale = useLocale();
  const isRTL = locale === 'fa';

  const [formData, setFormData] = useState({
    email: customer?.email || '',
    first_name: customer?.name?.split(' ')[0] || '',
    last_name: customer?.name?.split(' ').slice(1).join(' ') || '',
    phone: customer?.phone || '',
    address: customer?.address || '',
    city: customer?.city || '',
    country: customer?.country || '',
    birth_date: customer?.birth_date || '',
    gender: customer?.gender || '',
    preferred_language: customer?.preferred_language || 'fa',
    preferred_contact_method: customer?.preferred_contact_method || 'email',
    customer_status: customer?.status || 'active',
    customer_tier: customer?.tier || 'bronze',
    relationship_notes: '',
    special_requirements: '',
    marketing_consent: false,
    // Authentication options
    send_credentials: true,
    verification_method: 'email' as 'email' | 'sms' | 'both',
    welcome_message: '',
    custom_instructions: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateEmail = (email: string): string | null => {
    if (!email.trim()) {
      return t('validation.emailRequired');
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return t('validation.invalidEmail');
    }
    return null;
  };

  const validatePhone = (phone: string): string | null => {
    if (!phone.trim()) return null; // Phone is optional
    
    // Enhanced phone validation for international numbers
    const phoneRegex = /^[\+]?[1-9][0-9\s\-\(\)]{7,15}$/;
    if (!phoneRegex.test(phone)) {
      return t('validation.invalidPhone');
    }
    return null;
  };

  const validateName = (name: string, fieldName: string): string | null => {
    if (!name.trim()) {
      return t(`validation.${fieldName}Required`);
    }
    if (name.trim().length < 2) {
      return t(`validation.${fieldName}TooShort`);
    }
    if (name.trim().length > 50) {
      return t(`validation.${fieldName}TooLong`);
    }
    return null;
  };

  const validateBirthDate = (date: string): string | null => {
    if (!date) return null; // Birth date is optional
    
    const birthDate = new Date(date);
    const today = new Date();
    const age = today.getFullYear() - birthDate.getFullYear();
    
    if (age < 0) {
      return t('validation.futureDate');
    }
    if (age > 120) {
      return t('validation.invalidAge');
    }
    return null;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Enhanced validation
    const newErrors: Record<string, string> = {};
    
    // Email validation
    const emailError = validateEmail(formData.email);
    if (emailError) newErrors.email = emailError;
    
    // Name validation
    const firstNameError = validateName(formData.first_name, 'firstName');
    if (firstNameError) newErrors.first_name = firstNameError;
    
    const lastNameError = validateName(formData.last_name, 'lastName');
    if (lastNameError) newErrors.last_name = lastNameError;
    
    // Phone validation
    const phoneError = validatePhone(formData.phone);
    if (phoneError) newErrors.phone = phoneError;
    
    // Birth date validation
    const birthDateError = validateBirthDate(formData.birth_date);
    if (birthDateError) newErrors.birth_date = birthDateError;
    
    // Address validation (if provided)
    if (formData.address && formData.address.trim().length < 10) {
      newErrors.address = t('validation.addressTooShort');
    }
    
    // City validation (if provided)
    if (formData.city && formData.city.trim().length < 2) {
      newErrors.city = t('validation.cityTooShort');
    }
    
    setErrors(newErrors);
    
    if (Object.keys(newErrors).length === 0) {
      onSubmit(formData);
    }
  };

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Name Fields */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('customers.firstName')} *
          </label>
          <input
            type="text"
            value={formData.first_name}
            onChange={(e) => handleInputChange('first_name', e.target.value)}
            className={cn(
              "w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              errors.first_name ? "border-red-300 dark:border-red-600" : "border-gray-300 dark:border-gray-600",
              isRTL && "text-right"
            )}
            placeholder="Enter first name"
          />
          {errors.first_name && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">
              {errors.first_name}
            </p>
          )}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('customers.lastName')} *
          </label>
          <input
            type="text"
            value={formData.last_name}
            onChange={(e) => handleInputChange('last_name', e.target.value)}
            className={cn(
              "w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              errors.last_name ? "border-red-300 dark:border-red-600" : "border-gray-300 dark:border-gray-600",
              isRTL && "text-right"
            )}
            placeholder="Enter last name"
          />
          {errors.last_name && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">
              {errors.last_name}
            </p>
          )}
        </div>
      </div>

      {/* Email */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('customers.email')} *
        </label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => handleInputChange('email', e.target.value)}
          className={cn(
            "w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
            errors.email ? "border-red-300 dark:border-red-600" : "border-gray-300 dark:border-gray-600",
            isRTL && "text-right"
          )}
          placeholder="Enter email address"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            {errors.email}
          </p>
        )}
      </div>

      {/* Phone */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('customers.phone')}
        </label>
        <input
          type="tel"
          value={formData.phone}
          onChange={(e) => handleInputChange('phone', e.target.value)}
          className={cn(
            "w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
            errors.phone ? "border-red-300 dark:border-red-600" : "border-gray-300 dark:border-gray-600",
            isRTL && "text-right"
          )}
          placeholder="Enter phone number"
        />
        {errors.phone && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            {errors.phone}
          </p>
        )}
      </div>

      {/* Address */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('customers.address')}
        </label>
        <textarea
          value={formData.address}
          onChange={(e) => handleInputChange('address', e.target.value)}
          rows={3}
          className={cn(
            "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
            isRTL && "text-right"
          )}
          placeholder="Enter address"
        />
      </div>

      {/* City and Country */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('customers.city')}
          </label>
          <input
            type="text"
            value={formData.city}
            onChange={(e) => handleInputChange('city', e.target.value)}
            className={cn(
              "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              isRTL && "text-right"
            )}
            placeholder="Enter city"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('customers.country')}
          </label>
          <input
            type="text"
            value={formData.country}
            onChange={(e) => handleInputChange('country', e.target.value)}
            className={cn(
              "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
              isRTL && "text-right"
            )}
            placeholder="Enter country"
          />
        </div>
      </div>

      {/* Birth Date and Gender */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('customers.birthDate')}
          </label>
          <input
            type="date"
            value={formData.birth_date}
            onChange={(e) => handleInputChange('birth_date', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('customers.gender')}
          </label>
          <select
            value={formData.gender}
            onChange={(e) => handleInputChange('gender', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">{t('customers.selectGender')}</option>
            <option value="male">{t('customers.male')}</option>
            <option value="female">{t('customers.female')}</option>
            <option value="other">{t('customers.other')}</option>
          </select>
        </div>
      </div>

      {/* Preferences */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('customers.preferredLanguage')}
          </label>
          <select
            value={formData.preferred_language}
            onChange={(e) => handleInputChange('preferred_language', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="fa">{t('customers.persian')}</option>
            <option value="en">{t('customers.english')}</option>
            <option value="ar">{t('customers.arabic')}</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('customers.preferredContactMethod')}
          </label>
          <select
            value={formData.preferred_contact_method}
            onChange={(e) => handleInputChange('preferred_contact_method', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="email">{t('customers.email')}</option>
            <option value="phone">{t('customers.phone')}</option>
            <option value="whatsapp">{t('customers.whatsapp')}</option>
            <option value="sms">{t('customers.sms')}</option>
          </select>
        </div>
      </div>

      {/* Status and Tier */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('customers.status')}
          </label>
          <select
            value={formData.customer_status}
            onChange={(e) => handleInputChange('customer_status', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="active">{t('customers.filters.active')}</option>
            <option value="inactive">{t('customers.filters.inactive')}</option>
            <option value="vip">{t('customers.filters.vip')}</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {t('customers.tier')}
          </label>
          <select
            value={formData.customer_tier}
            onChange={(e) => handleInputChange('customer_tier', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="bronze">{t('customers.filters.bronze')}</option>
            <option value="silver">{t('customers.filters.silver')}</option>
            <option value="gold">{t('customers.filters.gold')}</option>
            <option value="platinum">{t('customers.filters.platinum')}</option>
          </select>
        </div>
      </div>

      {/* Authentication Options */}
      <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
          {t('customers.authenticationOptions')}
        </h4>

        <div className="space-y-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="send_credentials"
              checked={formData.send_credentials}
              onChange={(e) => handleInputChange('send_credentials', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label
              htmlFor="send_credentials"
              className="ml-2 block text-sm text-gray-900 dark:text-white"
            >
              {t('customers.sendCredentials')}
            </label>
          </div>

          {formData.send_credentials && (
            <div className="ml-6 space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('customers.verificationMethod')}
                </label>
                <select
                  value={formData.verification_method}
                  onChange={(e) => handleInputChange('verification_method', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="email">{t('customers.email')}</option>
                  <option value="sms">{t('customers.sms')}</option>
                  <option value="both">{t('customers.both')}</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('customers.welcomeMessage')}
                </label>
                <textarea
                  value={formData.welcome_message}
                  onChange={(e) => handleInputChange('welcome_message', e.target.value)}
                  rows={3}
                  placeholder={t('customers.welcomeMessagePlaceholder')}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('customers.customInstructions')}
                </label>
                <textarea
                  value={formData.custom_instructions}
                  onChange={(e) => handleInputChange('custom_instructions', e.target.value)}
                  rows={2}
                  placeholder={t('customers.customInstructionsPlaceholder')}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Notes */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('customers.relationshipNotes')}
        </label>
        <textarea
          value={formData.relationship_notes}
          onChange={(e) => handleInputChange('relationship_notes', e.target.value)}
          rows={3}
          className={cn(
            "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
            isRTL && "text-right"
          )}
          placeholder={t('customers.relationshipNotesPlaceholder')}
        />
      </div>

      {/* Special Requirements */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {t('customers.specialRequirements')}
        </label>
        <textarea
          value={formData.special_requirements}
          onChange={(e) => handleInputChange('special_requirements', e.target.value)}
          rows={3}
          className={cn(
            "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white",
            isRTL && "text-right"
          )}
          placeholder={t('customers.specialRequirementsPlaceholder')}
        />
      </div>

      {/* Marketing Consent */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="marketing_consent"
          checked={formData.marketing_consent}
          onChange={(e) => handleInputChange('marketing_consent', e.target.checked)}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
        />
        <label htmlFor="marketing_consent" className={cn(
          "ml-2 block text-sm text-gray-900 dark:text-white",
          isRTL && "ml-0 mr-2"
        )}>
          {t('customers.marketingConsent')}
        </label>
      </div>

      {/* Form Actions */}
      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {t('customers.cancel')}
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? t('customers.saving') : (customer ? t('customers.update') : t('customers.create'))}
        </button>
      </div>
    </form>
  );
}
