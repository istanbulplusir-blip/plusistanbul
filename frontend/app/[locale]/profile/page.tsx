'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { useAuth } from '../../../lib/contexts/AuthContext';
import ProtectedRoute from '../../../components/ProtectedRoute';
import { 
  User, 
  Mail, 
  Phone, 
  Calendar, 
  Edit, 
  Save, 
  X,
  Key,
  LogOut,
  Package
} from 'lucide-react';
import { profileService, SensitiveFieldRequest, SensitiveFieldVerify } from '../../../lib/services/profileService';
import OTPModal from '../../../components/OTPModal';

import OrderHistory from '../../../components/OrderHistory';
import { useLocale } from 'next-intl';
import ChangePasswordModal from '../../../components/ChangePasswordModal';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';


interface ProfileData {
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  date_of_birth: string;
  city: string;
  country: string;
}

interface ExtendedUser {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone_number?: string;
  date_of_birth?: string;
  profile?: {
    city?: string;
    country?: string;
  };
  is_email_verified?: boolean;
  is_phone_verified?: boolean;
  created_at?: string;
}

export default function ProfilePage() {
  const router = useRouter();
  const t = useTranslations('profile');
  const { user, updateUser, logout } = useAuth();
  const locale = useLocale();
  
  const [profileData, setProfileData] = useState<ProfileData>({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    phone_number: user?.phone_number || '',
    date_of_birth: (user as ExtendedUser)?.date_of_birth || '',
    city: (user as ExtendedUser)?.profile?.city || '',
    country: (user as ExtendedUser)?.profile?.country || 'ایران',
  });
  
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // OTP Modal states
  const [showOTPModal, setShowOTPModal] = useState(false);
  const [otpField, setOtpField] = useState<string>('');
  const [otpNewValue, setOtpNewValue] = useState<string>('');
  const [otpMessage, setOtpMessage] = useState<string>('');
  const [isRequestingOTP, setIsRequestingOTP] = useState(false);

  const [showOtpMethodModal, setShowOtpMethodModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'profile' | 'orders'>('profile');

  // Add state for phone editing
  const [isEditingPhone, setIsEditingPhone] = useState(false);
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false);

  // Toast handler function
  const handleShowToast = (message: string, type: 'success' | 'error' | 'info') => {
    if (type === 'success') {
      setSuccess(message);
    } else if (type === 'error') {
      setError(message);
    }
    // For 'info' type, we can use success for now
    else {
      setSuccess(message);
    }
  };

  useEffect(() => {
    if (user) {
      setProfileData(prev => ({
        ...prev,
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone_number: user.phone_number || '',
        date_of_birth: (user as ExtendedUser)?.date_of_birth || '',
        city: (user as ExtendedUser)?.profile?.city || '',
        country: (user as ExtendedUser)?.profile?.country || 'ایران',
      }));
    }
  }, [user]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
    if (error) setError(null);
  };

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // Check for sensitive field changes
      const sensitiveFields = ['first_name', 'last_name', 'email', 'phone_number'];
      const changedSensitiveFields = sensitiveFields.filter(field => {
        const currentValue = user?.[field as keyof typeof user] || '';
        const newValue = profileData[field as keyof ProfileData];
        return currentValue !== newValue;
      });

      if (changedSensitiveFields.length > 0) {
        // Handle sensitive field changes with OTP
        await handleSensitiveFieldChange(changedSensitiveFields[0]);
        return;
      }

      // Update non-sensitive fields only
      const updateData = {
        user_data: {
          date_of_birth: profileData.date_of_birth,
        },
        profile: {
          city: profileData.city,
          country: profileData.country,
        }
      };

      const result = await profileService.updateBasicProfile(updateData);

      if (result.success && result.user) {
        updateUser(result.user);
        setSuccess(t('updateSuccess'));
        // Toast notification removed - using setSuccess instead
        setIsEditing(false);
      } else {
        setError(result.message || t('updateError'));
        // Toast notification removed - using setError instead
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : t('updateError');
      console.error('Profile update error:', err);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSensitiveFieldChange = async (field: string) => {
    setIsRequestingOTP(true);
    setError(null);

    try {
      // بررسی وضعیت تایید ایمیل و تلفن
      if (!user?.is_email_verified && !user?.is_phone_verified) {
        setError(t('verifyContactFirst'));
        setIsRequestingOTP(false);
        return;
      }
      // اگر هر دو تایید شده‌اند، انتخاب روش
      if (user?.is_email_verified && user?.is_phone_verified) {
        setShowOtpMethodModal(true);
        setIsRequestingOTP(false);
        return;
      }
      // اگر فقط یکی تایید شده
      const method: 'email' | 'phone_number' = user?.is_email_verified ? 'email' : 'phone_number';
      await requestSensitiveFieldOtp(field, method);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : t('sensitiveFieldError');
      setError(errorMessage);
    } finally {
      setIsRequestingOTP(false);
    }
  };

  const requestSensitiveFieldOtp = async (field: string, method: 'email' | 'phone_number') => {
    const newValue = profileData[field as keyof ProfileData];
    const request: SensitiveFieldRequest = {
      field: field as 'email' | 'phone_number' | 'first_name' | 'last_name',
      new_value: newValue,
      method,
    };
    const result = await profileService.requestSensitiveFieldUpdate(request);
    if (result.success) {
      setOtpField(field);
      setOtpNewValue(newValue);
      setOtpMessage(result.message);
      setShowOTPModal(true);
    } else {
      setError(result.message);
              // Toast notification removed - using setError instead
    }
  };

  const handleOTPVerify = async (otpCode: string) => {
    try {
      const verifyData: SensitiveFieldVerify = {
        field: otpField as 'email' | 'phone_number' | 'first_name' | 'last_name',
        new_value: otpNewValue,
        otp_code: otpCode
      };

      const result = await profileService.verifySensitiveFieldUpdate(verifyData);

      if (result.success && result.user) {
        updateUser(result.user);
        setSuccess(t('sensitiveFieldSuccess'));
        // Toast notification removed - using setSuccess instead
        setShowOTPModal(false);
        setIsEditing(false);
      } else {
        throw new Error(result.message);
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : t('otpVerifyError');
      throw new Error(errorMessage);
    }
  };

  const handleCancel = () => {
    setProfileData({
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      email: user?.email || '',
      phone_number: user?.phone_number || '',
      date_of_birth: (user as ExtendedUser)?.date_of_birth || '',
      city: (user as ExtendedUser)?.profile?.city || '',
      country: (user as ExtendedUser)?.profile?.country || 'ایران',
    });
    setIsEditing(false);
    setError(null);
  };

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        await fetch('/api/v1/auth/logout/', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.error('Logout API error:', error);
    } finally {
      logout();
      router.push('/login');
    }
  };

  const handleResendEmailOTP = async () => {
    await profileService.resendEmailOTP();
    // Toast notification removed - using setSuccess/setError instead
  };
  
  const handleResendPhoneOTP = async () => {
    await profileService.resendPhoneOTP();
    // Toast notification removed - using setSuccess/setError instead
  };


  // تابع جدید برای نمایش تاریخ عضویت بر اساس زبان
  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (locale === 'fa') {
      // تبدیل ساده میلادی به شمسی (در صورت نیاز می‌توان از کتابخانه استفاده کرد)
      // اینجا فقط نمایش YYYY/MM/DD به سبک شمسی برای نمونه
      const y = date.getFullYear() - 621;
      const m = date.getMonth() + 1;
      const d = date.getDate();
      return `${y}/${m.toString().padStart(2, '0')}/${d.toString().padStart(2, '0')}`;
    }
    return date.toLocaleDateString('en-US');
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">{t('title')}</h1>
            <p className="text-gray-600 dark:text-gray-400">{t('subtitle')}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 lg:gap-8">
            {/* Sidebar Navigation */}
            <div className="lg:col-span-1 order-2 lg:order-1">
              <Card>
                <CardContent className="p-4 lg:p-6">
                  <div className="space-y-1 lg:space-y-2">
                    <button 
                      onClick={() => setActiveTab('profile')}
                      className={`w-full flex items-center gap-2 lg:gap-3 px-2 lg:px-3 py-2 lg:py-2 text-left rounded-lg transition-colors text-sm lg:text-base ${
                        activeTab === 'profile' 
                          ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 font-medium' 
                          : 'text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20'
                      }`}
                    >
                      <User className="w-4 h-4 lg:w-4 lg:h-4 flex-shrink-0" />
                      <span className="min-w-0">{t('personalInfo')}</span>
                    </button>
                    <button 
                      onClick={() => setActiveTab('orders')}
                      className={`w-full flex items-center gap-2 lg:gap-3 px-2 lg:px-3 py-2 lg:py-2 text-left rounded-lg transition-colors text-sm lg:text-base ${
                        activeTab === 'orders' 
                          ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 font-medium' 
                          : 'text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20'
                      }`}
                    >
                      <Package className="w-4 h-4 lg:w-4 lg:h-4 flex-shrink-0" />
                      <span className="min-w-0">{t('ordersTab')}</span>
                    </button>
                    <Button 
                      variant="ghost"
                      className="w-full justify-start text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 text-sm lg:text-base px-2 lg:px-3 py-2 lg:py-2" 
                      onClick={handleLogout}
                    >
                      <LogOut className="w-4 h-4 lg:w-4 lg:h-4 mr-1 lg:mr-2 flex-shrink-0" />
                      <span className="min-w-0">{t('logout')}</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Main Content */}
            <div className="lg:col-span-3 order-1 lg:order-2">
              <Card>
                <CardContent className="p-4 lg:p-6">
                  {activeTab === 'profile' ? (
                  <>
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                      <h2 className="text-lg lg:text-xl font-semibold text-gray-900 dark:text-gray-100">{t('personalInfo')}</h2>
                      {!isEditing ? (
                        <Button
                          variant="ghost"
                          onClick={() => setIsEditing(true)}
                          className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm lg:text-base"
                        >
                          <Edit className="w-4 h-4 mr-2" />
                          {t('editProfile')}
                        </Button>
                      ) : (
                        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                          <Button
                            onClick={handleSave}
                            disabled={isLoading}
                            className="text-sm lg:text-base"
                          >
                            <Save className="w-4 h-4 mr-2" />
                            {isLoading ? t('saving') : t('save')}
                          </Button>
                          <Button
                            variant="secondary"
                            onClick={handleCancel}
                            className="text-sm lg:text-base"
                          >
                            <X className="w-4 h-4 mr-2" />
                            {t('cancel')}
                          </Button>
                        </div>
                      )}
                    </div>

                    {/* Verification Warning Message - Moved to top */}
                    {error === t('verifyContactFirst') && (
                      <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg">
                        <p className="text-yellow-700 dark:text-yellow-300 text-sm">{t('verifyContactFirst')}</p>
                        <div className="flex gap-2 mt-2">
                          <Button onClick={handleResendEmailOTP}>{t('verifyEmail')}</Button>
                          <Button variant="default" onClick={handleResendPhoneOTP}>{t('verifyPhone')}</Button>
                        </div>
                      </div>
                    )}

                    {/* Error/Success Messages */}
                    {error && error !== t('verifyContactFirst') && (
                      <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg">
                        <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
                      </div>
                    )}

                    {success && (
                      <div className="mb-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg">
                        <p className="text-green-600 dark:text-green-400 text-sm">{success}</p>
                      </div>
                    )}

                    {/* Email & Phone verification status */}
                    <div className="flex flex-col gap-2 mb-6">
                      <div className="flex items-center gap-2">
                        <Mail className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                        <span className="text-sm text-gray-900 dark:text-gray-100">{profileData.email}</span>
                        {user?.is_email_verified ? (
                          <span className="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-full">{t('verified')}</span>
                        ) : (
                          <>
                            <span className="text-xs px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300 rounded-full">{t('notVerified')}</span>
                            <button
                              onClick={handleResendEmailOTP}
                              className="ml-2 text-xs text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-300"
                            >
                              {t('resendVerificationCode')}
                            </button>
                          </>
                        )}
                      </div>
                      {/* بخش شماره تلفن */}
                      <div className="flex items-center gap-2">
                        <Phone className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                        {isEditingPhone ? (
                          <>
                            <input
                              type="tel"
                              id="phone_number"
                              name="phone_number"
                              value={profileData.phone_number}
                              onChange={handleInputChange}
                              placeholder={t('phonePlaceholder')}
                              className="w-40 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400"
                              disabled={isRequestingOTP}
                            />
                            <button
                              onClick={async () => {
                                if (!profileData.phone_number) return;
                                await handleSensitiveFieldChange('phone_number');
                                setIsEditingPhone(false);
                              }}
                              className="ml-2 text-xs text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-300"
                              disabled={!profileData.phone_number || isRequestingOTP}
                            >
                              {t('saveAndVerifyPhone')}
                            </button>
                            <button
                              onClick={() => {
                                setProfileData(prev => ({ ...prev, phone_number: user?.phone_number || '' }));
                                setIsEditingPhone(false);
                              }}
                              className="ml-2 text-xs text-gray-500 dark:text-gray-400 underline hover:text-gray-700 dark:hover:text-gray-300"
                            >
                              {t('cancel')}
                            </button>
                          </>
                        ) : profileData.phone_number ? (
                          <>
                            <span className="text-sm text-gray-900 dark:text-gray-100">{profileData.phone_number}</span>
                            {user?.is_phone_verified ? (
                              <span className="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300 rounded-full">{t('verified')}</span>
                            ) : (
                              <span className="text-xs px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300 rounded-full">{t('notVerified')}</span>
                            )}
                            <button
                              onClick={handleResendPhoneOTP}
                              className="ml-2 text-xs text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-300"
                              disabled={isRequestingOTP}
                            >
                              {t('resendVerificationCode')}
                            </button>
                            <button
                              onClick={() => setIsEditingPhone(true)}
                              className="ml-2 text-xs text-gray-500 dark:text-gray-400 underline hover:text-gray-700 dark:hover:text-gray-300"
                            >
                              {t('editPhone')}
                            </button>
                          </>
                        ) : (
                          <>
                            <input
                              type="tel"
                              id="phone_number"
                              name="phone_number"
                              value={profileData.phone_number}
                              onChange={handleInputChange}
                              placeholder={t('phonePlaceholder')}
                              className="w-40 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-lg text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400"
                              disabled={isRequestingOTP}
                            />
                            <button
                              onClick={async () => {
                                if (!profileData.phone_number) return;
                                await handleSensitiveFieldChange('phone_number');
                              }}
                              className="ml-2 text-xs text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-300"
                              disabled={!profileData.phone_number || isRequestingOTP}
                            >
                              {t('addAndVerifyPhone')}
                            </button>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Profile Form */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 lg:gap-6">
                      <div>
                        <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('firstName')}
                        </label>
                        <input
                          type="text"
                          id="first_name"
                          name="first_name"
                          value={profileData.first_name}
                          onChange={handleInputChange}
                          disabled={!isEditing}
                          required
                          className="w-full px-3 lg:px-4 py-2 lg:py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-900/20 focus:border-transparent disabled:bg-gray-50 dark:disabled:bg-gray-700 disabled:text-gray-500 dark:disabled:text-gray-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 text-sm lg:text-base"
                          placeholder={t('firstNamePlaceholder')}
                        />
                      </div>

                      <div>
                        <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('lastName')}
                        </label>
                        <input
                          type="text"
                          id="last_name"
                          name="last_name"
                          value={profileData.last_name}
                          onChange={handleInputChange}
                          disabled={!isEditing}
                          required
                          className="w-full px-3 lg:px-4 py-2 lg:py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-900/20 focus:border-transparent disabled:bg-gray-50 dark:disabled:bg-gray-700 disabled:text-gray-500 dark:disabled:text-gray-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 text-sm lg:text-base"
                          placeholder={t('lastNamePlaceholder')}
                        />
                      </div>

                      <div>
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('email')}
                        </label>
                        <div className="relative">
                          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Mail className="h-5 w-5 text-gray-400" />
                          </div>
                          <input
                            type="email"
                            id="email"
                            name="email"
                            value={profileData.email}
                            onChange={handleInputChange}
                            disabled={!isEditing}
                            required
                            className="w-full pl-10 pr-3 lg:pr-4 py-2 lg:py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-900/20 focus:border-transparent disabled:bg-gray-50 dark:disabled:bg-gray-700 disabled:text-gray-500 dark:disabled:text-gray-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 text-sm lg:text-base"
                            placeholder={t('emailPlaceholder')}
                          />
                        </div>
                      </div>

                      <div>
                        <label htmlFor="date_of_birth" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('dateOfBirth')}
                        </label>
                        <div className="relative">
                          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <Calendar className="h-5 w-5 text-gray-400" />
                          </div>
                          <input
                            type="date"
                            id="date_of_birth"
                            name="date_of_birth"
                            value={profileData.date_of_birth || ''}
                            onChange={handleInputChange}
                            disabled={!isEditing}
                            className="w-full pl-10 pr-3 lg:pr-4 py-2 lg:py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-900/20 focus:border-transparent disabled:bg-gray-50 dark:disabled:bg-gray-700 disabled:text-gray-500 dark:disabled:text-gray-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 text-sm lg:text-base"
                            placeholder={t('dateOfBirthPlaceholder')}
                          />
                        </div>
                      </div>

                      <div>
                        <label htmlFor="country" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('country')}
                        </label>
                        <input
                          type="text"
                          id="country"
                          name="country"
                          value={profileData.country}
                          onChange={handleInputChange}
                          disabled={!isEditing}
                          className="w-full px-3 lg:px-4 py-2 lg:py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-900/20 focus:border-transparent disabled:bg-gray-50 dark:disabled:bg-gray-700 disabled:text-gray-500 dark:disabled:text-gray-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 text-sm lg:text-base"
                          placeholder={t('countryPlaceholder')}
                        />
                      </div>

                      <div className="sm:col-span-2">
                        <label htmlFor="city" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('city')}
                        </label>
                        <input
                          type="text"
                          id="city"
                          name="city"
                          value={profileData.city}
                          onChange={handleInputChange}
                          disabled={!isEditing}
                          className="w-full px-3 lg:px-4 py-2 lg:py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-900/20 focus:border-transparent disabled:bg-gray-50 dark:disabled:bg-gray-700 disabled:text-gray-500 dark:disabled:text-gray-400 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder:text-gray-500 dark:placeholder:text-gray-400 text-sm lg:text-base"
                          placeholder={t('cityPlaceholder')}
                        />
                      </div>
                    </div>

                    {/* Account Info */}
                    <div className="mt-6 lg:mt-8 pt-6 lg:pt-8 border-t border-gray-200 dark:border-gray-700">
                      <h3 className="text-base lg:text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">{t('accountInfo')}</h3>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 lg:gap-4">
                        <div className="p-3 lg:p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                          <p className="text-xs lg:text-sm text-gray-600 dark:text-gray-400">{t('joinDate')}</p>
                          <p className="font-medium text-gray-900 dark:text-gray-100 text-sm lg:text-base">
                            {user?.created_at ? formatDate(String(user.created_at)) : t('unknown')}
                          </p>
                        </div>
                        <div className="p-3 lg:p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                          <p className="text-xs lg:text-sm text-gray-600 dark:text-gray-400">{t('accountStatus')}</p>
                          <p className="font-medium text-green-600 dark:text-green-400 text-sm lg:text-base">{t('active')}</p>
                        </div>
                      </div>
                    </div>
                    {!isEditing && (
                      <Button
                        variant="ghost"
                        onClick={() => setShowChangePasswordModal(true)}
                        className="text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                      >
                        <Key className="w-4 h-4 mr-2" />
                        {t('changePassword')}
                      </Button>
                    )}
                  </>
                ) : (
                  <OrderHistory onShowToast={handleShowToast} />
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

        {/* OTP Modal */}
        <OTPModal
          isOpen={showOTPModal}
          onClose={() => setShowOTPModal(false)}
          onVerify={handleOTPVerify}
          field={otpField}
          newValue={otpNewValue}
          message={otpMessage}
          isLoading={isRequestingOTP}
        />
        
        {/* Modal انتخاب روش دریافت OTP */}
        {showOtpMethodModal && (
          <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-xs w-full">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">{t('chooseOtpMethod')}</h3>
              <div className="flex flex-col gap-3 mb-4">
                <Button
                  onClick={async () => {
                    setShowOtpMethodModal(false);
                    await requestSensitiveFieldOtp(otpField || 'email', 'email');
                  }}
                >
                  {t('sendOtpToEmail', { email: user?.email || '' })}
                </Button>
                <Button
                  variant="default"
                  onClick={async () => {
                    setShowOtpMethodModal(false);
                    await requestSensitiveFieldOtp(otpField || 'phone_number', 'phone_number');
                  }}
                >
                  {t('sendOtpToPhone', { phone: user?.phone_number || '' })}
                </Button>
              </div>
              <Button variant="secondary" onClick={() => setShowOtpMethodModal(false)}>{t('cancel')}</Button>
            </div>
          </div>
        )}

        
        {/* Toast notifications are handled by ToastProvider */}
        <ChangePasswordModal
          isOpen={showChangePasswordModal}
          onClose={() => setShowChangePasswordModal(false)}
          onSubmit={async (currentPassword, newPassword, confirmPassword) => {
            // Toast notification removed
            try {
              const token = localStorage.getItem('access_token');
              const res = await fetch('/api/v1/auth/change-password/', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                  current_password: currentPassword,
                  new_password: newPassword,
                  new_password_confirm: confirmPassword,
                }),
              });
              const data = await res.json();
              if (res.ok) {
                // Toast notification removed - using setSuccess instead
                setShowChangePasswordModal(false);
              } else {
                throw new Error(data.error || data.non_field_errors?.[0] || t('passwordChangeError'));
              }
            } catch (err: unknown) {
              // Toast notification removed - using setError instead
              throw err;
            }
          }}
          t={t}
        />
      </div>
    </ProtectedRoute>
  );
}