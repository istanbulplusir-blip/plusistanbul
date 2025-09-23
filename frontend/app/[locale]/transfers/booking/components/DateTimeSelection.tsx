'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useTransferBookingStore } from '@/lib/stores/transferBookingStore';
import { Calendar, Clock, ArrowLeft, ArrowRight, AlertCircle } from 'lucide-react';
import Select from 'react-select';

interface DateTimeSelectionProps {
  onNext: () => void;
  onBack: () => void;
}

export default function DateTimeSelection({ onNext, onBack }: DateTimeSelectionProps) {
  const t = useTranslations('transfers');
  
  // Get booking state from store
  const {
    trip_type,
    outbound_date,
    outbound_time,
    return_date,
    return_time,
    route_data,
    setTripType,
    setDateTime,
    isStepValid,
  } = useTransferBookingStore();

  // Local state for form inputs
  const [localOutboundDate, setLocalOutboundDate] = useState(outbound_date || '');
  const [localOutboundTime, setLocalOutboundTime] = useState(outbound_time || '');
  const [localReturnDate, setLocalReturnDate] = useState(return_date || '');
  const [localReturnTime, setLocalReturnTime] = useState(return_time || '');
  
  // Browser compatibility state
  const [isMobile, setIsMobile] = useState(false);
  const [useFallbackDatePicker, setUseFallbackDatePicker] = useState(false);
  
  // Validation state
  const [validationErrors, setValidationErrors] = useState<{
    outbound?: string;
    return?: string;
  }>({});

  // Detect mobile and date picker support
  useEffect(() => {
    const checkMobileAndDateSupport = () => {
      const isMobileDevice = /iPhone|iPad|iPod|Android|webOS|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
      setIsMobile(isMobileDevice);
      
      // Test if native date picker works properly
      const input = document.createElement('input');
      input.type = 'date';
      input.value = 'not-a-date';
      const supportsDate = input.value !== 'not-a-date';
      
      // Use fallback for problematic browsers or if native doesn't work
      const isProblematicBrowser = /Safari/i.test(navigator.userAgent) && /iPhone|iPad|iPod/i.test(navigator.userAgent);
      setUseFallbackDatePicker(!supportsDate || (isMobileDevice && isProblematicBrowser));
    };

    checkMobileAndDateSupport();
  }, []);

  // Handle trip type change
  const handleTripTypeChange = (newTripType: 'one_way' | 'round_trip') => {
    setTripType(newTripType);
    if (newTripType === 'one_way') {
      setLocalReturnDate('');
      setLocalReturnTime('');
      setValidationErrors(prev => ({ ...prev, return: undefined }));
    }
  };

  // Handle outbound date/time change
  const handleOutboundChange = (date: string, time: string) => {
    setLocalOutboundDate(date);
    setLocalOutboundTime(time);
    setDateTime(date, time, false);
    
    // Clear return validation if outbound changes
    if (trip_type === 'round_trip') {
      setValidationErrors(prev => ({ ...prev, return: undefined }));
    }
    
    // Validate immediately
    validateOutboundDateTime(date, time);
  };

  // Handle return date/time change
  const handleReturnChange = (date: string, time: string) => {
    setLocalReturnDate(date);
    setLocalReturnTime(time);
    setDateTime(date, time, true);
    
    // Validate immediately
    validateReturnDateTime(date, time);
  };

  // Real-time validation for outbound
  const validateOutboundDateTime = (date: string, time: string) => {
    if (!date || !time) {
      setValidationErrors(prev => ({ ...prev, outbound: undefined }));
      return;
    }

    const error = getOutboundValidationError(date, time);
    setValidationErrors(prev => ({ ...prev, outbound: error }));
  };

  // Real-time validation for return
  const validateReturnDateTime = (date: string, time: string) => {
    if (!date || !time) {
      setValidationErrors(prev => ({ ...prev, return: undefined }));
      return;
    }

    const error = getReturnValidationError(date, time);
    setValidationErrors(prev => ({ ...prev, return: error }));
  };

  // Get outbound validation error
  const getOutboundValidationError = (date: string, time: string): string | undefined => {
    // Get user's local timezone
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const now = new Date();
    
    // Convert to user's timezone
    const userNow = new Date(now.toLocaleString("en-US", { timeZone: userTimezone }));
    const today = userNow.toISOString().split('T')[0];
    
    if (date < today) {
      return t('dateCannotBeInPast');
    }
    
    if (date === today) {
      // Add 2-hour buffer for today
      const bufferTime = new Date(userNow.getTime() + 2 * 60 * 60 * 1000);
      const minTime = bufferTime.toTimeString().slice(0, 5);
      
      if (time < minTime) {
        return t('timeTooEarlyToday', { minTime });
      }
    }
    
    // Check business hours (configurable from backend)
    const hour = parseInt(time.split(':')[0]);
    const businessStart = route_data?.business_hours_start || 6;
    const businessEnd = route_data?.business_hours_end || 23;
    
    if (hour < businessStart || hour >= businessEnd) {
      return t('timeOutsideBusinessHours', { start: businessStart, end: businessEnd });
    }
    
    return undefined;
  };

  // Get return validation error
  const getReturnValidationError = (date: string, time: string): string | undefined => {
    if (!localOutboundDate || !localOutboundTime) {
      return t('selectOutboundFirst');
    }
    
    // Get user's local timezone
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const now = new Date();
    const userNow = new Date(now.toLocaleString("en-US", { timeZone: userTimezone }));
    const today = userNow.toISOString().split('T')[0];
    
    // CRITICAL: Return date cannot be before outbound date
    if (date < localOutboundDate) {
      return t('returnDateCannotBeBeforeOutbound');
    }
    
    if (date === localOutboundDate) {
      // Same day return: must be at least 2 hours after outbound
      const outboundHour = parseInt(localOutboundTime.split(':')[0]);
      const outboundMinute = parseInt(localOutboundTime.split(':')[1]);
      const returnHour = parseInt(time.split(':')[0]);
      const returnMinute = parseInt(time.split(':')[1]);
      
      const outboundMinutes = outboundHour * 60 + outboundMinute;
      const returnMinutes = returnHour * 60 + returnMinute;
      
      if (returnMinutes - outboundMinutes < 120) { // 2 hours = 120 minutes
        return t('returnTimeTooCloseToOutbound');
      }
    }
    
    // Max return date: 30 days after outbound
    const maxReturnDate = new Date(localOutboundDate);
    maxReturnDate.setDate(maxReturnDate.getDate() + 30);
    const maxReturnDateStr = maxReturnDate.toISOString().split('T')[0];
    
    if (date > maxReturnDateStr) {
      return t('returnDateTooFar');
    }
    
    // Check business hours
    const hour = parseInt(time.split(':')[0]);
    const businessStart = route_data?.business_hours_start || 6;
    const businessEnd = route_data?.business_hours_end || 23;
    
    if (hour < businessStart || hour >= businessEnd) {
      return t('timeOutsideBusinessHours', { start: businessStart, end: businessEnd });
    }
    
    // If return date is today, check 2-hour buffer
    if (date === today) {
      const bufferTime = new Date(userNow.getTime() + 2 * 60 * 60 * 1000);
      const minTime = bufferTime.toTimeString().slice(0, 5);
      
      if (time < minTime) {
        return t('timeTooEarlyToday', { minTime });
      }
    }
    
    return undefined;
  };

  // Handle next step
  const handleNext = () => {
    // Clear previous validation errors
    setValidationErrors({});
    
    // Validate outbound date/time
    if (localOutboundDate && localOutboundTime) {
      const outboundError = getOutboundValidationError(localOutboundDate, localOutboundTime);
      if (outboundError) {
        setValidationErrors(prev => ({ ...prev, outbound: outboundError }));
        return;
      }
    }
    
    // Validate return date/time for round trip
    if (trip_type === 'round_trip') {
      if (!localReturnDate || !localReturnTime) {
        setValidationErrors(prev => ({ ...prev, return: t('returnDateAndTimeRequired') }));
        return;
      }
      
      const returnError = getReturnValidationError(localReturnDate, localReturnTime);
      if (returnError) {
        setValidationErrors(prev => ({ ...prev, return: returnError }));
        return;
      }
    }
    
    // If all validation passes, proceed to next step
    if (isStepValid('datetime')) {
      onNext();
    }
  };

  // Check if form is valid - IMPROVED LOGIC FOR ROUND TRIP
  const isValid = (() => {
    // Check for validation errors
    if (Object.values(validationErrors).some(error => error)) return false;
    
    // Basic validation: outbound date and time must be selected
    if (!localOutboundDate || !localOutboundTime) return false;
    
    // Additional validation for round trip return fields
    if (trip_type === 'round_trip') {
      if (!localReturnDate || !localReturnTime) return false;
      
      // Ensure return date is not before outbound date
      if (localReturnDate < localOutboundDate) return false;
      
      // If same day, ensure return time is at least 2 hours after outbound
      if (localReturnDate === localOutboundDate) {
        const outboundHour = parseInt(localOutboundTime.split(':')[0]);
        const outboundMinute = parseInt(localOutboundTime.split(':')[1]);
        const returnHour = parseInt(localReturnTime.split(':')[0]);
        const returnMinute = parseInt(localReturnTime.split(':')[1]);
        
        const outboundMinutes = outboundHour * 60 + outboundMinute;
        const returnMinutes = returnHour * 60 + returnMinute;
        
        if (returnMinutes - outboundMinutes < 120) return false; // 2 hours = 120 minutes
      }
    }
    
    return true;
  })();

  // Get minimum date (today) - with proper timezone handling
  const getMinDate = () => {
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const now = new Date();
    const userNow = new Date(now.toLocaleString("en-US", { timeZone: userTimezone }));
    const year = userNow.getFullYear();
    const month = String(userNow.getMonth() + 1).padStart(2, '0');
    const day = String(userNow.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // Get minimum date for return (outbound date or today, whichever is later)
  const getMinReturnDate = () => {
    if (localOutboundDate) {
      return localOutboundDate;
    }
    return getMinDate();
  };

  // Get maximum return date (30 days after outbound)
  const getMaxReturnDate = () => {
    if (!localOutboundDate) return '';
    
    const maxDate = new Date(localOutboundDate);
    maxDate.setDate(maxDate.getDate() + 30);
    const year = maxDate.getFullYear();
    const month = String(maxDate.getMonth() + 1).padStart(2, '0');
    const day = String(maxDate.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // Helper: Generate time slots with business hours consideration
  const generateTimeSlots = () => {
    const slots: { value: string; label: string; surcharge?: { label: string; percent: number; color: string } }[] = [];
    
    const businessStart = route_data?.business_hours_start || 6;
    const businessEnd = route_data?.business_hours_end || 23;
    
    for (let h = businessStart; h < businessEnd; h++) {
      for (let m = 0; m < 60; m += 30) {
        const value = `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
        let surcharge = undefined as undefined | { label: string; percent: number; color: string };
        
        const peakPct = Number(route_data?.peak_hour_surcharge ?? 10);
        const midnightPct = Number(route_data?.midnight_surcharge ?? 5);
        
        if ((h >= 7 && h <= 9) || (h >= 17 && h <= 19)) {
          surcharge = { label: t('peakHour'), percent: peakPct, color: 'bg-orange-100 text-orange-700 border-orange-300' };
        } else if ((h >= 22 && h <= 23) || (h >= 0 && h <= 6)) {
          surcharge = { label: t('midnight'), percent: midnightPct, color: 'bg-purple-100 text-purple-700 border-purple-300' };
        }
        
        slots.push({ value, label: value, surcharge });
      }
    }
    return slots;
  };

  // Helper: Is time slot allowed (for today or return logic)
  const isTimeSlotAllowed = (date: string, slot: string, isReturn = false) => {
    if (!date) return false;
    
    // Get user's local timezone
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const now = new Date();
    const userNow = new Date(now.toLocaleString("en-US", { timeZone: userTimezone }));
    const today = userNow.toISOString().split('T')[0];
    
    // Check if date is today
    if (date === today) {
      const bufferTime = new Date(userNow.getTime() + 2 * 60 * 60 * 1000);
      const minTime = bufferTime.toTimeString().slice(0, 5);
      if (slot < minTime) return false;
    }
    
    // For return time validation (must be at least 2h after outbound time when same day)
    if (isReturn && localOutboundDate && date === localOutboundDate && localOutboundTime) {
      const outboundHour = parseInt(localOutboundTime.split(':')[0]);
      const outboundMinute = parseInt(localOutboundTime.split(':')[1]);
      const returnHour = parseInt(slot.split(':')[0]);
      const returnMinute = parseInt(slot.split(':')[1]);
      
      const outboundMinutes = outboundHour * 60 + outboundMinute;
      const returnMinutes = returnHour * 60 + returnMinute;
      
      if (returnMinutes - outboundMinutes < 120) return false;
    }
    
    return true;
  };



  // Helper: Get computed min return date
  const getComputedMinReturnDate = () => {
    return getMinReturnDate();
  };

  // Helper: Get computed max return date
  const getComputedMaxReturnDate = () => {
    return getMaxReturnDate();
  };

  // Render date picker with mobile compatibility
  const renderDatePicker = (value: string, onChange: (date: string) => void, minDate?: string, maxDate?: string) => {

    // Format date for display (Persian/English based on locale)
    const formatDateForDisplay = (dateStr: string) => {
      if (!dateStr) return '';
      try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('fa-IR', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        });
      } catch {
        return dateStr;
      }
    };

    return (
      <div className="relative">
        <input
          type="date"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          min={minDate}
          max={maxDate}
          className="w-full p-3 pl-10 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-gray-100"
          style={{
            // Ensure date picker is visible on all mobile browsers
            WebkitAppearance: 'none',
            MozAppearance: 'textfield',
            appearance: 'none',
            // Force date picker to show on mobile
            position: 'relative',
            zIndex: 1,
            // Additional mobile-specific styles
            fontSize: isMobile ? '16px' : '14px', // Prevent zoom on iOS
            minHeight: '48px', // Ensure touch target is large enough
            touchAction: 'manipulation', // Improve touch responsiveness
          }}
          // Add mobile-specific attributes
          inputMode="none"
          autoComplete="off"
          // Force mobile browsers to show native date picker
          onFocus={(e) => {
            // For iOS Safari and other problematic browsers
            if (isMobile) {
              try {
                const input = e.target as HTMLInputElement;
                (input as HTMLInputElement & { showPicker?: () => void }).showPicker?.();
              } catch {
                console.log('showPicker not supported on focus');
              }
            }
          }}
          // Fallback for browsers that don't support showPicker
          onClick={(e) => {
            if (isMobile) {
              try {
                const input = e.target as HTMLInputElement;
                (input as HTMLInputElement & { showPicker?: () => void }).showPicker?.();
              } catch {
                // Fallback: try to trigger the picker manually
                console.log('Date picker fallback triggered');
                // Force focus and click for stubborn browsers
                setTimeout(() => {
                  const input = e.target as HTMLInputElement;
                  input.focus();
                }, 100);
              }
            }
          }}
        />
        
        {/* Custom date picker button for mobile fallback */}
        {isMobile && (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              const input = e.currentTarget.previousElementSibling as HTMLInputElement;
              if (input && input.type === 'date') {
                try {
                  input.showPicker?.();
                } catch {
                  // Multiple fallback strategies
                  input.focus();
                  input.click();
                  
                  // Try dispatching events
                  const clickEvent = new MouseEvent('click', { bubbles: true });
                  input.dispatchEvent(clickEvent);
                  
                  // Last resort: try to open with touch events
                  const touchStart = new TouchEvent('touchstart', { bubbles: true });
                  const touchEnd = new TouchEvent('touchend', { bubbles: true });
                  input.dispatchEvent(touchStart);
                  input.dispatchEvent(touchEnd);
                }
              }
            }}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
            aria-label="Open date picker"
          />
        )}
        
        {/* Display formatted date for better UX */}
        {value && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-gray-500 dark:text-gray-400 pointer-events-none">
            {formatDateForDisplay(value)}
          </div>
        )}
        
        {/* Alternative date picker for very problematic browsers */}
        {useFallbackDatePicker && (
          <div className="absolute inset-0 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg flex items-center justify-between px-3 cursor-pointer"
            onClick={() => {
              // This will be replaced with a proper date picker modal if needed
              const newDate = prompt(t('datePickerPrompt'), value);
              if (newDate && /^\d{4}-\d{2}-\d{2}$/.test(newDate)) {
                onChange(newDate);
              }
            }}
          >
            <span className="text-gray-900 dark:text-gray-100">
              {value ? formatDateForDisplay(value) : t('selectDatePlaceholder')}
            </span>
            <Calendar className="w-4 h-4 text-gray-400" />
          </div>
        )}
      </div>
    );
  };

  // Render time dropdown
  const renderTimeDropdown = (date: string, value: string, onChange: (time: string) => void, isReturn = false) => {
    const timeSlots = generateTimeSlots().filter(slot => isTimeSlotAllowed(date, slot.value, isReturn));
    
    const options = timeSlots.map(slot => ({
      value: slot.value,
      label: (
        <div className="flex items-center justify-between">
          <span>{slot.label}</span>
          {slot.surcharge && (
            <span className={`text-xs px-2 py-1 rounded ${slot.surcharge.color}`}>
              +{slot.surcharge.percent}%
            </span>
          )}
        </div>
      )
    }));
    
    const selectedOption = options.find(opt => opt.value === value);
    
    return (
      <Select
        value={selectedOption}
        onChange={(option) => onChange(option?.value || '')}
        options={options}
        placeholder={t('selectTime')}
        className="w-full"
        classNamePrefix="react-select"
        isClearable={false}
        styles={{
          control: (base, state) => ({
            ...base,
            minHeight: '48px',
            borderColor: state.isFocused ? '#3b82f6' : '#d1d5db',
            boxShadow: state.isFocused ? '0 0 0 1px #3b82f6' : 'none',
            backgroundColor: 'white',
            '@media (prefers-color-scheme: dark)': {
              backgroundColor: '#374151',
              borderColor: state.isFocused ? '#3b82f6' : '#6b7280'
            }
          }),
          option: (base, state) => ({ 
            ...base, 
            fontSize: '1rem', 
            padding: '0.5rem 1rem',
            backgroundColor: state.isSelected ? '#3b82f6' : state.isFocused ? '#f3f4f6' : 'transparent',
            color: state.isSelected ? 'white' : '#374151',
            '@media (prefers-color-scheme: dark)': {
              backgroundColor: state.isSelected ? '#3b82f6' : state.isFocused ? '#4b5563' : '#374151',
              color: state.isSelected ? 'white' : state.isFocused ? '#f9fafb' : '#d1d5db'
            }
          }),
          menu: (base) => ({
            ...base,
            backgroundColor: 'white',
            '@media (prefers-color-scheme: dark)': {
              backgroundColor: '#374151'
            }
          }),
          menuList: (base) => ({
            ...base,
            '@media (prefers-color-scheme: dark)': {
              backgroundColor: '#374151'
            }
          }),
          singleValue: (base) => ({
            ...base,
            color: '#374151',
            '@media (prefers-color-scheme: dark)': {
              color: '#f9fafb'
            }
          }),
          placeholder: (base) => ({
            ...base,
            color: '#9ca3af',
            '@media (prefers-color-scheme: dark)': {
              color: '#9ca3af'
            }
          }),
          input: (base) => ({
            ...base,
            color: '#374151',
            '@media (prefers-color-scheme: dark)': {
              color: '#f9fafb'
            }
          }),
          indicatorSeparator: (base) => ({
            ...base,
            backgroundColor: '#d1d5db',
            '@media (prefers-color-scheme: dark)': {
              backgroundColor: '#6b7280'
            }
          }),
          dropdownIndicator: (base) => ({
            ...base,
            color: '#6b7280',
            '@media (prefers-color-scheme: dark)': {
              color: '#9ca3af'
            }
          }),
          clearIndicator: (base) => ({
            ...base,
            color: '#6b7280',
            '@media (prefers-color-scheme: dark)': {
              color: '#9ca3af'
            }
          }),
        }}
        isSearchable={false}
      />
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          {t('selectDateAndTime')}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {t('step3')}
        </p>
      </div>

      {/* Trip Type Selection */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('tripType')}
        </h3>
        
        {/* Surcharge Information */}
        {route_data && (
          <div className="mb-4 p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg">
            <div className="flex items-center gap-2 text-sm text-orange-800 dark:text-orange-200">
              <Clock className="w-4 h-4" />
              <span className="font-medium">{t('timeSurcharge')}:</span>
            </div>
            <div className="mt-2 space-y-1 text-xs text-orange-700 dark:text-orange-300">
              {parseFloat(route_data.peak_hour_surcharge || '0') > 0 && (
                <div>• {t('peakHourSurcharge')}: {route_data.peak_hour_surcharge}% (7:00-9:00 & 17:00-19:00)</div>
              )}
              {parseFloat(route_data.midnight_surcharge || '0') > 0 && (
                <div>• {t('midnightSurcharge')}: {route_data.midnight_surcharge}% (22:00-6:00)</div>
              )}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            onClick={() => handleTripTypeChange('one_way')}
            className={`
              p-4 border rounded-lg cursor-pointer transition-all
              ${trip_type === 'one_way'
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-700'
              }
            `}
          >
            <div className="flex items-center gap-3">
              {/* <Plane className="w-6 h-6 text-blue-600 dark:text-blue-400" /> */}
              <div>
                <h4 className="font-medium text-gray-900 dark:text-gray-100">{t('oneWay')}</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">{t('oneWayDescription')}</p>
              </div>
            </div>
          </div>

          <div
            onClick={() => handleTripTypeChange('round_trip')}
            className={`
              p-4 border rounded-lg cursor-pointer transition-all
              ${trip_type === 'round_trip'
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-700'
              }
            `}
          >
            <div className="flex items-center gap-3">
              {/* <PlaneTakeoff className="w-6 h-6 text-blue-600 dark:text-blue-400" /> */}
              <div>
                <h4 className="font-medium text-gray-900 dark:text-gray-100">{t('roundTrip')}</h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">{t('roundTripDescription')}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Outbound Date & Time */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {t('outboundDate')} & {t('outboundTime')}
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('date')}
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              {renderDatePicker(localOutboundDate, (date) => handleOutboundChange(date, localOutboundTime), getMinDate(), getComputedMaxReturnDate())}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {t('time')}
            </label>
            <div className="relative">
              <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              {renderTimeDropdown(localOutboundDate, localOutboundTime, (time) => handleOutboundChange(localOutboundDate, time))}
            </div>
            {localOutboundDate && localOutboundTime && validationErrors.outbound && (
              <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                <AlertCircle className="w-4 h-4 mr-1 inline-block" /> {validationErrors.outbound}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Return Date & Time (for round trip) */}
      {trip_type === 'round_trip' && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
            {t('returnDate')} & {t('returnTime')}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('date')}
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                {renderDatePicker(
                  localReturnDate,
                  (date) => handleReturnChange(date, localReturnTime),
                  getComputedMinReturnDate(),
                  getComputedMaxReturnDate()
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                {t('time')}
              </label>
              <div className="relative">
                <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                {renderTimeDropdown(localReturnDate, localReturnTime, (time) => handleReturnChange(localReturnDate, time), true)}
              </div>
              {localReturnDate && localReturnTime && validationErrors.return && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  <AlertCircle className="w-4 h-4 mr-1 inline-block" /> {validationErrors.return}
                </p>
              )}
            </div>
          </div>
          
          {/* Show error if return fields are empty for round trip */}
          {trip_type === 'round_trip' && (!localReturnDate || !localReturnTime) && (
            <p className="mt-2 text-sm text-red-600 dark:text-red-400">
              <AlertCircle className="w-4 h-4 mr-1 inline-block" /> {t('returnDateAndTimeRequired')}
            </p>
          )}
        </div>
      )}

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
            onClick={handleNext}
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