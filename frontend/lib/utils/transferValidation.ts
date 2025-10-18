/**
 * Transfer-specific validation utilities
 * Handles round-trip discounts, surcharges, and other transfer-specific validations
 */

export interface TransferValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
  warnings: Record<string, string>;
}

export interface TransferBookingData {
  route_id: number;
  vehicle_type: string;
  passenger_count: number;
  luggage_count: number;
  trip_type: 'one_way' | 'round_trip';
  booking_date: string;
  booking_time: string;
  return_date?: string;
  return_time?: string;
  selected_options?: Array<{
    option_id: string;
    quantity: number;
    name?: string;
    price?: number;
  }>;
}

export interface VehicleCapacity {
  max_passengers: number;
  max_luggage: number;
  vehicle_type: string;
}

export interface RouteConstraints {
  min_advance_booking_hours: number;
  max_advance_booking_days: number;
  allowed_vehicle_types: string[];
  peak_hours: Array<{ start: string; end: string }>;
  night_hours: Array<{ start: string; end: string }>;
}

/**
 * Validate transfer booking data with transfer-specific rules
 */
export function validateTransferBooking(
  bookingData: TransferBookingData,
  vehicleCapacity: VehicleCapacity,
  routeConstraints: RouteConstraints
): TransferValidationResult {
  const errors: Record<string, string> = {};
  const warnings: Record<string, string> = {};

  // Basic validations
  if (!bookingData.route_id) {
    errors.route_id = 'Route selection is required';
  }

  if (!bookingData.vehicle_type) {
    errors.vehicle_type = 'Vehicle type selection is required';
  }

  if (!bookingData.booking_date) {
    errors.booking_date = 'Booking date is required';
  }

  if (!bookingData.booking_time) {
    errors.booking_time = 'Booking time is required';
  }

  // Date validations
  if (bookingData.booking_date) {
    const bookingDate = new Date(bookingData.booking_date);
    const now = new Date();
    
    // Check if date is in the past
    if (bookingDate < now) {
      errors.booking_date = 'Booking date cannot be in the past';
    }

    // Check minimum advance booking time
    const minAdvanceTime = new Date(now.getTime() + (routeConstraints.min_advance_booking_hours * 60 * 60 * 1000));
    if (bookingDate < minAdvanceTime) {
      errors.booking_date = `Booking must be at least ${routeConstraints.min_advance_booking_hours} hours in advance`;
    }

    // Check maximum advance booking time
    const maxAdvanceTime = new Date(now.getTime() + (routeConstraints.max_advance_booking_days * 24 * 60 * 60 * 1000));
    if (bookingDate > maxAdvanceTime) {
      errors.booking_date = `Booking cannot be more than ${routeConstraints.max_advance_booking_days} days in advance`;
    }
  }

  // Time validations
  if (bookingData.booking_time) {
    const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
    if (!timeRegex.test(bookingData.booking_time)) {
      errors.booking_time = 'Invalid time format (HH:MM)';
    }
  }

  // Round trip validations
  if (bookingData.trip_type === 'round_trip') {
    if (!bookingData.return_date) {
      errors.return_date = 'Return date is required for round trip';
    }

    if (!bookingData.return_time) {
      errors.return_time = 'Return time is required for round trip';
    }

    if (bookingData.return_date && bookingData.booking_date) {
      const outboundDate = new Date(bookingData.booking_date);
      const returnDate = new Date(bookingData.return_date);
      
      if (returnDate <= outboundDate) {
        errors.return_date = 'Return date must be after outbound date';
      }

      // Check if return date is too far in the future
      const maxReturnTime = new Date(outboundDate.getTime() + (30 * 24 * 60 * 60 * 1000)); // 30 days max
      if (returnDate > maxReturnTime) {
        errors.return_date = 'Return date cannot be more than 30 days after outbound date';
      }
    }

    if (bookingData.return_time) {
      const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
      if (!timeRegex.test(bookingData.return_time)) {
        errors.return_time = 'Invalid return time format (HH:MM)';
      }
    }
  }

  // Passenger validations
  if (bookingData.passenger_count < 1) {
    errors.passenger_count = 'At least 1 passenger is required';
  } else if (bookingData.passenger_count > vehicleCapacity.max_passengers) {
    errors.passenger_count = `Maximum ${vehicleCapacity.max_passengers} passengers allowed for ${vehicleCapacity.vehicle_type}`;
  }

  // Luggage validations
  if (bookingData.luggage_count < 0) {
    errors.luggage_count = 'Luggage count cannot be negative';
  } else if (bookingData.luggage_count > vehicleCapacity.max_luggage) {
    errors.luggage_count = `Maximum ${vehicleCapacity.max_luggage} pieces of luggage allowed for ${vehicleCapacity.vehicle_type}`;
  }

  // Vehicle type validations
  if (bookingData.vehicle_type && !routeConstraints.allowed_vehicle_types.includes(bookingData.vehicle_type)) {
    errors.vehicle_type = `Vehicle type ${bookingData.vehicle_type} is not allowed on this route`;
  }

  // Peak hour warnings
  if (bookingData.booking_time) {
    const bookingHour = parseInt(bookingData.booking_time.split(':')[0]);
    const isPeakHour = routeConstraints.peak_hours.some(peak => {
      const startHour = parseInt(peak.start.split(':')[0]);
      const endHour = parseInt(peak.end.split(':')[0]);
      return bookingHour >= startHour && bookingHour <= endHour;
    });

    if (isPeakHour) {
      warnings.booking_time = 'Peak hour booking - surcharge may apply';
    }
  }

  // Night hour warnings
  if (bookingData.booking_time) {
    const bookingHour = parseInt(bookingData.booking_time.split(':')[0]);
    const isNightHour = routeConstraints.night_hours.some(night => {
      const startHour = parseInt(night.start.split(':')[0]);
      const endHour = parseInt(night.end.split(':')[0]);
      
      // Handle overnight hours (e.g., 22:00-06:00)
      if (startHour > endHour) {
        return bookingHour >= startHour || bookingHour <= endHour;
      } else {
        return bookingHour >= startHour && bookingHour <= endHour;
      }
    });

    if (isNightHour) {
      warnings.booking_time = 'Night hour booking - surcharge will apply';
    }
  }

  // Round trip discount validation
  if (bookingData.trip_type === 'round_trip') {
    if (bookingData.return_date && bookingData.booking_date) {
      const outboundDate = new Date(bookingData.booking_date);
      const returnDate = new Date(bookingData.return_date);
      const daysDifference = Math.ceil((returnDate.getTime() - outboundDate.getTime()) / (1000 * 60 * 60 * 24));
      
      if (daysDifference > 7) {
        warnings.return_date = 'Round trip discount may not apply for trips longer than 7 days';
      }
    }
  }

  // Option validations
  if (bookingData.selected_options) {
    for (const option of bookingData.selected_options) {
      if (option.quantity < 1) {
        errors[`option_${option.option_id}`] = `Invalid quantity for ${option.name || 'option'}`;
      }
      
      if (option.quantity > 10) {
        warnings[`option_${option.option_id}`] = `High quantity for ${option.name || 'option'} - please verify`;
      }
    }
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    warnings
  };
}

