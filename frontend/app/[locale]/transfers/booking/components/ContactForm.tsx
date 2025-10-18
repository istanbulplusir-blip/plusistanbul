'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { User, Phone, MessageSquare, ArrowRight, ArrowLeft } from 'lucide-react';
import { useTransferBookingStore } from '@/lib/stores/transferBookingStore';
import { useAuth } from '@/lib/contexts/AuthContext';
import { UI_CLASSES } from '@/lib/constants/ui';

interface ContactFormProps {
  onNext: () => void;
  onBack: () => void;
}

export default function ContactForm({ onNext, onBack }: ContactFormProps) {
  const t = useTranslations('transfers');
  const { user, isAuthenticated } = useAuth();
  
  // Get booking state from store
  const {
    route_data,
    contact_name,
    contact_phone,
    special_requirements,
    setContact,
  } = useTransferBookingStore();

  // Local state for form inputs
  const [localContactName, setLocalContactName] = useState(contact_name || '');
  const [localContactPhone, setLocalContactPhone] = useState(contact_phone || '');
  const [localSpecialRequirements, setLocalSpecialRequirements] = useState(special_requirements || '');

  // Auto-fill user data if logged in
  useEffect(() => {
    if (isAuthenticated && user) {
      if (!localContactName) {
        setLocalContactName(`${user.first_name} ${user.last_name}`.trim());
      }
      if (!localContactPhone && user.phone_number) {
        setLocalContactPhone(user.phone_number);
      }
    }
  }, [isAuthenticated, user, localContactName, localContactPhone]);

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isValid) {
      setContact({
        contact_name: localContactName,
        contact_phone: localContactPhone,
        special_requirements: localSpecialRequirements,
      });
      onNext();
    }
  };

  // Check if form is valid - only name and phone are required
  const isValid = localContactName.trim() && localContactPhone.trim();

  if (!route_data) {
    return (
      <div className={UI_CLASSES.container}>
        <div className={UI_CLASSES.pageHeader}>
          <h2 className={UI_CLASSES.title}>
            {t('contactInformation')}
          </h2>
          <p className={UI_CLASSES.description}>
            {t('step6')}
          </p>
        </div>

        <div className={UI_CLASSES.cardLarge}>
          <div className={UI_CLASSES.textCenter}>
            <User className={`${UI_CLASSES.iconLarge} text-gray-400 mx-auto mb-4`} />
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          {t('contactInformation')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {t('step6')}
        </p>
        
        {/* Route Info */}
        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="flex items-center gap-2 text-blue-800 dark:text-blue-200 mb-2">
            <span className="font-medium">{route_data.origin}</span>
            <ArrowRight className="w-4 h-4" />
            <span className="font-medium">{route_data.destination}</span>
          </div>
          <div className="text-sm text-blue-700 dark:text-blue-300">
            {route_data.pricing?.length || 0} {t('vehicleType')} {t('available')}
          </div>
        </div>

        {/* User Info Notice */}
        {isAuthenticated && user && (
          <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-600 rounded-lg">
            <div className="flex items-center gap-2 text-green-800 dark:text-green-200">
              <User className="w-4 h-4" />
              <span className="text-sm font-medium">
                {t('userDataAutoFilled')}
              </span>
            </div>
            <p className="text-xs text-green-700 dark:text-green-300 mt-1">
              {t('userDataAutoFilledDescription')}
            </p>
          </div>
        )}
      </div>

      {/* Contact Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Contact Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('contactName')} *
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                value={localContactName}
                onChange={(e) => setLocalContactName(e.target.value)}
                placeholder={t('contactNamePlaceholder')}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-800"
                required
              />
            </div>
          </div>

          {/* Contact Phone (WhatsApp) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('whatsappNumber')} *
            </label>
            <div className="relative">
              <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="tel"
                value={localContactPhone}
                onChange={(e) => setLocalContactPhone(e.target.value)}
                placeholder={t('whatsappNumberPlaceholder')}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-800"
                required
              />
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {t('whatsappNumberHelp')}
            </p>
          </div>

          {/* Special Requirements */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('specialRequirements')}
            </label>
            <div className="relative">
              <MessageSquare className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
              <textarea
                value={localSpecialRequirements}
                onChange={(e) => setLocalSpecialRequirements(e.target.value)}
                placeholder={t('specialRequirementsPlaceholder')}
                rows={4}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-gray-800 resize-none"
              />
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {t('specialRequirementsHelp')}
            </p>
          </div>
        </form>
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
            onClick={handleSubmit}
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