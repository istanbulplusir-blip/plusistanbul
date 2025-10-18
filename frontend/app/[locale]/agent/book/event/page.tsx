'use client';

import { useState, useEffect } from 'react';
import { useAgentTranslations } from '@/lib/hooks/useAgentTranslations';
import { useAgent } from '@/app/lib/hooks/useAgent';
import { useLocale } from 'next-intl';
import { cn } from '@/lib/utils';
import {
  TicketIcon,
  CheckCircleIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  InformationCircleIcon,
  MapPinIcon,
} from '@heroicons/react/24/outline';

interface EventBookingData {
  customer_id: string;
  event_id: string;
  performance_id: string;
  section: string;
  ticket_type_id: string;
  quantity: number;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
  }>;
  special_requests?: string;
  notes?: string;
}

interface Event {
  id: string;
  title: string;
  description: string;
  venue: string;
  city: string;
  image: string;
  category: string;
  is_active: boolean;
}

interface Performance {
  id: string;
  event_id: string;
  date: string;
  time: string;
  venue: string;
  is_available: boolean;
  max_capacity: number;
  current_capacity: number;
}

interface TicketType {
  id: string;
  name: string;
  description: string;
  base_price: number;
  agent_price: number;
  section: string;
  is_available: boolean;
  max_quantity: number;
  available_quantity: number;
}

interface EventOption {
  id: string;
  name: string;
  description: string;
  base_price: number;
  agent_price: number;
  is_required: boolean;
  max_quantity: number;
}

interface BookingStep {
  id: string;
  title: string;
  description: string;
  isCompleted: boolean;
}