/**
 * Validate capacity for transfer booking
 */
export function validateTransferCapacity(
  passengerCount: number,
  luggageCount: number,
  vehicleCapacity: VehicleCapacity
): TransferValidationResult {
  const errors: Record<string, string> = {};
  const warnings: Record<string, string> = {};

  if (passengerCount > vehicleCapacity.max_passengers) {
    errors.passenger_count = `Exceeds maximum capacity of ${vehicleCapacity.max_passengers} passengers`;
  }

  if (luggageCount > vehicleCapacity.max_luggage) {
    errors.luggage_count = `Exceeds maximum luggage capacity of ${vehicleCapacity.max_luggage} pieces`;
  }

  // Warning for high utilization
  const passengerUtilization = (passengerCount / vehicleCapacity.max_passengers) * 100;
  const luggageUtilization = (luggageCount / vehicleCapacity.max_luggage) * 100;

  if (passengerUtilization > 80) {
    warnings.passenger_count = 'High passenger utilization - consider larger vehicle';
  }

  if (luggageUtilization > 80) {
    warnings.luggage_count = 'High luggage utilization - consider additional space';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    warnings
  };
}

/**
 * Validate time-based surcharges
 */
export function validateTimeSurcharges(
  bookingTime: string,
  returnTime?: string,
  routeConstraints?: RouteConstraints
): {
  hasPeakSurcharge: boolean;
  hasNightSurcharge: boolean;
  peakSurchargeAmount?: number;
  nightSurchargeAmount?: number;
  warnings: string[];
} {
  const warnings: string[] = [];
  let hasPeakSurcharge = false;
  let hasNightSurcharge = false;
  let peakSurchargeAmount = 0;
  let nightSurchargeAmount = 0;

  if (!routeConstraints) {
    return { hasPeakSurcharge, hasNightSurcharge, warnings };
  }

  const bookingHour = parseInt(bookingTime.split(':')[0]);

  // Check peak hours
  const isPeakHour = routeConstraints.peak_hours.some(peak => {
    const startHour = parseInt(peak.start.split(':')[0]);
    const endHour = parseInt(peak.end.split(':')[0]);
    return bookingHour >= startHour && bookingHour <= endHour;
  });

  if (isPeakHour) {
    hasPeakSurcharge = true;
    peakSurchargeAmount = 0.2; // 20% surcharge
    warnings.push('Peak hour surcharge applies');
  }

  // Check night hours
  const isNightHour = routeConstraints.night_hours.some(night => {
    const startHour = parseInt(night.start.split(':')[0]);
    const endHour = parseInt(night.end.split(':')[0]);
    
    // Handle overnight hours (e.g., 22:00-06:00)
    if (startHour > endHour) {
      return bookingHour >= startHour || bookingHour <= endHour;
    } else {
      return bookingHour >= startHour && bookingHour <= endHour;
    }
  });

  if (isNightHour) {
    hasNightSurcharge = true;
    nightSurchargeAmount = 0.25; // 25% surcharge
    warnings.push('Night hour surcharge applies');
  }

  // Check return time for round trips
  if (returnTime) {
    const returnHour = parseInt(returnTime.split(':')[0]);
    
    const isReturnPeakHour = routeConstraints.peak_hours.some(peak => {
      const startHour = parseInt(peak.start.split(':')[0]);
      const endHour = parseInt(peak.end.split(':')[0]);
      return returnHour >= startHour && returnHour <= endHour;
    });

    if (isReturnPeakHour) {
      warnings.push('Return trip peak hour surcharge applies');
    }

    const isReturnNightHour = routeConstraints.night_hours.some(night => {
      const startHour = parseInt(night.start.split(':')[0]);
      const endHour = parseInt(night.end.split(':')[0]);
      
      if (startHour > endHour) {
        return returnHour >= startHour || returnHour <= endHour;
      } else {
        return returnHour >= startHour && returnHour <= endHour;
      }
    });

    if (isReturnNightHour) {
      warnings.push('Return trip night hour surcharge applies');
    }
  }

  return {
    hasPeakSurcharge,
    hasNightSurcharge,
    peakSurchargeAmount,
    nightSurchargeAmount,
    warnings
  };
}

