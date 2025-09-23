'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useAgent } from '@/app/lib/hooks/useAgent';
import { useLocale } from 'next-intl';
import { useUnifiedCurrency } from '@/lib/contexts/UnifiedCurrencyContext';
import { useUnifiedLanguage } from '@/lib/contexts/UnifiedLanguageContext';
import { cn } from '@/lib/utils';
import {
  UserIcon,
  BellIcon,
  ShieldCheckIcon,
  CreditCardIcon,
  GlobeAltIcon,
  KeyIcon,
  EyeIcon,
  EyeSlashIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

interface AgentSettings {
  // Profile Settings
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  company_name: string;
  license_number: string;
  address: string;
  city: string;
  country: string;
  
  // Notification Settings
  email_notifications: boolean;
  sms_notifications: boolean;
  push_notifications: boolean;
  commission_alerts: boolean;
  booking_alerts: boolean;
  payment_alerts: boolean;
  
  // Security Settings
  two_factor_auth: boolean;
  session_timeout: number;
  password_change_required: boolean;
  
  // Payment Settings
  bank_name: string;
  bank_account: string;
  swift_code: string;
  payment_method: 'bank_transfer' | 'paypal' | 'stripe';
  
  // Language & Region
  language: string;
  timezone: string;
  currency: string;
  date_format: string;
}

interface SettingsTab {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
}

export default function AgentSettingsPage() {
  const t = useTranslations('agent');
  const locale = useLocale();
  const isRTL = locale === 'fa';
  
  const {
    agent,
    updateAgentProfile,
    loadDashboard,
    loading,
  } = useAgent();
  
      const { currency: unifiedCurrency, setCurrency: setUnifiedCurrency } = useUnifiedCurrency();
      const { language: unifiedLanguage, setLanguage: setUnifiedLanguage, changeLanguageAndNavigate } = useUnifiedLanguage();

  // State for settings
  const [settings, setSettings] = useState<AgentSettings>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    company_name: '',
    license_number: '',
    address: '',
    city: '',
    country: '',
    email_notifications: true,
    sms_notifications: true,
    push_notifications: true,
    commission_alerts: true,
    booking_alerts: true,
    payment_alerts: true,
    two_factor_auth: false,
    session_timeout: 30,
    password_change_required: false,
    bank_name: '',
    bank_account: '',
    swift_code: '',
    payment_method: 'bank_transfer',
    language: 'fa',
    timezone: 'Asia/Tehran',
    currency: 'IRR',
    date_format: 'YYYY-MM-DD'
  });

  // State for UI
  const [activeTab, setActiveTab] = useState('profile');
  const [showPassword, setShowPassword] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  // Settings tabs
  const tabs: SettingsTab[] = [
    {
      id: 'profile',
      name: t('settings.tabs.profile'),
      icon: UserIcon,
      description: t('settings.tabs.profileDesc')
    },
    {
      id: 'notifications',
      name: t('settings.tabs.notifications'),
      icon: BellIcon,
      description: t('settings.tabs.notificationsDesc')
    },
    {
      id: 'security',
      name: t('settings.tabs.security'),
      icon: ShieldCheckIcon,
      description: t('settings.tabs.securityDesc')
    },
    {
      id: 'payment',
      name: t('settings.tabs.payment'),
      icon: CreditCardIcon,
      description: t('settings.tabs.paymentDesc')
    },
    {
      id: 'preferences',
      name: t('settings.tabs.preferences'),
      icon: GlobeAltIcon,
      description: t('settings.tabs.preferencesDesc')
    }
  ];

  // Load agent data
  useEffect(() => {
    if (agent) {
      console.log('Agent data loaded in settings:', agent);
      console.log('Agent preferred currency:', (agent as { preferred_currency?: string }).preferred_currency);
      console.log('Agent preferred language:', (agent as { preferred_language?: string }).preferred_language);
      
      // Get current language from URL
      const currentLocale = locale || 'fa';
      console.log('Current locale from URL:', currentLocale);
      
      setSettings(prev => ({
        ...prev,
        first_name: agent.username || '',
        last_name: '',
        email: agent.email || '',
        phone: '',
        company_name: agent.agency_name || '',
        license_number: agent.agent_code || '',
        address: '',
        city: '',
        country: '',
        // Load agent's preferred currency and language
        currency: (agent as { preferred_currency?: string }).preferred_currency || 'USD',
        language: (agent as { preferred_language?: string }).preferred_language || currentLocale
      }));
    }
  }, [agent, locale]);

  // Update language setting when URL locale changes
  useEffect(() => {
    if (locale && ['fa', 'en', 'tr'].includes(locale)) {
      setSettings(prev => ({
        ...prev,
        language: locale
      }));
      console.log('Language setting updated from URL locale:', locale);
    }
  }, [locale]);

  // Handle settings update
  const handleSettingsUpdate = (updates: Partial<AgentSettings>) => {
    setSettings(prev => ({ ...prev, ...updates }));
  };

  // Handle password change
  const handlePasswordChange = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      alert(t('passwordMismatch'));
      return;
    }

    if (passwordData.new_password.length < 8) {
      alert(t('passwordTooShort'));
      return;
    }

    try {
      setSaveStatus('saving');
      // Call password change API
      await new Promise(resolve => setTimeout(resolve, 1000)); // Mock API call
      setSaveStatus('saved');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  // Save settings
  const saveSettings = async () => {
    try {
      setSaveStatus('saving');
      
      // Prepare profile data to send (only fields that exist in User model)
      const profileData = {
        preferred_currency: settings.currency,
        preferred_language: settings.language,
        // Note: timezone is not available in User model
        // Add other fields as needed
      };
      
      console.log('Saving profile data:', profileData);
      
      // First, update the agent profile in the database
      await updateAgentProfile(profileData);
      console.log('Profile saved successfully');
      
      // Update unified contexts immediately
      setUnifiedCurrency(settings.currency);
      
      // For language changes, navigate to new URL if language actually changed
      const currentLanguage = unifiedLanguage || 'fa';
      if (settings.language !== currentLanguage) {
        console.log(`Language changed from ${currentLanguage} to ${settings.language}, navigating...`);
        // Use changeLanguageAndNavigate to update URL
        changeLanguageAndNavigate(settings.language);
      } else {
        // Just update the context without navigation
        setUnifiedLanguage(settings.language);
      }
      console.log('Updated unified contexts');
      
      // Reload agent data to ensure UI reflects changes
      await loadDashboard();
      console.log('Agent data reloaded');
      
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('Failed to save settings:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  // Format currency

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {t('settings.title')}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {t('settings.subtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Settings Navigation */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 sticky top-8">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                {t('categories')}
              </h3>
              
              <nav className="space-y-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={cn(
                      "w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                      isRTL ? "space-x-reverse space-x-3" : "space-x-3",
                      activeTab === tab.id
                        ? "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400"
                        : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                    )}
                  >
                    <tab.icon className="w-5 h-5 flex-shrink-0" />
                    <span className="truncate">{tab.name}</span>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Settings Content */}
          <div className="lg:col-span-3">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="p-6">
                {/* Tab Header */}
                <div className="mb-6">
                  <div className="flex items-center mb-2">
                    {(() => {
                      const currentTab = tabs.find(tab => tab.id === activeTab);
                      return currentTab?.icon && (
                        <currentTab.icon className="w-6 h-6 text-blue-600 mr-3" />
                      );
                    })()}
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                      {tabs.find(tab => tab.id === activeTab)?.name}
                    </h2>
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">
                    {tabs.find(tab => tab.id === activeTab)?.description}
                  </p>
                </div>

                {/* Profile Settings */}
                {activeTab === 'profile' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.firstName')}
                        </label>
                        <input
                          type="text"
                          value={settings.first_name}
                          onChange={(e) => handleSettingsUpdate({ first_name: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.lastName')}
                        </label>
                        <input
                          type="text"
                          value={settings.last_name}
                          onChange={(e) => handleSettingsUpdate({ last_name: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.email')}
                        </label>
                        <input
                          type="email"
                          value={settings.email}
                          onChange={(e) => handleSettingsUpdate({ email: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.phone')}
                        </label>
                        <input
                          type="tel"
                          value={settings.phone}
                          onChange={(e) => handleSettingsUpdate({ phone: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.companyName')}
                        </label>
                        <input
                          type="text"
                          value={settings.company_name}
                          onChange={(e) => handleSettingsUpdate({ company_name: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('licenseNumber')}
                        </label>
                        <input
                          type="text"
                          value={settings.license_number}
                          onChange={(e) => handleSettingsUpdate({ license_number: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {t('settings.address')}
                      </label>
                      <textarea
                        value={settings.address}
                        onChange={(e) => handleSettingsUpdate({ address: e.target.value })}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.city')}
                        </label>
                        <input
                          type="text"
                          value={settings.city}
                          onChange={(e) => handleSettingsUpdate({ city: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.country')}
                        </label>
                        <input
                          type="text"
                          value={settings.country}
                          onChange={(e) => handleSettingsUpdate({ country: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Notification Settings */}
                {activeTab === 'notifications' && (
                  <div className="space-y-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {t('settings.notificationChannels')}
                      </h3>
                      
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {t('settings.emailNotifications')}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {t('settings.emailNotificationsDesc')}
                            </p>
                          </div>
                          <input
                            type="checkbox"
                            checked={settings.email_notifications}
                            onChange={(e) => handleSettingsUpdate({ email_notifications: e.target.checked })}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                        </div>
                        
                        <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {t('settings.smsNotifications')}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {t('settings.smsNotificationsDesc')}
                            </p>
                          </div>
                          <input
                            type="checkbox"
                            checked={settings.sms_notifications}
                            onChange={(e) => handleSettingsUpdate({ sms_notifications: e.target.checked })}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                        </div>
                        
                        <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {t('settings.pushNotifications')}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {t('settings.pushNotificationsDesc')}
                            </p>
                          </div>
                          <input
                            type="checkbox"
                            checked={settings.push_notifications}
                            onChange={(e) => handleSettingsUpdate({ push_notifications: e.target.checked })}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                        </div>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {t('settings.notificationTypes')}
                      </h3>
                      
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {t('settings.commissionAlerts')}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {t('settings.commissionAlertsDesc')}
                            </p>
                          </div>
                          <input
                            type="checkbox"
                            checked={settings.commission_alerts}
                            onChange={(e) => handleSettingsUpdate({ commission_alerts: e.target.checked })}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                        </div>
                        
                        <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {t('settings.bookingAlerts')}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {t('settings.bookingAlertsDesc')}
                            </p>
                          </div>
                          <input
                            type="checkbox"
                            checked={settings.booking_alerts}
                            onChange={(e) => handleSettingsUpdate({ booking_alerts: e.target.checked })}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                        </div>
                        
                        <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {t('settings.paymentAlerts')}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {t('settings.paymentAlertsDesc')}
                            </p>
                          </div>
                          <input
                            type="checkbox"
                            checked={settings.payment_alerts}
                            onChange={(e) => handleSettingsUpdate({ payment_alerts: e.target.checked })}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Security Settings */}
                {activeTab === 'security' && (
                  <div className="space-y-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {t('settings.passwordChange')}
                      </h3>
                      
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            {t('settings.currentPassword')}
                          </label>
                          <div className="relative">
                            <input
                              type={showPassword ? "text" : "password"}
                              value={passwordData.current_password}
                              onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                              className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword(!showPassword)}
                              className="absolute inset-y-0 right-0 pr-3 flex items-center"
                            >
                              {showPassword ? (
                                <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                              ) : (
                                <EyeIcon className="h-5 w-5 text-gray-400" />
                              )}
                            </button>
                          </div>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            {t('settings.newPassword')}
                          </label>
                          <input
                            type="password"
                            value={passwordData.new_password}
                            onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            {t('settings.confirmPassword')}
                          </label>
                          <input
                            type="password"
                            value={passwordData.confirm_password}
                            onChange={(e) => setPasswordData(prev => ({ ...prev, confirm_password: e.target.value }))}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          />
                        </div>
                        
                        <button
                          onClick={handlePasswordChange}
                          disabled={!passwordData.current_password || !passwordData.new_password || !passwordData.confirm_password}
                          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <KeyIcon className="w-4 h-4 mr-2" />
                          {t('settings.changePassword')}
                        </button>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {t('settings.securityOptions')}
                      </h3>
                      
                      <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {t('settings.twoFactorAuth')}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {t('settings.twoFactorAuthDesc')}
                            </p>
                          </div>
                          <input
                            type="checkbox"
                            checked={settings.two_factor_auth}
                            onChange={(e) => handleSettingsUpdate({ two_factor_auth: e.target.checked })}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                        </div>
                        
                        <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {t('settings.passwordChangeRequired')}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {t('settings.passwordChangeRequiredDesc')}
                            </p>
                          </div>
                          <input
                            type="checkbox"
                            checked={settings.password_change_required}
                            onChange={(e) => handleSettingsUpdate({ password_change_required: e.target.checked })}
                            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Payment Settings */}
                {activeTab === 'payment' && (
                  <div className="space-y-6">
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {t('settings.paymentMethod')}
                      </h3>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.preferredPaymentMethod')}
                        </label>
                        <select
                          value={settings.payment_method}
                          onChange={(e) => handleSettingsUpdate({ payment_method: e.target.value as 'paypal' | 'stripe' | 'bank_transfer' })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="bank_transfer">{t('settings.bankTransfer')}</option>
                          <option value="paypal">{t('settings.paypal')}</option>
                          <option value="stripe">{t('settings.stripe')}</option>
                        </select>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                        {t('settings.bankDetails')}
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            {t('settings.bankName')}
                          </label>
                          <input
                            type="text"
                            value={settings.bank_name}
                            onChange={(e) => handleSettingsUpdate({ bank_name: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            {t('settings.bankAccount')}
                          </label>
                          <input
                            type="text"
                            value={settings.bank_account}
                            onChange={(e) => handleSettingsUpdate({ bank_account: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          />
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            {t('settings.swiftCode')}
                          </label>
                          <input
                            type="text"
                            value={settings.swift_code}
                            onChange={(e) => handleSettingsUpdate({ swift_code: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Preferences Settings */}
                {activeTab === 'preferences' && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.language')}
                        </label>
                        <select
                          value={settings.language}
                          onChange={(e) => handleSettingsUpdate({ language: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="fa">فارسی</option>
                          <option value="en">English</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.timezone')}
                        </label>
                        <select
                          value={settings.timezone}
                          onChange={(e) => handleSettingsUpdate({ timezone: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="Asia/Tehran">Asia/Tehran</option>
                          <option value="UTC">UTC</option>
                          <option value="America/New_York">America/New_York</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.currency')}
                        </label>
                        <select
                          value={settings.currency}
                          onChange={(e) => handleSettingsUpdate({ currency: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="IRR">ریال ایران (IRR)</option>
                          <option value="USD">دلار آمریکا (USD)</option>
                          <option value="EUR">یورو (EUR)</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t('settings.dateFormat')}
                        </label>
                        <select
                          value={settings.date_format}
                          onChange={(e) => handleSettingsUpdate({ date_format: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="YYYY-MM-DD">2024-01-15</option>
                          <option value="DD/MM/YYYY">15/01/2024</option>
                          <option value="MM/DD/YYYY">01/15/2024</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {/* Save Button */}
                <div className="flex justify-end mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={saveSettings}
                    disabled={loading || saveStatus === 'saving'}
                    className={cn(
                      "inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed",
                      isRTL ? "space-x-reverse space-x-2" : "space-x-2"
                    )}
                  >
                    {saveStatus === 'saving' ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>{t('settings.saving')}</span>
                      </>
                    ) : saveStatus === 'saved' ? (
                      <>
                        <CheckCircleIcon className="w-4 h-4" />
                        <span>{t('settings.saved')}</span>
                      </>
                    ) : saveStatus === 'error' ? (
                      <>
                        <ExclamationTriangleIcon className="w-4 h-4" />
                        <span>{t('settings.error')}</span>
                      </>
                    ) : (
                      <>
                        <span>{t('settings.save')}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

