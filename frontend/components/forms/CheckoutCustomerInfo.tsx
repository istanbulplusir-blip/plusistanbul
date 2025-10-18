/**
 * Improved checkout customer information form.
 * Shows read-only profile data and allows only special requests.
 */

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useCustomerData } from '../../lib/hooks/useCustomerData';
import { useAuth } from '../../lib/contexts/AuthContext';
import {
  User,
  Mail,
  Phone,
  MapPin,
  AlertCircle,
  CheckCircle,
  Edit3
} from 'lucide-react';

interface CheckoutCustomerInfoProps {
  onSpecialRequestsChange?: (requests: string) => void;
  className?: string;
}

export const CheckoutCustomerInfo: React.FC<CheckoutCustomerInfoProps> = ({
  onSpecialRequestsChange,
  className = ''
}) => {
  const t = useTranslations('checkout');
  const { customerData, isLoading } = useCustomerData();
  const { user, isAuthenticated } = useAuth();

  const [specialRequests, setSpecialRequests] = useState('');
  const [profileIncomplete, setProfileIncomplete] = useState(false);
  const [missingFields, setMissingFields] = useState<string[]>([]);

  // Check profile completeness
  useEffect(() => {
    if (customerData && user) {
      const missing: string[] = [];

      // Check required fields based on authentication method
      if (!customerData.full_name?.trim()) {
        missing.push(t('fullName'));
      }

      // Phone is required only if user is not verified via OAuth or email OTP
      // For OAuth users (Google login), phone is not required
      // For email OTP users, phone is not required
      // Check if user is OAuth (Google) or email-only OTP user
      // const isOAuthUser = user.is_email_verified && !user.phone_number;
      // const isEmailOTPUser = user.is_email_verified && !user.is_phone_verified;

      // Phone is not required for OAuth users or email-only OTP users
      // Skip phone requirement for OAuth and email OTP users
      // Temporarily disable phone requirement for all users
      // TODO: Re-enable based on proper user type detection
      // const requiresPhone = !isOAuthUser && !isEmailOTPUser;
      // if (requiresPhone && !customerData.phone?.trim()) {
      //   missing.push(t('phoneNumber'));
      // }

      setMissingFields(missing);
      setProfileIncomplete(missing.length > 0);
    }
  }, [customerData, user]);

  const handleSpecialRequestsChange = (value: string) => {
    setSpecialRequests(value);
    onSpecialRequestsChange?.(value);
  };

  const getVerificationStatus = () => {
    if (!user) return null;

    // OAuth users (Google login) - email verified, no phone
    if (user.is_email_verified && !user.phone_number) {
      return {
        type: 'oauth',
        message: t('authenticatedWithGoogle'),
        icon: <CheckCircle className="h-4 w-4 text-green-600" />
      };
    }

    // Fully verified users
    if (user.is_email_verified && user.is_phone_verified) {
      return {
        type: 'full',
        message: t('emailAndPhoneVerified'),
        icon: <CheckCircle className="h-4 w-4 text-green-600" />
      };
    }

    // Email verified only
    if (user.is_email_verified) {
      return {
        type: 'email',
        message: t('emailVerified'),
        icon: <CheckCircle className="h-4 w-4 text-blue-600" />
      };
    }

    // Authenticated but email not verified
    return {
      type: 'unverified',
      message: t('emailNotVerified'),
      icon: <AlertCircle className="h-4 w-4 text-yellow-600" />
    };
  };

  const verificationStatus = getVerificationStatus();

  if (!isAuthenticated || !user) {
    return (
      <div className={`bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2 text-red-800 dark:text-red-200">
          <AlertCircle className="h-5 w-5" />
          <p className="font-medium">{t('loginRequired')}</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className={`bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/4 mb-2"></div>
          <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Verification Status */}
      {verificationStatus && (
        <div className={`rounded-lg p-4 ${verificationStatus.type === 'unverified'
            ? 'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700'
            : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700'
          }`}>
          <div className="flex items-center justify-between gap-2">
            <div className={`flex items-center gap-2 ${verificationStatus.type === 'unverified'
                ? 'text-yellow-800 dark:text-yellow-200'
                : 'text-blue-800 dark:text-blue-200'
              }`}>
              {verificationStatus.icon}
              <p className="font-medium">{verificationStatus.message}</p>
            </div>
            {verificationStatus.type === 'unverified' && (
              <p className="text-sm text-yellow-700 dark:text-yellow-300">
                {t('checkoutAllowedWithoutVerification')}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Profile Incomplete Warning */}
      {profileIncomplete && (
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg p-4">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5" />
            <div>
              <p className="font-medium text-amber-800 dark:text-amber-200 mb-1">
                {t('profileIncomplete')}
              </p>
              <p className="text-sm text-amber-700 dark:text-amber-300 mb-2">
                {t('missingFieldsInProfile')}:
              </p>
              <ul className="text-sm text-amber-700 dark:text-amber-300 list-disc list-inside">
                {missingFields.map((field, index) => (
                  <li key={index}>{field}</li>
                ))}
              </ul>
              <p className="text-sm text-amber-700 dark:text-amber-300 mt-2">
                {t('pleaseEnterInSpecialRequests')}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Customer Information Display */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <User className="h-5 w-5" />
          {t('customerInformation')}
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Full Name */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('fullName')}
            </label>
            <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
              <User className="h-4 w-4 text-gray-500 dark:text-gray-400" />
              <span className="text-gray-900 dark:text-gray-100">
                {customerData?.full_name || t('unknown')}
              </span>
              {!customerData?.full_name && (
                <span className="text-red-500 dark:text-red-400 text-sm">({t('required')})</span>
              )}
            </div>
          </div>

          {/* Email */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('email')}
            </label>
            <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
              <Mail className="h-4 w-4 text-gray-500 dark:text-gray-400" />
              <span className="text-gray-900 dark:text-gray-100">{user.email}</span>
              {user.is_email_verified && (
                <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
              )}
            </div>
          </div>

          {/* Phone */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {t('phoneNumber')}
            </label>
            <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
              <Phone className="h-4 w-4 text-gray-500 dark:text-gray-400" />
              <span className="text-gray-900 dark:text-gray-100">
                {customerData?.phone || user.phone_number || t('unknown')}
              </span>
              {!customerData?.phone && !user.phone_number && (
                <span className="text-red-500 dark:text-red-400 text-sm">({t('required')})</span>
              )}
              {user.is_phone_verified && (
                <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
              )}
            </div>
          </div>

          {/* City */}
          {customerData?.city && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {t('city')}
              </label>
              <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                <MapPin className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <span className="text-gray-900 dark:text-gray-100">{customerData.city}</span>
              </div>
            </div>
          )}

          {/* Country */}
          {customerData?.country && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                {t('country')}
              </label>
              <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                <MapPin className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                <span className="text-gray-900 dark:text-gray-100">{customerData.country}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Special Requests */}
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
          <Edit3 className="h-5 w-5" />
          {t('specialRequests')}
        </h3>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {profileIncomplete
              ? t('completeInfoAndSpecialRequests')
              : t('specialRequestsOrAdditionalInfo')
            }
          </label>
          <textarea
            value={specialRequests}
            onChange={(e) => handleSpecialRequestsChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder:text-gray-500 dark:placeholder:text-gray-400 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder={
              profileIncomplete
                ? `${t('pleaseEnterMissingInfo')}:\n- ${missingFields.join('\n- ')}\n\n${t('andAnyOtherRequests')}`
                : t('anySpecialRequestsPlaceholder')
            }
            rows={4}
          />
          {profileIncomplete && (
            <p className="text-sm text-amber-600 dark:text-amber-400">
              ⚠️ {t('pleaseEnterMissingProfileInfo')}
            </p>
          )}
        </div>
      </div>

      {/* Information Note */}
      <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <AlertCircle className="h-5 w-5 text-gray-500 dark:text-gray-400 mt-0.5" />
          <div className="text-sm text-gray-600 dark:text-gray-300">
            <p className="font-medium mb-1">{t('infoNoteTitle')}</p>
            <p>
              {t('infoNoteDescription')}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
