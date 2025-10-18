'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Loading } from '@/components/ui/Loading';
import { agentApi, Customer as CustomerType, Tour, TourVariant, PricingData } from '@/lib/api/agents';

interface BookingData {
  tour: Tour | null;
  variant: TourVariant | null;
  date: string | null;
  participants: {
    adults: number;
    children: number;
    infants: number;
  };
  options: number[];
  customer: CustomerType | null;
  pricing: PricingData | null;
}

interface CustomerSelectorProps {
  bookingData: BookingData;
  onComplete: (data: Partial<BookingData>) => void;
  onPrevious: () => void;
  onNext: () => void;
  isFirstStep: boolean;
  isLastStep: boolean;
}

export default function CustomerSelector({ 
  bookingData, 
  onComplete, 
  onPrevious, 
  isFirstStep 
}: CustomerSelectorProps) {
  const t = useTranslations('agent.booking.customerSelector');
  const [customers, setCustomers] = useState<CustomerType[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerType | null>(bookingData.customer);
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewCustomerForm, setShowNewCustomerForm] = useState(false);
  const [newCustomer, setNewCustomer] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    national_id: '',
    birth_date: ''
  });

  useEffect(() => {
    // Fetch customers from API
    const fetchCustomers = async () => {
      try {
        setLoading(true);
        const response = await agentApi.customers.getCustomers();
        // Handle both array and object response formats
        const customersData = Array.isArray(response) ? response : ((response as { customers?: CustomerType[] }).customers || []);
        setCustomers(customersData);
      } catch (error) {
        console.error('Error fetching customers:', error);
        // Fallback to mock data if API fails
        const mockCustomers: CustomerType[] = [
          {
            id: 1,
            first_name: 'احمد',
            last_name: 'محمدی',
            email: 'ahmad.mohammadi@email.com',
            phone: '+98 912 345 6789',
            national_id: '1234567890',
            birth_date: '1985-03-15',
            created_at: '2023-01-15',
            total_bookings: 5,
            total_spent: 1250
          },
          {
            id: 2,
            first_name: 'فاطمه',
            last_name: 'احمدی',
            email: 'fateme.ahmadi@email.com',
            phone: '+98 912 345 6790',
            national_id: '1234567891',
            birth_date: '1990-07-22',
            created_at: '2023-02-20',
            total_bookings: 3,
            total_spent: 750
          },
          {
            id: 3,
            first_name: 'علی',
            last_name: 'رضایی',
            email: 'ali.rezaei@email.com',
            phone: '+98 912 345 6791',
            national_id: '1234567892',
            birth_date: '1988-11-08',
            created_at: '2023-03-10',
            total_bookings: 2,
            total_spent: 400
          }
        ];
        setCustomers(mockCustomers);
      } finally {
        setLoading(false);
      }
    };

    fetchCustomers();
  }, []);

  const filteredCustomers = Array.isArray(customers) ? customers.filter(customer =>
    (customer.first_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (customer.last_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (customer.email || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (customer.phone || '').includes(searchTerm)
  ) : [];

  const handleCustomerSelect = (customer: CustomerType) => {
    setSelectedCustomer(customer);
    setShowNewCustomerForm(false);
  };

  const handleNewCustomerSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const customer = await agentApi.customers.createCustomer(newCustomer);
      setCustomers(prev => [customer, ...prev]);
      setSelectedCustomer(customer);
      setShowNewCustomerForm(false);
      setNewCustomer({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        national_id: '',
        birth_date: ''
      });
    } catch (error) {
      console.error('Error creating customer:', error);
      // Fallback to local creation if API fails
      const customer: CustomerType = {
        id: Date.now(), // Generate unique ID
        ...newCustomer,
        created_at: new Date().toISOString().split('T')[0],
        total_bookings: 0,
        total_spent: 0
      };
      
      setCustomers(prev => [customer, ...prev]);
      setSelectedCustomer(customer);
      setShowNewCustomerForm(false);
      setNewCustomer({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        national_id: '',
        birth_date: ''
      });
    }
  };

  const handleContinue = () => {
    if (selectedCustomer) {
      onComplete({ customer: selectedCustomer });
    }
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Search and New Customer Button */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Input
            type="text"
            placeholder={t('searchCustomers')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        <Button
          variant="outline"
          onClick={() => setShowNewCustomerForm(!showNewCustomerForm)}
          className="whitespace-nowrap"
        >
          {showNewCustomerForm ? t('cancelNewCustomer') : t('newCustomer')}
        </Button>
      </div>

      {/* New Customer Form */}
      {showNewCustomerForm && (
        <Card>
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              {t('newCustomerForm')}
            </h3>
            <form onSubmit={handleNewCustomerSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('firstName')} *
                  </label>
                  <Input
                    type="text"
                    value={newCustomer.first_name}
                    onChange={(e) => setNewCustomer(prev => ({ ...prev, first_name: e.target.value }))}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('lastName')} *
                  </label>
                  <Input
                    type="text"
                    value={newCustomer.last_name}
                    onChange={(e) => setNewCustomer(prev => ({ ...prev, last_name: e.target.value }))}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('email')} *
                  </label>
                  <Input
                    type="email"
                    value={newCustomer.email}
                    onChange={(e) => setNewCustomer(prev => ({ ...prev, email: e.target.value }))}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('phone')} *
                  </label>
                  <Input
                    type="tel"
                    value={newCustomer.phone}
                    onChange={(e) => setNewCustomer(prev => ({ ...prev, phone: e.target.value }))}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('nationalId')} *
                  </label>
                  <Input
                    type="text"
                    value={newCustomer.national_id}
                    onChange={(e) => setNewCustomer(prev => ({ ...prev, national_id: e.target.value }))}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t('birthDate')} *
                  </label>
                  <Input
                    type="date"
                    value={newCustomer.birth_date}
                    onChange={(e) => setNewCustomer(prev => ({ ...prev, birth_date: e.target.value }))}
                    required
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowNewCustomerForm(false)}
                >
                  {t('cancel')}
                </Button>
                <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                  {t('createCustomer')}
                </Button>
              </div>
            </form>
          </div>
        </Card>
      )}

      {/* Customers List */}
      <div className="space-y-4">
        {filteredCustomers.map((customer) => (
          <Card
            key={customer.id}
            className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
              selectedCustomer?.id === customer.id 
                ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                : 'hover:ring-1 hover:ring-gray-300'
            }`}
            onClick={() => handleCustomerSelect(customer)}
          >
            <div className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {customer.first_name} {customer.last_name}
                  </h3>
                  <div className="mt-2 space-y-1">
                    <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      {customer.email}
                    </div>
                    <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      {customer.phone}
                    </div>
                    <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                      </svg>
                      {customer.national_id}
                    </div>
                  </div>
                </div>
                
                <div className="text-right space-y-2">
                  <div className="flex space-x-2">
                    <Badge variant="secondary">
                      {customer.total_bookings} {t('bookings')}
                    </Badge>
                    <Badge variant="outline">
                      ${customer.total_spent} {t('spent')}
                    </Badge>
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {t('memberSince')}: {new Date(customer.created_at).toLocaleDateString('fa-IR')}
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {filteredCustomers.length === 0 && !showNewCustomerForm && (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
            {t('noCustomersFound')}
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {t('noCustomersDescription')}
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between pt-6 border-t border-gray-200 dark:border-gray-700">
        <Button
          variant="outline"
          onClick={onPrevious}
          disabled={isFirstStep}
        >
          {t('previous')}
        </Button>
        
        <Button
          onClick={handleContinue}
          disabled={!selectedCustomer}
          className="bg-blue-600 hover:bg-blue-700"
        >
          {t('continue')}
        </Button>
      </div>
    </div>
  );
}
