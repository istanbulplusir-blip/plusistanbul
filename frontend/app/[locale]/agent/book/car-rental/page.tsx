'use client';

import { useState, useEffect } from 'react';
import { useAgentTranslations } from '@/lib/hooks/useAgentTranslations';
import { useAgent } from '@/app/lib/hooks/useAgent';
import { useLocale } from 'next-intl';
import { cn } from '@/lib/utils';
import {
  TruckIcon,
  CalendarDaysIcon,
  CheckCircleIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  InformationCircleIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';

interface CarRentalBookingData {
  customer_id: string;
  car_id: string;
  pickup_date: string;
  pickup_time: string;
  dropoff_date: string;
  dropoff_time: string;
  days: number;
  hours?: number;
  include_insurance?: boolean;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  special_requests?: string;
  notes?: string;
}

interface Car {
  id: string;
  name: string;
  model: string;
  year: number;
  capacity: number;
  transmission: 'manual' | 'automatic';
  fuel_type: 'gasoline' | 'diesel' | 'hybrid' | 'electric';
  daily_rate: number;
  agent_daily_rate: number;
  hourly_rate: number;
  agent_hourly_rate: number;
  features: string[];
  image: string;
  is_available: boolean;
}

interface CarOption {
  id: string;
  name: string;
  description: string;
  daily_price: number;
  agent_daily_price: number;
  hourly_price: number;
  agent_hourly_price: number;
  is_required: boolean;
  max_quantity: number;
}

interface BookingStep {
  id: string;
  title: string;
  description: string;
  isCompleted: boolean;
}

export default function AgentCarRentalBookingPage() {
  const t = useAgentTranslations();
  const locale = useLocale();
  const isRTL = locale === 'fa';
  
  const {
    customers,
    loadCustomers,
    bookCarRental,
    getPricingPreview,
    loading,
  } = useAgent();

  // State for booking data
  const [bookingData, setBookingData] = useState<CarRentalBookingData>({
    customer_id: '',
    car_id: '',
    pickup_date: '',
    pickup_time: '',
    dropoff_date: '',
    dropoff_time: '',
    days: 1,
    hours: 0,
    include_insurance: false,
    selected_options: [],
    special_requests: '',
    notes: ''
  });

  // State for UI
  const [currentStep, setCurrentStep] = useState(0);
  const [cars, setCars] = useState<Car[]>([]);
  const [options, setOptions] = useState<CarOption[]>([]);
  const [pricing, setPricing] = useState<Record<string, unknown> | null>(null);
  const [loadingPricing, setLoadingPricing] = useState(false);

  // Steps configuration
  const steps: BookingStep[] = [
    {
      id: 'car',
      title: t.carRental.steps.car.title,
      description: t.carRental.steps.car.description,
      isCompleted: !!bookingData.car_id
    },
    {
      id: 'dates',
      title: t.carRental.steps.dates.title,
      description: t.carRental.steps.dates.description,
      isCompleted: !!bookingData.pickup_date && !!bookingData.dropoff_date
    },
    {
      id: 'options',
      title: t.carRental.steps.options.title,
      description: t.carRental.steps.options.description,
      isCompleted: true
    },
    {
      id: 'customer',
      title: t.carRental.steps.customer.title,
      description: t.carRental.steps.customer.description,
      isCompleted: !!bookingData.customer_id
    },
    {
      id: 'pricing',
      title: t.carRental.steps.pricing.title,
      description: t.carRental.steps.pricing.description,
      isCompleted: !!pricing
    },
    {
      id: 'confirm',
      title: t.carRental.steps.confirm.title,
      description: t.carRental.steps.confirm.description,
      isCompleted: false
    }
  ];

  // Load initial data
  useEffect(() => {
    loadCustomers();
    loadCarData();
  }, [loadCustomers]);

  // Load car data (mock data for now)
  const loadCarData = () => {
    // Mock cars
    setCars([
      {
        id: '1',
        name: 'پراید',
        model: 'Pride',
        year: 2023,
        capacity: 5,
        transmission: 'manual',
        fuel_type: 'gasoline',
        daily_rate: 500000,
        agent_daily_rate: 425000,
        hourly_rate: 25000,
        agent_hourly_rate: 21250,
        features: ['تهویه مطبوع', 'رادیو', 'قفل مرکزی'],
        image: '/images/cars/pride.jpg',
        is_available: true
      },
      {
        id: '2',
        name: 'سمند',
        model: 'Samand',
        year: 2023,
        capacity: 5,
        transmission: 'manual',
        fuel_type: 'gasoline',
        daily_rate: 700000,
        agent_daily_rate: 595000,
        hourly_rate: 35000,
        agent_hourly_rate: 29750,
        features: ['تهویه مطبوع', 'رادیو', 'قفل مرکزی', 'پاور استیرینگ'],
        image: '/images/cars/samand.jpg',
        is_available: true
      },
      {
        id: '3',
        name: 'پژو 206',
        model: 'Peugeot 206',
        year: 2023,
        capacity: 5,
        transmission: 'manual',
        fuel_type: 'gasoline',
        daily_rate: 800000,
        agent_daily_rate: 680000,
        hourly_rate: 40000,
        agent_hourly_rate: 34000,
        features: ['تهویه مطبوع', 'رادیو', 'قفل مرکزی', 'پاور استیرینگ', 'کیسه هوا'],
        image: '/images/cars/peugeot206.jpg',
        is_available: true
      }
    ]);

    // Mock options
    setOptions([
      {
        id: 'insurance',
        name: 'بیمه کامل',
        description: 'بیمه کامل خودرو شامل بیمه شخص ثالث و بیمه بدنه',
        daily_price: 50000,
        agent_daily_price: 42500,
        hourly_price: 2500,
        agent_hourly_price: 2125,
        is_required: false,
        max_quantity: 1
      },
      {
        id: 'gps',
        name: 'سیستم GPS',
        description: 'سیستم ناوبری GPS برای مسیریابی',
        daily_price: 30000,
        agent_daily_price: 25500,
        hourly_price: 1500,
        agent_hourly_price: 1275,
        is_required: false,
        max_quantity: 1
      },
      {
        id: 'child_seat',
        name: 'صندلی کودک',
        description: 'صندلی کودک برای کودکان زیر 4 سال',
        daily_price: 20000,
        agent_daily_price: 17000,
        hourly_price: 1000,
        agent_hourly_price: 850,
        is_required: false,
        max_quantity: 2
      }
    ]);
  };

  // Calculate pricing
  const calculatePricing = async () => {
    if (!bookingData.car_id || !bookingData.pickup_date || !bookingData.dropoff_date) return;

    setLoadingPricing(true);
    try {
      const previewData = {
        product_type: 'car_rental' as const,
        car_id: bookingData.car_id,
        days: bookingData.days,
        hours: bookingData.hours || 0,
        include_insurance: bookingData.include_insurance || false,
        selected_options: bookingData.selected_options || []
      };

      const result = await getPricingPreview(previewData);
      setPricing(result);
    } catch (error) {
      console.error('Pricing calculation failed:', error);
    } finally {
      setLoadingPricing(false);
    }
  };

  // Update booking data and recalculate pricing
  const updateBookingData = (updates: Partial<CarRentalBookingData>) => {
    const newData = { ...bookingData, ...updates };
    setBookingData(newData);
    
    // Recalculate pricing if relevant fields changed
    if (updates.car_id || updates.pickup_date || updates.dropoff_date || updates.include_insurance) {
      setTimeout(() => calculatePricing(), 100);
    }
  };

  // Calculate rental duration
  const calculateDuration = () => {
    if (!bookingData.pickup_date || !bookingData.dropoff_date) return { days: 0, hours: 0 };

    const pickupDate = new Date(bookingData.pickup_date);
    const dropoffDate = new Date(bookingData.dropoff_date);
    const diffTime = dropoffDate.getTime() - pickupDate.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return { days: Math.max(1, diffDays), hours: 0 };
  };

  // Handle step navigation
  const handleNextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePreviousStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // Handle booking submission
  const handleBookingSubmit = async () => {
    try {
      await bookCarRental(bookingData as unknown as Record<string, unknown>);
      alert(t.carRental.bookingSuccess);
    } catch (error) {
      console.error('Booking failed:', error);
      alert(t.carRental.bookingError);
    }
  };

  // Format currency
  const formatCurrency = (amount: number, currency: string = 'IRR') => {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(locale, {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Get selected car
  const selectedCar = cars.find(car => car.id === bookingData.car_id);
  const selectedCustomer = customers.find(customer => customer.id === bookingData.customer_id);
  const duration = calculateDuration();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {t.carRental.title}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {t.carRental.subtitle}
          </p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg mb-8">
          <div className="p-6">
            <div className="flex items-center justify-between">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center flex-1">
                  <div className="flex flex-col items-center">
                    <div className={cn(
                      "flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-300",
                      index <= currentStep 
                        ? 'bg-blue-600 border-blue-600 text-white shadow-lg' 
                        : 'bg-gray-200 border-gray-300 text-gray-500 dark:bg-gray-700 dark:border-gray-600'
                    )}>
                      {index < currentStep ? (
                        <CheckCircleIcon className="w-6 h-6" />
                      ) : (
                        <span className="text-sm font-bold">{index + 1}</span>
                      )}
                    </div>
                    <div className="mt-2 text-center">
                      <p className={cn(
                        "text-xs font-medium",
                        index <= currentStep 
                          ? 'text-blue-600 dark:text-blue-400' 
                          : 'text-gray-500 dark:text-gray-400'
                      )}>
                        {step.title}
                      </p>
                      {index === currentStep && (
                        <div className="mt-1 w-2 h-2 bg-blue-600 rounded-full mx-auto animate-pulse"></div>
                      )}
                    </div>
                  </div>
                  {index < steps.length - 1 && (
                    <div className={cn(
                      "flex-1 h-0.5 mx-2 transition-all duration-300",
                      index < currentStep ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                    )} />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="p-6">
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {steps[currentStep].title}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    {steps[currentStep].description}
                  </p>
                </div>

                {/* Step Content */}
                {currentStep === 0 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.carRental.selectCar}
                    </h3>
                    <div className="grid grid-cols-1 gap-4">
                      {cars.map((car) => (
                        <div
                          key={car.id}
                          onClick={() => updateBookingData({ car_id: car.id })}
                          className={cn(
                            "p-4 border-2 rounded-lg cursor-pointer transition-all duration-200",
                            bookingData.car_id === car.id
                              ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                              : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                          )}
                        >
                          <div className="flex items-center space-x-4">
                            <div className="w-20 h-16 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                              <TruckIcon className="w-8 h-8 text-gray-500" />
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {car.name} {car.model} ({car.year})
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                ظرفیت: {car.capacity} نفر • {car.transmission === 'manual' ? 'دستی' : 'اتوماتیک'} • {car.fuel_type}
                              </p>
                              <div className="flex flex-wrap gap-2 mt-2">
                                {car.features.slice(0, 3).map((feature, index) => (
                                  <span key={index} className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-2 py-1 rounded">
                                    {feature}
                                  </span>
                                ))}
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-semibold text-gray-900 dark:text-white">
                                {formatCurrency(car.agent_daily_rate)}/روز
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-500 line-through">
                                {formatCurrency(car.daily_rate)}/روز
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {currentStep === 1 && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.carRental.selectDates}
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t.carRental.pickupDate}
                        </label>
                        <input
                          type="date"
                          value={bookingData.pickup_date}
                          onChange={(e) => updateBookingData({ pickup_date: e.target.value })}
                          min={new Date().toISOString().split('T')[0]}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t.carRental.pickupTime}
                        </label>
                        <input
                          type="time"
                          value={bookingData.pickup_time}
                          onChange={(e) => updateBookingData({ pickup_time: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t.carRental.dropoffDate}
                        </label>
                        <input
                          type="date"
                          value={bookingData.dropoff_date}
                          onChange={(e) => updateBookingData({ dropoff_date: e.target.value })}
                          min={bookingData.pickup_date || new Date().toISOString().split('T')[0]}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t.carRental.dropoffTime}
                        </label>
                        <input
                          type="time"
                          value={bookingData.dropoff_time}
                          onChange={(e) => updateBookingData({ dropoff_time: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                      </div>
                    </div>

                    {bookingData.pickup_date && bookingData.dropoff_date && (
                      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                        <div className="flex items-center">
                          <CalendarDaysIcon className="w-5 h-5 text-blue-600 mr-2" />
                          <span className="text-blue-800 dark:text-blue-200 font-medium">
                            مدت اجاره: {duration.days} روز
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {currentStep === 2 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.carRental.additionalOptions}
                    </h3>
                    
                    <div className="space-y-4">
                      {options.map((option) => (
                        <div key={option.id} className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                          <div className="flex-1">
                            <div className="flex items-center">
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {option.name}
                              </h4>
                              {option.is_required && (
                                <span className="ml-2 text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                                  {t.carRental.required}
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {option.description}
                            </p>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {formatCurrency(option.agent_daily_price)}/روز
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              checked={bookingData.selected_options?.some(opt => opt.option_id === option.id) || false}
                              onChange={(e) => {
                                const currentOptions = bookingData.selected_options || [];
                                if (e.target.checked) {
                                  updateBookingData({
                                    selected_options: [...currentOptions, { option_id: option.id, quantity: 1 }]
                                  });
                                } else {
                                  updateBookingData({
                                    selected_options: currentOptions.filter(opt => opt.option_id !== option.id)
                                  });
                                }
                              }}
                              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="flex items-center p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                      <input
                        type="checkbox"
                        id="insurance"
                        checked={bookingData.include_insurance || false}
                        onChange={(e) => updateBookingData({ include_insurance: e.target.checked })}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="insurance" className="ml-3 flex-1">
                        <div className="flex items-center">
                          <ShieldCheckIcon className="w-5 h-5 text-green-600 mr-2" />
                          <span className="font-medium text-gray-900 dark:text-white">
                            {t.carRental.includeInsurance}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {t.carRental.insuranceDescription}
                        </p>
                      </label>
                    </div>
                  </div>
                )}

                {currentStep === 3 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.carRental.selectCustomer}
                    </h3>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {t.carRental.customer}
                      </label>
                      <select
                        value={bookingData.customer_id}
                        onChange={(e) => updateBookingData({ customer_id: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        <option value="">{t.carRental.selectCustomer}</option>
                        {customers.map((customer) => (
                          <option key={customer.id} value={customer.id}>
                            {customer.name} - {customer.email}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                )}

                {currentStep === 4 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.carRental.pricingSummary}
                    </h3>
                    {loadingPricing ? (
                      <div className="flex items-center justify-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        <span className="ml-3 text-gray-600 dark:text-gray-400">
                          {t.carRental.calculatingPricing}
                        </span>
                      </div>
                    ) : pricing ? (
                      <div className="space-y-4">
                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">
                                {t.carRental.basePrice}
                              </span>
                              <span className="text-gray-900 dark:text-white">
                                {formatCurrency(pricing.base_price as number)}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">
                                {t.carRental.agentDiscount}
                              </span>
                              <span className="text-green-600">
                                -{formatCurrency(pricing.discount_amount as number)}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">
                                {t.carRental.additionalOptions}
                              </span>
                              <span className="text-gray-900 dark:text-white">
                                {formatCurrency(pricing.options_total as number)}
                              </span>
                            </div>
                            <div className="border-t border-gray-200 dark:border-gray-600 pt-2">
                              <div className="flex justify-between">
                                <span className="font-medium text-gray-900 dark:text-white">
                                  {t.carRental.total}
                                </span>
                                <span className="font-bold text-lg text-gray-900 dark:text-white">
                                  {formatCurrency(pricing.total as number)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <InformationCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
                        <p className="mt-2 text-gray-600 dark:text-gray-400">
                          {t.carRental.pricingNotAvailable}
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {currentStep === 5 && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.carRental.confirmBooking}
                    </h3>
                    
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                      <h4 className="font-medium text-gray-900 dark:text-white mb-4">
                        {t.carRental.bookingDetails}
                      </h4>
                      
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.carRental.car}
                          </span>
                          <span className="text-gray-900 dark:text-white">
                            {selectedCar?.name} {selectedCar?.model}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.carRental.pickupDate}
                          </span>
                          <span className="text-gray-900 dark:text-white">
                            {formatDate(bookingData.pickup_date)}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.carRental.dropoffDate}
                          </span>
                          <span className="text-gray-900 dark:text-white">
                            {formatDate(bookingData.dropoff_date)}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.carRental.duration}
                          </span>
                          <span className="text-gray-900 dark:text-white">
                            {duration.days} روز
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.carRental.customer}
                          </span>
                          <span className="text-gray-900 dark:text-white">
                            {selectedCustomer?.name}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.carRental.total}
                          </span>
                          <span className="font-bold text-lg text-gray-900 dark:text-white">
                            {pricing ? formatCurrency(pricing.total as number) : 'محاسبه نشده'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {t.carRental.specialRequests}
                      </label>
                      <textarea
                        value={bookingData.special_requests || ''}
                        onChange={(e) => updateBookingData({ special_requests: e.target.value })}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        placeholder={t.carRental.specialRequestsPlaceholder}
                      />
                    </div>
                  </div>
                )}

                {/* Navigation Buttons */}
                <div className="flex justify-between mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={handlePreviousStep}
                    disabled={currentStep === 0}
                    className={cn(
                      "inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed",
                      isRTL ? "space-x-reverse space-x-2" : "space-x-2"
                    )}
                  >
                    <ArrowLeftIcon className="w-4 h-4" />
                    <span>{t.carRental.previous}</span>
                  </button>

                  {currentStep < steps.length - 1 ? (
                    <button
                      onClick={handleNextStep}
                      disabled={!steps[currentStep].isCompleted}
                      className={cn(
                        "inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed",
                        isRTL ? "space-x-reverse space-x-2" : "space-x-2"
                      )}
                    >
                      <span>{t.carRental.next}</span>
                      <ArrowRightIcon className="w-4 h-4" />
                    </button>
                  ) : (
                    <button
                      onClick={handleBookingSubmit}
                      disabled={loading || !pricing}
                      className={cn(
                        "inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed",
                        isRTL ? "space-x-reverse space-x-2" : "space-x-2"
                      )}
                    >
                      <CheckCircleIcon className="w-4 h-4" />
                      <span>{t.carRental.confirmBooking}</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 sticky top-8">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                {t.carRental.bookingSummary}
              </h3>
              
              <div className="space-y-4">
                {selectedCar && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {t.carRental.car}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {selectedCar.name} {selectedCar.model}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-500">
                      {selectedCar.year} • {selectedCar.capacity} نفر
                    </p>
                  </div>
                )}

                {bookingData.pickup_date && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {t.carRental.pickupDate}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {formatDate(bookingData.pickup_date)}
                    </p>
                    {bookingData.pickup_time && (
                      <p className="text-sm text-gray-500 dark:text-gray-500">
                        ساعت: {bookingData.pickup_time}
                      </p>
                    )}
                  </div>
                )}

                {bookingData.dropoff_date && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {t.carRental.dropoffDate}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {formatDate(bookingData.dropoff_date)}
                    </p>
                    {bookingData.dropoff_time && (
                      <p className="text-sm text-gray-500 dark:text-gray-500">
                        ساعت: {bookingData.dropoff_time}
                      </p>
                    )}
                  </div>
                )}

                {duration.days > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {t.carRental.duration}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {duration.days} روز
                    </p>
                  </div>
                )}

                {selectedCustomer && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {t.carRental.customer}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {selectedCustomer.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-500">
                      {selectedCustomer.email}
                    </p>
                  </div>
                )}

                {pricing && (
                  <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                    <div className="flex justify-between items-center">
                      <span className="font-medium text-gray-900 dark:text-white">
                        {t.carRental.total}
                      </span>
                      <span className="font-bold text-lg text-gray-900 dark:text-white">
                        {formatCurrency(pricing.total as number)}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