/**
 * Validate round trip discount eligibility
 */
export function validateRoundTripDiscount(
  outboundDate: string,
  returnDate: string,
  outboundTime?: string,
  returnTime?: string
): {
  isEligible: boolean;
  discountPercentage: number;
  warnings: string[];
} {
  const warnings: string[] = [];
  let isEligible = true;
  let discountPercentage = 0.2; // Default 20% discount

  const outbound = new Date(outboundDate);
  const returnDateObj = new Date(returnDate);
  const daysDifference = Math.ceil((returnDateObj.getTime() - outbound.getTime()) / (1000 * 60 * 60 * 24));

  // Check if return is within 7 days for full discount
  if (daysDifference > 7) {
    isEligible = false;
    warnings.push('Round trip discount not available for trips longer than 7 days');
  }

  // Check if return is within 3 days for maximum discount
  if (daysDifference > 3) {
    discountPercentage = 0.15; // Reduced discount
    warnings.push('Reduced round trip discount for trips longer than 3 days');
  }

  // Check if return is same day (minimum discount)
  if (daysDifference === 0) {
    discountPercentage = 0.1; // Minimum discount
    warnings.push('Minimum round trip discount for same-day return');
  }

  // Check time constraints for same-day returns
  if (daysDifference === 0 && outboundTime && returnTime) {
    const outboundHour = parseInt(outboundTime.split(':')[0]);
    const returnHour = parseInt(returnTime.split(':')[0]);
    const hoursDifference = returnHour - outboundHour;

    if (hoursDifference < 4) {
      isEligible = false;
      warnings.push('Round trip discount not available for same-day returns with less than 4 hours between trips');
    }
  }

  return {
    isEligible,
    discountPercentage,
    warnings
  };
}

/**
 * Get default route constraints
 */
export function getDefaultRouteConstraints(): RouteConstraints {
  return {
    min_advance_booking_hours: 2,
    max_advance_booking_days: 30,
    allowed_vehicle_types: ['sedan', 'suv', 'van', 'sprinter', 'bus', 'limousine'],
    peak_hours: [
      { start: '07:00', end: '09:00' },
      { start: '17:00', end: '19:00' }
    ],
    night_hours: [
      { start: '22:00', end: '06:00' }
    ]
  };
}

/**
 * Get default vehicle capacities
 */
export function getDefaultVehicleCapacities(): Record<string, VehicleCapacity> {
  return {
    sedan: {
      max_passengers: 4,
      max_luggage: 4,
      vehicle_type: 'sedan'
    },
    suv: {
      max_passengers: 6,
      max_luggage: 6,
      vehicle_type: 'suv'
    },
    van: {
      max_passengers: 8,
      max_luggage: 8,
      vehicle_type: 'van'
    },
    sprinter: {
      max_passengers: 12,
      max_luggage: 12,
      vehicle_type: 'sprinter'
    },
    bus: {
      max_passengers: 20,
      max_luggage: 20,
      vehicle_type: 'bus'
    },
    limousine: {
      max_passengers: 8,
      max_luggage: 8,
      vehicle_type: 'limousine'
    }
  };
}
