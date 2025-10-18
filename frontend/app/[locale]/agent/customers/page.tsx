'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useAgent } from '@/app/lib/hooks/useAgent';
import { AgentCustomer } from '@/app/lib/types/api';
import { formatCustomerTier, formatCustomerStatus, getCustomerStatusColor } from '@/lib/api/agent-utils';
import { useLocale } from 'next-intl';
import { cn } from '@/lib/utils';
// import { apiClient } from '@/lib/api/client'; // Unused import
import { sendCustomerCredentials, sendCustomerVerification } from '@/app/lib/api/agents';
import {
  PlusIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  UserGroupIcon,
  CurrencyDollarIcon,
  PencilIcon,
  TrashIcon,
  StarIcon,
  UserIcon,
  PhoneIcon,
  EnvelopeIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

export default function AgentCustomersPage() {
  const t = useTranslations('agent');
  const locale = useLocale();
  const isRTL = locale === 'fa';
  
  const {
    customers,
    customersLoading,
    customersError,
    customerStatistics,
    loadCustomers,
    createCustomer,
    updateCustomer,
    deleteCustomer,
    searchCustomers,
    loadCustomerStatistics,
    clearError,
  } = useAgent();

  // State for UI
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<AgentCustomer | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    tier: '',
    created_after: '',
    created_before: ''
  });

  // Notification state
  const [notification, setNotification] = useState<{
    type: 'success' | 'error' | 'info';
    message: string;
    show: boolean;
  }>({
    type: 'info',
    message: '',
    show: false
  });

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    address: '',
    city: '',
    country: '',
    birth_date: '',
    gender: '',
    preferred_language: 'fa',
    preferred_contact_method: 'email',
    customer_status: 'active',
    customer_tier: 'bronze',
    relationship_notes: '',
    special_requirements: '',
    marketing_consent: false,
    // New authentication fields
    password: '',
    password_confirmation: '',
    send_credentials: true,
    verification_method: 'email', // 'email' | 'sms' | 'both'
    welcome_message: '',
    custom_instructions: ''
  });

  // Load initial data
  useEffect(() => {
    loadCustomers();
    loadCustomerStatistics();
  }, [loadCustomers, loadCustomerStatistics]);

  // Handle search
  const handleSearch = async () => {
    if (searchQuery.trim()) {
      try {
        await searchCustomers(searchQuery);
        // Update customers list with search results
        // Note: This would need to be handled in the hook
      } catch (error) {
        console.error('Search failed:', error);
      }
    } else {
      loadCustomers(filters);
    }
  };

  // Handle create customer
  const handleCreateCustomer = async () => {
    try {
      // Only send fields that backend expects
      const customerData = {
        email: formData.email,
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
        address: formData.address,
        city: formData.city,
        country: formData.country,
        birth_date: formData.birth_date,
        gender: formData.gender,
        preferred_language: formData.preferred_language,
        preferred_contact_method: formData.preferred_contact_method,
        customer_status: formData.customer_status,
        customer_tier: formData.customer_tier,
        relationship_notes: formData.relationship_notes,
        special_requirements: formData.special_requirements,
        marketing_consent: formData.marketing_consent,
        // Authentication options
        send_credentials: formData.send_credentials,
        verification_method: formData.verification_method,
        welcome_message: formData.welcome_message,
        custom_instructions: formData.custom_instructions,
      };
      
      await createCustomer(customerData);
      
      setNotification({
        type: 'success',
        message: t('customers.customerCreated'),
        show: true
      });
      
      setShowCreateModal(false);
      resetForm();
      loadCustomers(filters);
    } catch (error: unknown) {
      console.error('Create customer failed:', error);
      
      const errorMessage = (error as { response?: { data?: { message?: string } }; message?: string })?.response?.data?.message || 
                          (error as { response?: { data?: { message?: string } }; message?: string })?.message || 
                          t('customers.createFailed');
      
      setNotification({
        type: 'error',
        message: errorMessage,
        show: true
      });
    }
  };

  // Handle update customer
  const handleUpdateCustomer = async () => {
    if (!selectedCustomer) return;
    
    try {
      await updateCustomer(selectedCustomer.id, formData);
      setShowEditModal(false);
      setSelectedCustomer(null);
      resetForm();
      loadCustomers(filters);
    } catch (error) {
      console.error('Update customer failed:', error);
    }
  };

  // Handle delete customer
  const handleDeleteCustomer = async (customerId: string) => {
    if (!confirm(t('customers.confirmDelete'))) return;
    
    try {
      await deleteCustomer(customerId);
      loadCustomers(filters);
    } catch (error) {
      console.error('Delete customer failed:', error);
    }
  };

  // Handle send credentials
  const handleSendCredentials = async (customerId: string) => {
    try {
      const response = await sendCustomerCredentials(customerId, { method: 'email' });
      
      if (response && typeof response === 'object' && 'data' in response && (response.data as { success: boolean }).success) {
        // Show success notification
        setNotification({
          type: 'success',
          message: t('customers.credentialsSent'),
          show: true
        });
        loadCustomers(filters);
      } else {
        throw new Error('Failed to send credentials');
      }
    } catch (error: unknown) {
      console.error('Send credentials failed:', error);
      
      // Show error notification with specific message
      const errorMessage = (error as { response?: { data?: { message?: string } }; message?: string })?.response?.data?.message || 
                          (error as { response?: { data?: { message?: string } }; message?: string })?.message || 
                          t('customers.credentialsSendFailed');
      
      setNotification({
        type: 'error',
        message: errorMessage,
        show: true
      });
    }
  };

  // Handle send verification
  const handleSendVerification = async (customerId: string) => {
    try {
      const response = await sendCustomerVerification(customerId);
      
      if (response && typeof response === 'object' && 'data' in response && (response.data as { success: boolean }).success) {
        setNotification({
          type: 'success',
          message: t('customers.verificationSent'),
          show: true
        });
        loadCustomers(filters);
      } else {
        throw new Error('Failed to send verification');
      }
    } catch (error: unknown) {
      console.error('Send verification failed:', error);
      
      const errorMessage = (error as { response?: { data?: { message?: string } }; message?: string })?.response?.data?.message || 
                          (error as { response?: { data?: { message?: string } }; message?: string })?.message || 
                          t('customers.verificationSendFailed');
      
      setNotification({
        type: 'error',
        message: errorMessage,
        show: true
      });
    }
  };

  // Handle tier update

  // Handle status update

  // Reset form
  const resetForm = () => {
    setFormData({
      email: '',
      first_name: '',
      last_name: '',
      phone: '',
      address: '',
      city: '',
      country: '',
      birth_date: '',
      gender: '',
      preferred_language: 'fa',
      preferred_contact_method: 'email',
      customer_status: 'active',
      customer_tier: 'bronze',
      relationship_notes: '',
      special_requirements: '',
      marketing_consent: false,
      // New authentication fields
      password: '',
      password_confirmation: '',
      send_credentials: true,
      verification_method: 'email',
      welcome_message: '',
      custom_instructions: ''
    });
  };

  // Open edit modal
  const openEditModal = (customer: AgentCustomer) => {
    setSelectedCustomer(customer);
    setFormData({
      email: customer.email,
      first_name: customer.name?.split(' ')[0] || '',
      last_name: customer.name?.split(' ').slice(1).join(' ') || '',
      phone: customer.phone || '',
      address: customer.address || '',
      city: customer.city || '',
      country: customer.country || '',
      birth_date: customer.birth_date || '',
      gender: customer.gender || '',
      preferred_language: customer.preferred_language || '',
      preferred_contact_method: customer.preferred_contact_method || '',
      customer_status: customer.status,
      customer_tier: customer.tier,
      relationship_notes: '',
      special_requirements: '',
      marketing_consent: false,
      // New authentication fields
      password: '',
      password_confirmation: '',
      send_credentials: true,
      verification_method: 'email',
      welcome_message: '',
      custom_instructions: ''
    });
    setShowEditModal(true);
  };

  return (
    <div className="space-y-6">
      {/* Notification */}
      {notification.show && (
        <div className={cn(
          "fixed top-4 right-4 z-50 p-4 rounded-md shadow-lg max-w-sm",
          notification.type === 'success' && "bg-green-50 border border-green-200 text-green-800",
          notification.type === 'error' && "bg-red-50 border border-red-200 text-red-800",
          notification.type === 'info' && "bg-blue-50 border border-blue-200 text-blue-800"
        )}>
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium">{notification.message}</p>
            <button
              onClick={() => setNotification(prev => ({ ...prev, show: false }))}
              className="ml-4 text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {t('customers.title')}
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {t('customers.subtitle')}
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className={cn(
            "mt-4 sm:mt-0 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
            isRTL ? "space-x-reverse space-x-2" : "space-x-2"
          )}
        >
          <PlusIcon className="w-4 h-4" />
          <span>{t('customers.addCustomer')}</span>
        </button>
      </div>

      {/* Statistics Cards */}
      {customerStatistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UserGroupIcon className="h-6 w-6 text-blue-600" />
                </div>
                <div className={cn("ml-5 w-0 flex-1", isRTL && "ml-0 mr-5")}>
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {t('customers.totalCustomers')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {customerStatistics.total_customers}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UserIcon className="h-6 w-6 text-green-600" />
                </div>
                <div className={cn("ml-5 w-0 flex-1", isRTL && "ml-0 mr-5")}>
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {t('customers.activeCustomers')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {customerStatistics.active_customers}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <StarIcon className="h-6 w-6 text-yellow-600" />
                </div>
                <div className={cn("ml-5 w-0 flex-1", isRTL && "ml-0 mr-5")}>
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {t('customers.vipCustomers')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {customerStatistics.vip_customers}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CurrencyDollarIcon className="h-6 w-6 text-purple-600" />
                </div>
                <div className={cn("ml-5 w-0 flex-1", isRTL && "ml-0 mr-5")}>
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {t('customers.totalSpent')}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      ${customerStatistics.total_spent.toLocaleString()}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
          {/* Search */}
          <div className="flex-1 max-w-lg">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder={t('customers.searchPlaceholder')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className={cn(
                  "block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500",
                  isRTL && "text-right"
                )}
              />
            </div>
          </div>

          {/* Filters Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={cn(
              "inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
              isRTL ? "space-x-reverse space-x-2" : "space-x-2"
            )}
          >
            <FunnelIcon className="w-4 h-4" />
            <span>Filters</span>
            {showFilters ? (
              <ChevronUpIcon className="w-4 h-4" />
            ) : (
              <ChevronDownIcon className="w-4 h-4" />
            )}
          </button>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Status Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('customers.status')}
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="">{t('customers.filters.allStatuses')}</option>
                  <option value="active">{t('customers.filters.active')}</option>
                  <option value="inactive">{t('customers.filters.inactive')}</option>
                  <option value="suspended">{t('customers.filters.suspended')}</option>
                </select>
              </div>

              {/* Tier Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('customers.tier')}
                </label>
                <select
                  value={filters.tier}
                  onChange={(e) => setFilters({ ...filters, tier: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="">{t('customers.filters.allTiers')}</option>
                  <option value="bronze">{t('customers.filters.bronze')}</option>
                  <option value="silver">{t('customers.filters.silver')}</option>
                  <option value="gold">{t('customers.filters.gold')}</option>
                  <option value="platinum">{t('customers.filters.platinum')}</option>
                </select>
              </div>

              {/* Date From */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('customers.createdFrom')}
                </label>
                <input
                  type="date"
                  value={filters.created_after}
                  onChange={(e) => setFilters({ ...filters, created_after: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              {/* Date To */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {t('customers.createdTo')}
                </label>
                <input
                  type="date"
                  value={filters.created_before}
                  onChange={(e) => setFilters({ ...filters, created_before: e.target.value })}
                  className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>

            {/* Filter Actions */}
            <div className="mt-4 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setFilters({
                    status: '',
                    tier: '',
                    created_after: '',
                    created_before: ''
                  });
                  loadCustomers();
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {t('customers.clearFilters')}
              </button>
              <button
                onClick={() => loadCustomers(filters)}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {t('customers.applyFilters')}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Customers Table */}
      <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-md">
        {customersLoading ? (
          <div className="p-8 text-center">
            <div className="inline-flex items-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              <span className={cn("ml-3 text-gray-600 dark:text-gray-400", isRTL && "ml-0 mr-3")}>
                {t('customers.loading')}
              </span>
            </div>
          </div>
        ) : customersError ? (
          <div className="p-8 text-center">
            <div className="text-red-600 dark:text-red-400">
              {customersError}
            </div>
            <button
              onClick={() => {
                clearError();
                loadCustomers(filters);
              }}
              className="mt-2 text-sm text-blue-600 hover:text-blue-500"
            >
              {t('customers.retry')}
            </button>
          </div>
        ) : customers.length === 0 ? (
          <div className="p-8 text-center">
            <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              {t('customers.noCustomers')}
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              {t('customers.noCustomersDescription')}
            </p>
            <div className="mt-6">
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                {t('customers.addCustomer')}
              </button>
            </div>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200 dark:divide-gray-700">
            {customers.map((customer) => (
              <li key={customer.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                        <UserIcon className="h-6 w-6 text-gray-600 dark:text-gray-300" />
                      </div>
                    </div>
                    <div className={cn("ml-4", isRTL && "ml-0 mr-4")}>
                      <div className="flex items-center">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {customer.name}
                        </p>
                        <span className={cn(
                          "ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                          isRTL && "ml-0 mr-2",
                          `bg-${getCustomerStatusColor(customer.status).split(' ')[1]}-100 text-${getCustomerStatusColor(customer.status).split(' ')[0]}-800 dark:bg-${getCustomerStatusColor(customer.status).split(' ')[1]}-900 dark:text-${getCustomerStatusColor(customer.status).split(' ')[0]}-200`
                        )}>
                          {formatCustomerStatus(customer.status)}
                        </span>
                        <span className={cn(
                          "ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
                          isRTL && "ml-0 mr-2"
                        )}>
                          {formatCustomerTier(customer.tier)}
                        </span>
                      </div>
                      <div className="mt-1 flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <EnvelopeIcon className="flex-shrink-0 mr-1.5 h-4 w-4" />
                        <span className="truncate">{customer.email}</span>
                      </div>
                      <div className="mt-1 flex items-center text-sm text-gray-500 dark:text-gray-400">
                        <PhoneIcon className="flex-shrink-0 mr-1.5 h-4 w-4" />
                        <span>{customer.phone}</span>
                      </div>
                      
                      {/* Authentication Status */}
                      <div className="mt-2 flex items-center space-x-2">
                        <span className={cn(
                          "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
                          customer.is_email_verified 
                            ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                            : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                        )}>
                          {customer.is_email_verified ? t('customers.verified') : t('customers.unverified')}
                        </span>
                        <span className={cn(
                          "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium",
                          customer.has_logged_in 
                            ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                            : "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
                        )}>
                          {customer.has_logged_in ? t('customers.active') : t('customers.inactive')}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      <div>{t('customers.totalOrders')}: {customer.total_orders}</div>
                      <div>{t('customers.totalSpent')}: ${customer.total_spent.toLocaleString()}</div>
                      {customer.last_login_at && (
                        <div>{t('customers.lastLogin')}: {new Date(customer.last_login_at).toLocaleDateString()}</div>
                      )}
                    </div>
                    <div className="flex items-center space-x-1">
                      {/* Credential Management Actions */}
                      {!customer.is_email_verified && (
                        <button
                          onClick={() => handleSendVerification(customer.id)}
                          className="p-1 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
                          title={t('customers.sendVerification')}
                        >
                          <EnvelopeIcon className="h-4 w-4" />
                        </button>
                      )}
                      {!customer.has_logged_in && (
                        <button
                          onClick={() => handleSendCredentials(customer.id)}
                          className="p-1 text-gray-400 hover:text-green-600 dark:hover:text-green-400"
                          title={t('customers.sendCredentials')}
                        >
                          <UserIcon className="h-4 w-4" />
                        </button>
                      )}
                      <button
                        onClick={() => openEditModal(customer)}
                        className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        title={t('customers.edit')}
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteCustomer(customer.id)}
                        className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                        title={t('customers.delete')}
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Create Customer Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  {t('customers.addCustomer')}
                </h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                {/* Basic Information */}
                <div className="border-b border-gray-200 dark:border-gray-700 pb-4">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                    {t('customers.basicInformation')}
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {t('customers.firstName')} *
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.first_name}
                        onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {t('customers.lastName')} *
                      </label>
                      <input
                        type="text"
                        required
                        value={formData.last_name}
                        onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                  </div>

                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {t('customers.email')} *
                    </label>
                    <input
                      type="email"
                      required
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>

                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {t('customers.phone')}
                    </label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
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
                        onChange={(e) => setFormData({ ...formData, send_credentials: e.target.checked })}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="send_credentials" className="ml-2 block text-sm text-gray-900 dark:text-white">
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
                            onChange={(e) => setFormData({ ...formData, verification_method: e.target.value })}
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
                            onChange={(e) => setFormData({ ...formData, welcome_message: e.target.value })}
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
                            onChange={(e) => setFormData({ ...formData, custom_instructions: e.target.value })}
                            rows={2}
                            placeholder={t('customers.customInstructionsPlaceholder')}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Customer Settings */}
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                    {t('customers.customerSettings')}
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {t('customers.status')}
                      </label>
                      <select
                        value={formData.customer_status}
                        onChange={(e) => setFormData({ ...formData, customer_status: e.target.value })}
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
                        onChange={(e) => setFormData({ ...formData, customer_tier: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        <option value="bronze">{t('customers.filters.bronze')}</option>
                        <option value="silver">{t('customers.filters.silver')}</option>
                        <option value="gold">{t('customers.filters.gold')}</option>
                        <option value="platinum">{t('customers.filters.platinum')}</option>
                      </select>
                    </div>
                  </div>

                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {t('customers.relationshipNotes')}
                    </label>
                    <textarea
                      value={formData.relationship_notes}
                      onChange={(e) => setFormData({ ...formData, relationship_notes: e.target.value })}
                      rows={3}
                      placeholder={t('customers.relationshipNotesPlaceholder')}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  {t('customers.cancel')}
                </button>
                <button
                  onClick={handleCreateCustomer}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  {t('customers.create')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Customer Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  {t('customers.editCustomer')}
                </h3>
                <button
                  onClick={() => setShowEditModal(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              
              {/* Similar form fields as create modal */}
              <div className="space-y-4">
                {/* Form fields would be similar to create modal */}
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {t('customers.editFormNote')}
                </div>
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  {t('customers.cancel')}
                </button>
                <button
                  onClick={handleUpdateCustomer}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  {t('customers.update')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