export default function AgentEventBookingPage() {
  const t = useAgentTranslations();
  const locale = useLocale();
  const isRTL = locale === 'fa';
  
  const {
    customers,
    loadCustomers,
    bookEvent,
    getPricingPreview,
    loading,
  } = useAgent();

  // State for booking data
  const [bookingData, setBookingData] = useState<EventBookingData>({
    customer_id: '',
    event_id: '',
    performance_id: '',
    section: '',
    ticket_type_id: '',
    quantity: 1,
    selected_options: [],
    special_requests: '',
    notes: ''
  });

  // State for UI
  const [currentStep, setCurrentStep] = useState(0);
  const [events, setEvents] = useState<Event[]>([]);
  const [performances, setPerformances] = useState<Performance[]>([]);
  const [ticketTypes, setTicketTypes] = useState<TicketType[]>([]);
  const [options, setOptions] = useState<EventOption[]>([]);
  const [pricing, setPricing] = useState<Record<string, unknown> | null>(null);
  const [loadingPricing, setLoadingPricing] = useState(false);

  // Steps configuration
  const steps: BookingStep[] = [
    {
      id: 'event',
      title: t.event.steps.event,
      description: t.event.steps.eventDesc,
      isCompleted: !!bookingData.event_id
    },
    {
      id: 'performance',
      title: t.event.steps.performance,
      description: t.event.steps.performanceDesc,
      isCompleted: !!bookingData.performance_id
    },
    {
      id: 'tickets',
      title: t.event.steps.tickets,
      description: t.event.steps.ticketsDesc,
      isCompleted: !!bookingData.ticket_type_id && bookingData.quantity > 0
    },
    {
      id: 'options',
      title: t.event.steps.options,
      description: t.event.steps.optionsDesc,
      isCompleted: true
    },
    {
      id: 'customer',
      title: t.event.steps.customer,
      description: t.event.steps.customerDesc,
      isCompleted: !!bookingData.customer_id
    },
    {
      id: 'pricing',
      title: t.event.steps.pricing,
      description: t.event.steps.pricingDesc,
      isCompleted: !!pricing
    },
    {
      id: 'confirm',
      title: t.event.steps.confirm,
      description: t.event.steps.confirmDesc,
      isCompleted: false
    }
  ];

  // Load initial data
  useEffect(() => {
    loadCustomers();
    loadEventData();
  }, [loadCustomers]);

  // Load event data (mock data for now)
  const loadEventData = () => {
    // Mock events
    setEvents([
      {
        id: '1',
        title: 'کنسرت موسیقی سنتی',
        description: 'کنسرت موسیقی سنتی ایرانی با اجرای استادان موسیقی',
        venue: 'تالار وحدت',
        city: 'تهران',
        image: '/images/events/concert.jpg',
        category: 'موسیقی',
        is_active: true
      },
      {
        id: '2',
        title: 'نمایش تئاتر',
        description: 'نمایش تئاتر کلاسیک با بازیگران مطرح',
        venue: 'تئاتر شهر',
        city: 'تهران',
        image: '/images/events/theater.jpg',
        category: 'تئاتر',
        is_active: true
      },
      {
        id: '3',
        title: 'جشنواره فیلم',
        description: 'جشنواره فیلم بین‌المللی',
        venue: 'سینما آزادی',
        city: 'تهران',
        image: '/images/events/film.jpg',
        category: 'سینما',
        is_active: true
      }
    ]);

    // Mock performances
    setPerformances([
      {
        id: '1',
        event_id: '1',
        date: '2024-02-15',
        time: '20:00',
        venue: 'تالار وحدت',
        is_available: true,
        max_capacity: 500,
        current_capacity: 300
      },
      {
        id: '2',
        event_id: '1',
        date: '2024-02-16',
        time: '20:00',
        venue: 'تالار وحدت',
        is_available: true,
        max_capacity: 500,
        current_capacity: 200
      },
      {
        id: '3',
        event_id: '2',
        date: '2024-02-20',
        time: '19:30',
        venue: 'تئاتر شهر',
        is_available: true,
        max_capacity: 300,
        current_capacity: 150
      }
    ]);

    // Mock ticket types
    setTicketTypes([
      {
        id: '1',
        name: 'VIP',
        description: 'بلیت VIP با بهترین مکان',
        base_price: 500000,
        agent_price: 425000,
        section: 'VIP',
        is_available: true,
        max_quantity: 4,
        available_quantity: 20
      },
      {
        id: '2',
        name: 'درجه یک',
        description: 'بلیت درجه یک با مکان مناسب',
        base_price: 300000,
        agent_price: 255000,
        section: 'درجه یک',
        is_available: true,
        max_quantity: 6,
        available_quantity: 50
      },
      {
        id: '3',
        name: 'درجه دو',
        description: 'بلیت درجه دو با قیمت مناسب',
        base_price: 200000,
        agent_price: 170000,
        section: 'درجه دو',
        is_available: true,
        max_quantity: 8,
        available_quantity: 100
      }
    ]);

    // Mock options
    setOptions([
      {
        id: 'parking',
        name: 'پارکینگ',
        description: 'پارکینگ اختصاصی برای رویداد',
        base_price: 50000,
        agent_price: 42500,
        is_required: false,
        max_quantity: 1
      },
      {
        id: 'refreshments',
        name: 'تنقلات',
        description: 'تنقلات و نوشیدنی برای رویداد',
        base_price: 100000,
        agent_price: 85000,
        is_required: false,
        max_quantity: 1
      },
      {
        id: 'backstage',
        name: 'دسترسی به پشت صحنه',
        description: 'دسترسی ویژه به پشت صحنه',
        base_price: 200000,
        agent_price: 170000,
        is_required: false,
        max_quantity: 1
      }
    ]);
  };

  // Calculate pricing
  const calculatePricing = async () => {
    if (!bookingData.event_id || !bookingData.ticket_type_id) return;

    setLoadingPricing(true);
    try {
      const previewData = {
        product_type: 'event' as const,
        event_id: bookingData.event_id,
        ticket_type_id: bookingData.ticket_type_id,
        quantity: bookingData.quantity,
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
  const updateBookingData = (updates: Partial<EventBookingData>) => {
    const newData = { ...bookingData, ...updates };
    setBookingData(newData);
    
    // Recalculate pricing if relevant fields changed
    if (updates.event_id || updates.ticket_type_id || updates.quantity) {
      setTimeout(() => calculatePricing(), 100);
    }
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
      await bookEvent(bookingData as unknown as Record<string, unknown>);
      alert(t.event.bookingSuccess);
    } catch (error) {
      console.error('Booking failed:', error);
      alert(t.event.bookingError);
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

  // Get selected data
  const selectedEvent = events.find(event => event.id === bookingData.event_id);
  const selectedPerformance = performances.find(perf => perf.id === bookingData.performance_id);
  const selectedTicketType = ticketTypes.find(ticket => ticket.id === bookingData.ticket_type_id);
  const selectedCustomer = customers.find(customer => customer.id === bookingData.customer_id);

  // Filter performances by selected event
  const availablePerformances = performances.filter(perf => perf.event_id === bookingData.event_id);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {t.event.title}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {t.event.subtitle}
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
                      {t.event.selectEvent}
                    </h3>
                    <div className="grid grid-cols-1 gap-4">
                      {events.map((event) => (
                        <div
                          key={event.id}
                          onClick={() => updateBookingData({ event_id: event.id })}
                          className={cn(
                            "p-4 border-2 rounded-lg cursor-pointer transition-all duration-200",
                            bookingData.event_id === event.id
                              ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                              : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                          )}
                        >
                          <div className="flex items-center space-x-4">
                            <div className="w-20 h-16 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center">
                              <TicketIcon className="w-8 h-8 text-gray-500" />
                            </div>
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {event.title}
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                {event.description}
                              </p>
                              <div className="flex items-center mt-2 text-sm text-gray-500 dark:text-gray-500">
                                <MapPinIcon className="w-4 h-4 mr-1" />
                                <span>{event.venue} - {event.city}</span>
                              </div>
                            </div>
                            <div className="text-right">
                              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                {event.category}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {currentStep === 1 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.event.selectPerformance}
                    </h3>
                    {availablePerformances.length === 0 ? (
                      <div className="text-center py-8">
                        <InformationCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
                        <p className="mt-2 text-gray-600 dark:text-gray-400">
                          {t.event.noPerformances}
                        </p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 gap-4">
                        {availablePerformances.map((performance) => (
                          <div
                            key={performance.id}
                            onClick={() => updateBookingData({ performance_id: performance.id })}
                            className={cn(
                              "p-4 border-2 rounded-lg cursor-pointer transition-all duration-200",
                              bookingData.performance_id === performance.id
                                ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                                : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                            )}
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <h4 className="font-medium text-gray-900 dark:text-white">
                                  {formatDate(performance.date)}
                                </h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  ساعت: {performance.time}
                                </p>
                                <p className="text-sm text-gray-500 dark:text-gray-500">
                                  {performance.venue}
                                </p>
                              </div>
                              <div className="text-right">
                                <div className="text-sm text-gray-600 dark:text-gray-400">
                                  {performance.current_capacity} / {performance.max_capacity}
                                </div>
                                <div className="text-xs text-gray-500 dark:text-gray-500">
                                  {t.event.availableTickets}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {currentStep === 2 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.event.selectTickets}
                    </h3>
                    <div className="space-y-4">
                      {ticketTypes.map((ticketType) => (
                        <div
                          key={ticketType.id}
                          onClick={() => updateBookingData({ 
                            ticket_type_id: ticketType.id,
                            section: ticketType.section
                          })}
                          className={cn(
                            "p-4 border-2 rounded-lg cursor-pointer transition-all duration-200",
                            bookingData.ticket_type_id === ticketType.id
                              ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                              : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                          )}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {ticketType.name}
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                {ticketType.description}
                              </p>
                              <p className="text-sm text-gray-500 dark:text-gray-500">
                                {t.event.section}: {ticketType.section}
                              </p>
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-semibold text-gray-900 dark:text-white">
                                {formatCurrency(ticketType.agent_price)}
                              </div>
                              <div className="text-sm text-gray-500 dark:text-gray-500 line-through">
                                {formatCurrency(ticketType.base_price)}
                              </div>
                              <div className="text-xs text-gray-500 dark:text-gray-500">
                                {ticketType.available_quantity} {t.event.available}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {bookingData.ticket_type_id && (
                      <div className="mt-6">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                          {t.event.quantity}
                        </label>
                        <input
                          type="number"
                          min="1"
                          max={selectedTicketType?.max_quantity || 8}
                          value={bookingData.quantity}
                          onChange={(e) => updateBookingData({ quantity: parseInt(e.target.value) })}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        />
                        {selectedTicketType && (
                          <p className="mt-1 text-sm text-gray-500 dark:text-gray-500">
                            حداکثر: {selectedTicketType.max_quantity} بلیت
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {currentStep === 3 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.event.additionalOptions}
                    </h3>
                    <div className="space-y-4">
                      {options.map((option) => (
                        <div key={option.id} className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {option.name}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {option.description}
                            </p>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {formatCurrency(option.agent_price)}
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
                  </div>
                )}

                {currentStep === 4 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.event.selectCustomer}
                    </h3>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {t.event.customer}
                      </label>
                      <select
                        value={bookingData.customer_id}
                        onChange={(e) => updateBookingData({ customer_id: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        <option value="">{t.event.selectCustomer}</option>
                        {customers.map((customer) => (
                          <option key={customer.id} value={customer.id}>
                            {customer.name} - {customer.email}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                )}

                {currentStep === 5 && (
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.event.pricingSummary}
                    </h3>
                    {loadingPricing ? (
                      <div className="flex items-center justify-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        <span className="ml-3 text-gray-600 dark:text-gray-400">
                          {t.event.calculatingPricing}
                        </span>
                      </div>
                    ) : pricing ? (
                      <div className="space-y-4">
                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">
                                {t.event.basePrice}
                              </span>
                              <span className="text-gray-900 dark:text-white">
                                {formatCurrency(pricing.base_price as number)}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">
                                {t.event.agentDiscount}
                              </span>
                              <span className="text-green-600">
                                -{formatCurrency(pricing.discount_amount as number)}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600 dark:text-gray-400">
                                {t.event.additionalOptions}
                              </span>
                              <span className="text-gray-900 dark:text-white">
                                {formatCurrency(pricing.options_total as number)}
                              </span>
                            </div>
                            <div className="border-t border-gray-200 dark:border-gray-600 pt-2">
                              <div className="flex justify-between">
                                <span className="font-medium text-gray-900 dark:text-white">
                                  {t.event.total}
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
                          {t.event.pricingNotAvailable}
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {currentStep === 6 && (
                  <div className="space-y-6">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {t.event.confirmBooking}
                    </h3>
                    
                    <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                      <h4 className="font-medium text-gray-900 dark:text-white mb-4">
                        {t.event.bookingDetails}
                      </h4>
                      
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.event.event}
                          </span>
                          <span className="text-gray-900 dark:text-white">
                            {selectedEvent?.title}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.event.date}
                          </span>
                          <span className="text-gray-900 dark:text-white">
                            {selectedPerformance ? formatDate(selectedPerformance.date) : ''}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.event.time}
                          </span>
                          <span className="text-gray-900 dark:text-white">
                            {selectedPerformance?.time}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.event.ticketType}
                          </span>
                          <span className="text-gray-900 dark:text-white">
                            {selectedTicketType?.name}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.event.quantity}
                          </span>
                          <span className="text-gray-900 dark:text-white">
                            {bookingData.quantity} بلیت
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.event.customer}
                          </span>
                          <span className="text-gray-900 dark:text-white">
                            {selectedCustomer?.name}
                          </span>
                        </div>
                        
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">
                            {t.event.total}
                          </span>
                          <span className="font-bold text-lg text-gray-900 dark:text-white">
                            {pricing ? formatCurrency(pricing.total as number) : 'محاسبه نشده'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {t.event.specialRequests}
                      </label>
                      <textarea
                        value={bookingData.special_requests || ''}
                        onChange={(e) => updateBookingData({ special_requests: e.target.value })}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        placeholder={t.event.specialRequestsPlaceholder}
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
                    <span>{t.event.previous}</span>
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
                      <span>{t.event.next}</span>
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
                      <span>{t.event.confirmBooking}</span>
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
                {t.event.bookingSummary}
              </h3>
              
              <div className="space-y-4">
                {selectedEvent && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {t.event.event}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {selectedEvent.title}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-500">
                      {selectedEvent.venue} - {selectedEvent.city}
                    </p>
                  </div>
                )}

                {selectedPerformance && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {t.event.date}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {formatDate(selectedPerformance.date)}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-500">
                      ساعت: {selectedPerformance.time}
                    </p>
                  </div>
                )}

                {selectedTicketType && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {t.event.ticketType}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {selectedTicketType.name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-500">
                      {t.event.section}: {selectedTicketType.section}
                    </p>
                  </div>
                )}

                {bookingData.quantity > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {t.event.quantity}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {bookingData.quantity} بلیت
                    </p>
                  </div>
                )}

                {selectedCustomer && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">
                      {t.event.customer}
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
                        {t.event.total}
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
