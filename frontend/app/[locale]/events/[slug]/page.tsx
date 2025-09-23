'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  Clock, 
  MapPin, 
  Users, 
  Star, 
  Info,
  Shield,
  Plus,
  Minus,
  AlertTriangle,
  CheckCircle,
  Sparkles
} from 'lucide-react';
import { getEventBySlug, calculateEventPricing, getPerformanceSeats, holdSeats, releaseSeats } from '@/lib/api/events';
import { addEventSeatsToCart } from '@/lib/api/cart';

import { Event, EventPricingBreakdown, EventPerformance, TicketType, ApiSection, ApiSectionTicketType, ApiSeat, PerformanceSeatsResponse } from '@/lib/types/api';
import PerformanceSelector from '@/components/events/PerformanceSelector';
import SeatMap from '@/components/events/SeatMap';
import PricingBreakdown from '@/components/events/PricingBreakdown';
import ProductCancellationPolicy from '@/components/common/ProductCancellationPolicy';
import { useCart } from '@/app/lib/hooks/useCart';
import { useToast } from '@/components/Toast';
import OptimizedImage from '@/components/common/OptimizedImage';

interface Seat {
  id: string;
  seat_number: string;
  row_number: string;
  section: string;
  price: number;
  currency: string;
  is_wheelchair_accessible: boolean;
  is_premium: boolean;
  status: 'available' | 'selected' | 'reserved' | 'sold' | 'blocked';
  ticket_type?: string | { id: string; name: string };
}

interface BookingStep {
  id: number;
  title: string;
  description: string;
  isComplete: boolean;
  isActive: boolean;
}

export default function EventDetailPage() {
  const params = useParams();
  const slug = params.slug as string;
  const locale = (params as { locale: string }).locale as string;
  const { refreshCart } = useCart();
  const { addToast } = useToast();
  const t = useTranslations('eventDetail');
  const tCommon = useTranslations('common');
  const tEventDetail = useTranslations('eventDetail');
  const router = useRouter();
  
  // Format price with currency
  const formatPrice = (price: number, currency?: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price);
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };
  
  const [event, setEvent] = useState<Event | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isBooking, setIsBooking] = useState(false);

  
  // Booking state
  const [selectedPerformance, setSelectedPerformance] = useState<EventPerformance | null>(null);
  const [selectedSections, setSelectedSections] = useState<Array<{
    id: string;
    name: string;
    description: string;
    total_capacity: number;
    available_capacity: number;
    reserved_capacity: number;
    sold_capacity: number;
    base_price: number;
    currency: string;
    is_wheelchair_accessible: boolean;
    is_premium: boolean;
    occupancy_rate: number;
    is_full: boolean;
    ticket_types: Array<{
      id: string;
      section: { id: string; name: string };
      ticket_type: { 
        id: string; 
        name: string; 
        description: string; 
        price_modifier: number;
        capacity: number;
        is_active: boolean;
        ticket_type: string; 
        benefits: string[];
        created_at: string;
        updated_at: string;
      };
      allocated_capacity: number;
      available_capacity: number;
      reserved_capacity: number;
      sold_capacity: number;
      price_modifier: number;
      final_price: number;
      created_at: string;
      updated_at: string;
    }>;
    created_at: string;
    updated_at: string;
  }>>([]);
  // Keep selectedSection for backward compatibility (current active section)
  const [selectedSection, setSelectedSection] = useState<typeof selectedSections[0] | null>(null);
  const [selectedTicketType, setSelectedTicketType] = useState<TicketType | null>(null);
  const [selectedSeats, setSelectedSeats] = useState<Seat[]>([]);
  const [availableSeats, setAvailableSeats] = useState<Seat[]>([]);
  const [quantity, setQuantity] = useState(1); // For manual quantity selection when no specific seats
  const [loadedSections, setLoadedSections] = useState<Array<{
    id: string;
    name: string;
    description: string;
    total_capacity: number;
    available_capacity: number;
    reserved_capacity: number;
    sold_capacity: number;
    base_price: number;
    currency: string;
    is_wheelchair_accessible: boolean;
    is_premium: boolean;
    occupancy_rate: number;
    is_full: boolean;
    ticket_types: Array<{
      id: string;
      section: { id: string; name: string };
      ticket_type: { 
        id: string; 
        name: string; 
        description: string; 
        price_modifier: number;
        capacity: number;
        is_active: boolean;
        ticket_type: string; 
        benefits: string[];
        created_at: string;
        updated_at: string;
      };
      allocated_capacity: number;
      available_capacity: number;
      reserved_capacity: number;
      sold_capacity: number;
      price_modifier: number;
      final_price: number;
      created_at: string;
      updated_at: string;
    }>;
    created_at: string;
    updated_at: string;
  }>>([]);
  const [selectedOptions, setSelectedOptions] = useState<Array<{ id: string; name: string; max_quantity?: number; quantity: number; price: number; currency: string }>>([]);
  const [pricingBreakdown, setPricingBreakdown] = useState<EventPricingBreakdown | null>(null);
  const [discountCode, setDiscountCode] = useState('');
  const [showPricingDetails, setShowPricingDetails] = useState(false);

  
  // Toast state for better error handling
  // const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  // Toast helper function - now using useToast hook
  const showToast = useCallback((message: string, type: 'success' | 'error' | 'info') => {
    addToast({
      title: type === 'error' ? tEventDetail('toastError') : type === 'success' ? tEventDetail('toastSuccess') : tEventDetail('toastInfo'),
      message: message,
      type: type
    });
  }, [addToast, tEventDetail]);

  // Booking steps
  const [bookingSteps, setBookingSteps] = useState<BookingStep[]>([
    {
      id: 1,
      title: t('selectPerformance'),
      description: t('chooseDateTime'),
      isComplete: false,
      isActive: true
    },
    {
      id: 2,
      title: t('selectSeats'),
      description: t('chooseSectionAndSeats'),
      isComplete: false,
      isActive: false
    },
    {
      id: 3,
      title: t('addOptions'),
      description: t('selectAdditionalOptions'),
      isComplete: false,
      isActive: false
    },
    {
      id: 4,
      title: t('review'),
      description: t('reviewAndConfirm'),
      isComplete: false,
      isActive: false
    }
  ]);
  
  // Fetch event data
  useEffect(() => {
    const fetchEvent = async () => {
      try {
        setIsLoading(true);
        const response = await getEventBySlug(slug as string);
        setEvent(response);
        setError(null);
      } catch (err: unknown) {
        console.error('Failed to load event:', err);
        
        // Improved error handling with user-friendly messages
        let errorMessage = t('failedToLoadEvent');
        
        if (err && typeof err === 'object' && 'response' in err && err.response && typeof err.response === 'object' && 'status' in err.response) {
          const status = (err.response as { status: number }).status;
          if (status === 404) {
            errorMessage = t('eventNotFound') || 'Event not found';
          } else if (status >= 500) {
            errorMessage = t('serverError') || 'Server error. Please try again later.';
          }
        } else if (err && typeof err === 'object' && 'code' in err && err.code === 'ECONNABORTED') {
          errorMessage = t('timeoutError') || 'Request timeout. Please try again.';
        } else if (err && typeof err === 'object' && 'message' in err && typeof err.message === 'string') {
          errorMessage = err.message;
        }
        
        setError(errorMessage);
        
        // Show toast notification for better user experience
        showToast(errorMessage, 'error');
      } finally {
        setIsLoading(false);
      }
    };

    if (slug) {
      fetchEvent();
    }
  }, [slug, t, showToast]);

  // Update booking steps based on selections
  useEffect(() => {
    setBookingSteps(prev => prev.map(step => ({
      ...step,
      isComplete: step.id === 1 ? !!selectedPerformance : 
                  step.id === 2 ? !!selectedSection && selectedSeats.length > 0 :
                  step.id === 3 ? true : // Options are optional
                  step.id === 4 ? !!pricingBreakdown : false,
      isActive: step.id === 1 ? true :
                step.id === 2 ? !!selectedPerformance :
                step.id === 3 ? !!selectedSection && selectedSeats.length > 0 :
                step.id === 4 ? !!selectedSection && selectedSeats.length > 0 : false
    })));
  }, [selectedPerformance, selectedSection, selectedSeats, pricingBreakdown]);

  // Reset quantity when section or ticket type changes
  useEffect(() => {
    if (selectedSection && selectedTicketType) {
      const sectionTicketType = selectedSection.ticket_types?.find(
        (tt) => tt.ticket_type.id === selectedTicketType.id
      );
      if (sectionTicketType) {
        const availableCapacity = sectionTicketType.available_capacity || 0;
        if (quantity > availableCapacity) {
          setQuantity(Math.min(quantity, availableCapacity));
          showToast(tEventDetail('quantityReduced', { capacity: availableCapacity }), 'info');
        }
        // Also reset to 1 if no seats are available
        if (availableCapacity === 0) {
          setQuantity(1);
        }
      }
    }
  }, [selectedSection, selectedTicketType, quantity, showToast, tEventDetail]);

  // Format functions
  const formatTime = (timeString: string) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Handle performance selection
  const handlePerformanceSelect = async (performance: EventPerformance) => {
    // Release any held seats when changing performance
    if (selectedPerformance && selectedSeats.length > 0) {
      try {
        await releaseSeats(String(selectedPerformance.id), { seat_ids: selectedSeats.map(s => String(s.id)) });
        showToast(tEventDetail('previousSeatsReleased'), 'info');
      } catch (e: unknown) {
        console.error('Failed to release seats on performance change', e);
        
        // Show user-friendly error message
        let errorMessage = tEventDetail('errorReleasingPreviousSeats');
        
        if (e && typeof e === 'object' && 'response' in e && e.response && typeof e.response === 'object' && 'status' in e.response) {
          const status = (e.response as { status: number }).status;
          if (status === 404) {
            errorMessage = tEventDetail('previousPerformanceNotFound');
          } else if (status >= 500) {
            errorMessage = tEventDetail('serverErrorTryAgain');
          }
        }
        
        if (e && typeof e === 'object' && 'message' in e && typeof e.message === 'string') {
          errorMessage = e.message;
        }
        
        showToast(errorMessage, 'error');
      }
    }
    setSelectedPerformance(performance);
    setSelectedSection(null);
    setSelectedSections([]); // Clear all selected sections
    setSelectedSeats([]);
    showToast(tEventDetail('newPerformanceSelected'), 'success');
  };

  // Handle section selection
  const handleSectionSelect = async (section: {
    id: string;
    name: string;
    description: string;
    total_capacity: number;
    available_capacity: number;
    reserved_capacity: number;
    sold_capacity: number;
    base_price: number;
    currency: string;
    is_wheelchair_accessible: boolean;
    is_premium: boolean;
    occupancy_rate: number;
    is_full: boolean;
    ticket_types: Array<{
      id: string;
      section: { id: string; name: string };
      ticket_type: { 
        id: string; 
        name: string; 
        description: string; 
        price_modifier: number;
        capacity: number;
        is_active: boolean;
        ticket_type: string; 
        benefits: string[];
        created_at: string;
        updated_at: string;
      };
      allocated_capacity: number;
      available_capacity: number;
      reserved_capacity: number;
      sold_capacity: number;
      price_modifier: number;
      final_price: number;
      created_at: string;
      updated_at: string;
    }>;
    created_at: string;
    updated_at: string;
  }) => {
    // Don't release seats when changing section - allow multiple section selections
    // Only release seats when changing performance
    
    // Add section to selectedSections array if not already selected
    setSelectedSections(prev => {
      const exists = prev.find(s => s.id === section.id);
      if (!exists) {
        return [...prev, section];
      }
      return prev;
    });
    
    // Set as current active section
    setSelectedSection(section);
    
    // Reset quantity to 1 when changing section
    setQuantity(1);
    
    if (section.ticket_types && section.ticket_types.length > 0) {
      // Use the first available ticket type from the transformed data
      const firstTicketType = section.ticket_types[0];
      
      // FIXED: Use ticket_type.id instead of firstTicketType.id
      const ticketType: TicketType = {
        id: firstTicketType.ticket_type.id, // Use the actual TicketType.id from transformed data
        name: firstTicketType.ticket_type.name || 'Standard Ticket',
        description: firstTicketType.ticket_type.description || 'Standard event ticket',
        price_modifier: firstTicketType.ticket_type.price_modifier || 1,
        capacity: firstTicketType.ticket_type.capacity || 0,
        is_active: firstTicketType.ticket_type.is_active || true,
        ticket_type: firstTicketType.ticket_type.ticket_type || 'standard',
        benefits: firstTicketType.ticket_type.benefits || [],
        created_at: firstTicketType.ticket_type.created_at || new Date().toISOString(),
        updated_at: firstTicketType.ticket_type.updated_at || new Date().toISOString()
      };
      
      setSelectedTicketType(ticketType);
      console.log('Selected section:', section);
      console.log('Selected ticket type:', ticketType);
      showToast(tEventDetail('sectionSelected', { sectionName: section.name, ticketName: ticketType.name }), 'success');
    } else {
      // If no valid ticket type found, don't set any ticket type
      setSelectedTicketType(null);
      showToast(tEventDetail('sectionSelectedNoTicket', { sectionName: section.name }), 'info');
    }
  };

    // Fetch sections/seat map when performance changes
  useEffect(() => {
    const fetchSeats = async () => {
      if (!selectedPerformance) {
        setAvailableSeats([]);
        setLoadedSections([]);
        return;
      }
      try {
        const resp: PerformanceSeatsResponse = await getPerformanceSeats(event!.id, selectedPerformance.id, { include_seats: 1 });
        const apiSections: ApiSection[] = Array.isArray(resp.sections) ? resp.sections : [];
        
        // Transform ApiSection to EventSectionData for SeatMap component
        const transformedSections = apiSections.map((sec: ApiSection) => ({
          id: sec.id || `section_${sec.name}_${Math.random().toString(36).substr(2, 9)}`,
          name: sec.name,
          description: sec.description || '',
          total_capacity: Number(sec.total_capacity ?? 0),
          available_capacity: Number(sec.available_capacity ?? 0),
          reserved_capacity: Number(sec.reserved_capacity ?? 0),
          sold_capacity: Number(sec.sold_capacity ?? 0),
          base_price: Number(sec.base_price ?? 0),
          currency: sec.currency || 'USD',
          is_wheelchair_accessible: Boolean(sec.is_wheelchair_accessible),
          is_premium: Boolean(sec.is_premium),
          occupancy_rate: Number(sec.occupancy_rate ?? 0),
          is_full: Boolean(sec.available_capacity === 0),
          ticket_types: (sec.ticket_types || [])
            .filter((tt: ApiSectionTicketType) => tt.id && tt.ticket_type && tt.ticket_type.id) // Filter out invalid ticket types
            .map((tt: ApiSectionTicketType) => ({
              id: tt.id, // Keep SectionTicketType.id for internal reference
              section: { id: sec.id || sec.name, name: sec.name },
              ticket_type: { 
                id: tt.ticket_type.id, // Use the nested ticket_type.id
                name: tt.ticket_type.name || 'Standard Ticket', 
                description: tt.ticket_type.description || 'Standard event ticket', 
                price_modifier: tt.price_modifier || 1,
                capacity: tt.allocated_capacity || 0,
                is_active: true,
                ticket_type: tt.ticket_type.name || 'standard', 
                benefits: tt.ticket_type.benefits || [],
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
              },
              allocated_capacity: Number(tt.allocated_capacity ?? 0),
              available_capacity: Number(tt.allocated_capacity ?? 0),
              reserved_capacity: Number(tt.reserved_capacity ?? 0),
              sold_capacity: Number(tt.sold_capacity ?? 0),
              price_modifier: Number(tt.price_modifier ?? 1),
              final_price: Number(tt.final_price ?? 0),
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            })),
          created_at: sec.created_at || new Date().toISOString(),
          updated_at: sec.updated_at || new Date().toISOString(),
        }));
        
        setLoadedSections(transformedSections);
        
        // Improved seat mapping with better error handling
        const flattenedSeats: Seat[] = apiSections.flatMap((sec: ApiSection) =>
          (sec.seats || []).map((s: ApiSeat) => ({
            id: s.id,
            seat_number: s.seat_number,
            row_number: s.row_number,
            section: sec.name || s.section || '',
            price: Number(s.price ?? 0),
            currency: s.currency || 'USD',
            is_wheelchair_accessible: Boolean(s.is_wheelchair_accessible),
            is_premium: Boolean(s.is_premium),
            status: (s.status || 'available') as 'available' | 'selected' | 'reserved' | 'sold' | 'blocked',
            ticket_type: s.ticket_type_id || undefined,
          }))
        );
        
        setAvailableSeats(flattenedSeats);
      } catch (err: unknown) {
        console.error('Failed to fetch performance sections:', err);
        
        // Show user-friendly error message
        let errorMessage = tEventDetail('seatMapLoadError');
        
        if (err && typeof err === 'object' && 'response' in err && err.response && typeof err.response === 'object' && 'status' in err.response) {
          const status = (err.response as { status: number }).status;
          if (status === 404) {
            errorMessage = tEventDetail('performanceNotFound');
          } else if (status === 500) {
            errorMessage = tEventDetail('serverError');
          }
        }
        
        if (err && typeof err === 'object' && 'message' in err && typeof err.message === 'string') {
          errorMessage = err.message;
        }
        
        showToast(errorMessage, 'error');
        setLoadedSections([]);
        setAvailableSeats([]);
      }
    };
    fetchSeats();
  }, [selectedPerformance?.id, event?.id, showToast, tEventDetail, event, selectedPerformance]);

  // Function to refresh sections data (useful for syncing capacity changes)
  const refreshSections = useCallback(async () => {
    if (!selectedPerformance || !event) return;
    
    try {
      const resp: PerformanceSeatsResponse = await getPerformanceSeats(event.id, selectedPerformance.id, { include_seats: 1 });
      const apiSections: ApiSection[] = Array.isArray(resp.sections) ? resp.sections : [];
      
      // Transform ApiSection to EventSectionData for SeatMap component
      const transformedSections = apiSections.map((sec: ApiSection) => ({
        id: sec.id || `section_${sec.name}_${Math.random().toString(36).substr(2, 9)}`,
        name: sec.name,
        description: sec.description || '',
        total_capacity: Number(sec.total_capacity ?? 0),
        available_capacity: Number(sec.available_capacity ?? 0),
        reserved_capacity: Number(sec.reserved_capacity ?? 0),
        sold_capacity: Number(sec.sold_capacity ?? 0),
        base_price: Number(sec.base_price ?? 0),
        currency: sec.currency || 'USD',
        is_wheelchair_accessible: Boolean(sec.is_wheelchair_accessible),
        is_premium: Boolean(sec.is_premium),
        occupancy_rate: Number(sec.occupancy_rate ?? 0),
        is_full: Boolean(sec.available_capacity === 0),
        ticket_types: (sec.ticket_types || [])
          .filter((tt: ApiSectionTicketType) => tt.id)
          .map((tt: ApiSectionTicketType) => ({
            id: tt.id, // Keep SectionTicketType.id for internal reference
            section: { id: sec.id || sec.name, name: sec.name },
            ticket_type: { 
              id: tt.ticket_type.id, // Use the nested ticket_type.id
              name: tt.ticket_type.name, 
              description: tt.ticket_type.description, 
              price_modifier: tt.price_modifier,
              capacity: tt.allocated_capacity,
              is_active: true,
              ticket_type: tt.ticket_type.name, 
              benefits: tt.ticket_type.benefits || [],
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            },
            allocated_capacity: Number(tt.allocated_capacity ?? 0),
            available_capacity: Number(tt.allocated_capacity ?? 0),
            reserved_capacity: Number(tt.reserved_capacity ?? 0),
            sold_capacity: Number(tt.sold_capacity ?? 0),
            price_modifier: Number(tt.price_modifier ?? 1),
            final_price: Number(tt.final_price ?? 0),
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          })),
        created_at: sec.created_at || new Date().toISOString(),
        updated_at: sec.updated_at || new Date().toISOString(),
      }));
      
      setLoadedSections(transformedSections);
      
      const flattenedSeats: Seat[] = apiSections.flatMap((sec: ApiSection) =>
        (sec.seats || []).map((s: ApiSeat) => ({
          id: s.id,
          seat_number: s.seat_number,
          row_number: s.row_number,
          section: sec.name || s.section || '',
          price: Number(s.price ?? 0),
          currency: s.currency || 'USD',
          is_wheelchair_accessible: Boolean(s.is_wheelchair_accessible),
          is_premium: Boolean(s.is_premium),
          status: (s.status || 'available') as 'available' | 'selected' | 'reserved' | 'sold' | 'blocked',
          ticket_type: s.ticket_type_id || undefined,
        }))
      );
      
      setAvailableSeats(flattenedSeats);
    } catch (err: unknown) {
      console.error('Failed to refresh sections:', err);
      
      // Show user-friendly error message
      let errorMessage = tEventDetail('errorUpdatingSeatMap');
      
      if (err && typeof err === 'object' && 'response' in err && err.response && typeof err.response === 'object' && 'status' in err.response) {
        const status = (err.response as { status: number }).status;
        if (status === 404) {
          errorMessage = tEventDetail('selectedPerformanceNotFound');
        } else if (status >= 500) {
          errorMessage = tEventDetail('serverErrorTryAgain');
        }
      }
      
      if (err && typeof err === 'object' && 'message' in err && typeof err.message === 'string') {
        errorMessage = err.message;
      }
      
      showToast(errorMessage, 'error');
    }
  }, [showToast, tEventDetail, selectedPerformance, event]);

  // Handle seat selection
  const handleSeatSelect = async (seat: Seat) => {
    if (!selectedPerformance) return;
    
          // Check capacity limits
      if (selectedSeats.length >= 10) {
        showToast(tEventDetail('maxSeatsSelectionLimit'), 'error');
        return;
      }
    
          // Check if seat is already selected
      if (selectedSeats.find(s => s.id === seat.id)) {
        showToast(tEventDetail('seatAlreadySelected'), 'error');
        return;
      }
    
    // Check available capacity for the selected section and ticket type
    if (selectedSection && selectedTicketType) {
      const sectionTicketType = selectedSection.ticket_types?.find(
        (tt) => tt.ticket_type.id === selectedTicketType.id
      );
      
      if (sectionTicketType) {
        const availableCapacity = sectionTicketType.available_capacity || 0;
        
        // Check if any seats are available at all
        if (availableCapacity === 0) {
          showToast(tEventDetail('noSeatsForSectionTicketType'), 'error');
          return;
        }
        
        const requestedQuantity = selectedSeats.length + 1; // +1 for the new seat
        
        if (requestedQuantity > availableCapacity) {
          showToast(tEventDetail('onlySeatsAvailableCannotSelect', { availableCapacity, requestedQuantity }), 'error');
          return;
        }
      }
    }
    
    try {
      await holdSeats(String(selectedPerformance.id), {
        seat_ids: [seat.id],
        ticket_type_id: selectedTicketType?.id,
        ttl_seconds: 600,
      });
              setSelectedSeats(prev => [...prev, seat]);
        showToast(tEventDetail('seatSelectedSuccess'), 'success');
      } catch (e: unknown) {
        console.error('Failed to hold seat', e);
        // Show user-friendly error message
        if (e && typeof e === 'object' && 'message' in e && typeof e.message === 'string' && e.message.includes('Only') && e.message.includes('seats available')) {
          showToast(e.message, 'error');
        } else {
          showToast(tEventDetail('errorSelectingSeat'), 'error');
        }
      }
  };

  const handleSeatDeselect = async (seat: Seat) => {
    if (!selectedPerformance) return;
    try {
      await releaseSeats(String(selectedPerformance.id), { seat_ids: [String(seat.id)] });
      showToast(tEventDetail('seatReleasedSuccess'), 'success');
    } catch (e: unknown) {
      console.error('Failed to release seat', e);
      
      // Show user-friendly error message
      let errorMessage = tEventDetail('seatReleaseError');
      
      if (e && typeof e === 'object' && 'response' in e && e.response && typeof e.response === 'object' && 'status' in e.response) {
        const status = (e.response as { status: number }).status;
        if (status === 404) {
          errorMessage = tEventDetail('seatNotFound');
        } else if (status >= 500) {
          errorMessage = tEventDetail('serverError');
        }
      }
      
      if (e && typeof e === 'object' && 'message' in e && typeof e.message === 'string') {
        errorMessage = e.message;
      }
      
      showToast(errorMessage, 'error');
    } finally {
      setSelectedSeats(prev => prev.filter(s => s.id !== seat.id));
    }
  };

  // Handle quantity change with validation
  const handleQuantityChange = (newQuantity: number) => {
    if (!selectedSection || !selectedTicketType) {
      setQuantity(newQuantity);
      return;
    }

    // Find the section ticket type to get available capacity
    const sectionTicketType = selectedSection.ticket_types?.find(
      (tt) => tt.ticket_type.id === selectedTicketType.id
    );

    if (sectionTicketType) {
      const availableCapacity = sectionTicketType.available_capacity || 0;
      
      // Validate against available capacity
      if (newQuantity > availableCapacity) {
        showToast(tEventDetail('maxSeatsAvailable', { capacity: availableCapacity, quantity: newQuantity }), 'error');
        return;
      }
      
      // Validate against total cart limit (max 10)
      const totalItems = newQuantity + selectedOptions.reduce((sum, opt) => sum + opt.quantity, 0);
      if (totalItems > 10) {
        showToast(tEventDetail('maxCartItems'), 'error');
        return;
      }
    }

    setQuantity(newQuantity);
  };

  // Handle option selection
  const handleOptionChange = (option: { id: string; name: string; max_quantity?: number; quantity: number; price: number; currency: string }, quantity: number) => {
          // Check max_quantity limit
      if (option.max_quantity && quantity > option.max_quantity) {
        showToast(tEventDetail('maxOptionQuantity', { maxQuantity: option.max_quantity }), 'error');
        return;
      }
    
    // Check total cart items limit (max 10)
    const currentTotalItems = selectedOptions.reduce((sum, opt) => sum + opt.quantity, 0) + 
                             (selectedOptions.find(opt => opt.id === option.id)?.quantity || 0);
    if (currentTotalItems + quantity > 10) {
      showToast(tEventDetail('maxCartItems'), 'error');
      return;
    }
    
    setSelectedOptions(prev => {
      const existing = prev.find(opt => opt.id === option.id);
      if (existing) {
        if (quantity === 0) {
          return prev.filter(opt => opt.id !== option.id);
        }
        return prev.map(opt => 
          opt.id === option.id ? { ...opt, quantity } : opt
        );
      }
      return quantity > 0 ? [...prev, { ...option, quantity }] : prev;
    });
    
    if (quantity > 0) {
      showToast(tEventDetail('optionAddedToCart', { optionName: option.name }), 'success');
    } else if (selectedOptions.find(opt => opt.id === option.id)) {
      showToast(tEventDetail('optionRemovedFromCart', { optionName: option.name }), 'info');
    }
  };

  // Get pricing when selections change - simplified like backup
  useEffect(() => {
    const fetchPricing = async () => {
      if (!selectedPerformance || !selectedSection || !selectedTicketType) {
        setPricingBreakdown(null);
        return;
      }

      // Validate available capacity before making the pricing request
      const sectionTicketType = selectedSection.ticket_types?.find(
        (tt) => tt.ticket_type.id === selectedTicketType.id
      );
      
      if (sectionTicketType) {
        const availableCapacity = sectionTicketType.available_capacity || 0;
        
        // Check if any seats are available at all
        if (availableCapacity === 0) {
          console.warn('No seats available for this section/ticket type');
          setPricingBreakdown(null);
          showToast(tEventDetail('noSeatsAvailable'), 'error');
          return;
        }
        
        // Use selected seats count if available, otherwise use the quantity state (for manual quantity mode)
        const requestQuantity = selectedSeats.length > 0 ? selectedSeats.length : quantity;
        
        if (requestQuantity > availableCapacity) {
          console.warn(`Cannot request ${requestQuantity} seats when only ${availableCapacity} are available`);
          setPricingBreakdown(null);
          // Show user-friendly error message
          showToast(tEventDetail('maxSeatsAvailable', { capacity: availableCapacity, quantity: requestQuantity }), 'error');
          return;
        }
        
        // Additional validation: ensure quantity doesn't exceed available capacity
        if (quantity > availableCapacity) {
          setQuantity(availableCapacity);
          showToast(tEventDetail('quantityReduced', { capacity: availableCapacity }), 'info');
        }
      }
      
      try {
        // Use selected seats count if available, otherwise use the quantity state (for manual quantity mode)
        const requestQuantity = selectedSeats.length > 0 ? selectedSeats.length : quantity;
        
        const pricingRequest = {
          performance_id: selectedPerformance.id,
          section_name: selectedSection.name,
          ticket_type_id: selectedTicketType.id,
          quantity: requestQuantity,
          selected_options: selectedOptions.map(opt => ({
            option_id: opt.id,
            quantity: opt.quantity
          })),
          discount_code: discountCode
        };
        
        const response = await calculateEventPricing(event!.id, pricingRequest);
        setPricingBreakdown(response.pricing_breakdown);
      } catch (err: unknown) {
        console.error('Failed to fetch pricing:', err);
        showToast(err && typeof err === 'object' && 'message' in err && typeof err.message === 'string' ? err.message : tEventDetail('pricingError'), 'error');
      }
    };

    fetchPricing();
  }, [selectedPerformance, selectedSection, selectedTicketType, selectedSeats, selectedOptions, discountCode, quantity, showToast, event?.id, tEventDetail, event]);

  // Handle booking
  const handleBooking = async () => {
    if (!selectedPerformance || !selectedSection || !selectedTicketType) {
      showToast(t('selectRequiredFields'), 'error');
      return;
    }

    // Validate seat selection or quantity limits
    const requestQuantity = selectedSeats.length > 0 ? selectedSeats.length : quantity;
    
    if (requestQuantity === 0) {
      showToast(tEventDetail('selectAtLeastOneSeat'), 'error');
      return;
    }
    
    if (requestQuantity > 10) {
      showToast(tEventDetail('maxSeatsLimit'), 'error');
      return;
    }
    
    // Validate available capacity for the selected section and ticket type
    if (selectedSection && selectedTicketType) {
      const sectionTicketType = selectedSection.ticket_types?.find(
        (tt) => tt.ticket_type.id === selectedTicketType.id
      );
      
      if (sectionTicketType) {
        const availableCapacity = sectionTicketType.available_capacity || 0;
        
        // Check if any seats are available at all
        if (availableCapacity === 0) {
          showToast(tEventDetail('noSeatsAvailable'), 'error');
          return;
        }
        
        if (requestQuantity > availableCapacity) {
          showToast(tEventDetail('maxSeatsAvailable', { capacity: availableCapacity, quantity: requestQuantity }), 'error');
          return;
        }
      }
    }
    
    // Validate total cart items limit
    const totalItems = selectedSeats.length + selectedOptions.reduce((sum, opt) => sum + opt.quantity, 0);
    if (totalItems > 10) {
      showToast(tEventDetail('maxCartItems'), 'error');
      return;
    }
    
    // Validate cart total limit (estimated)
    const estimatedTotal = selectedSeats.length > 0 ? 
      selectedSeats.reduce((sum, seat) => sum + seat.price, 0) : 0 +
      selectedOptions.reduce((sum, opt) => sum + (opt.price * opt.quantity), 0);
    if (estimatedTotal > 10000) {
      showToast(tEventDetail('maxOrderTotal'), 'error');
      return;
    }

    setIsBooking(true);
    
    try {


      // Validate ticket type ID before making the request
      if (!selectedTicketType.id || selectedTicketType.id.startsWith('fallback_') || selectedTicketType.id.startsWith('default_')) {
        showToast(tEventDetail('invalidTicketType'), 'error');
        return;
      }
      
      if (selectedSeats.length > 0) {
        await addEventSeatsToCart({
          event_id: event!.id,
          performance_id: selectedPerformance.id,
          ticket_type_id: selectedTicketType.id,
          seats: selectedSeats.map(seat => ({
            seat_id: seat.id,
            seat_number: seat.seat_number,
            row_number: seat.row_number,
            section: seat.section,
            price: seat.price
          })),
          selected_options: selectedOptions.map(opt => ({
            option_id: opt.id,
            quantity: opt.quantity
          })),
          special_requests: selectedOptions.length > 0 ? 
            `Options: ${selectedOptions.map(opt => `${opt.name} x${opt.quantity}`).join(', ')}` : 
            undefined
        });
      } else {
        // Fallback flow when seats are not provided: reserve by ticket type count
        await (await import('../../../../lib/api/events')).addEventToCart({
          event_id: event!.id,
          performance_id: selectedPerformance.id,
          section_name: selectedSection.name,
          ticket_type_id: selectedTicketType.id,
          quantity: Math.max(1, quantity),
          selected_options: selectedOptions.map(opt => ({ option_id: opt.id, quantity: opt.quantity })),
          special_requirements: selectedOptions.length > 0 ? `Options: ${selectedOptions.map(opt => `${opt.name} x${opt.quantity}`).join(', ')}` : undefined
        });
      }

      await refreshCart();
      router.push(`/${locale}/cart`);
    } catch (err: unknown) {
      console.error('Booking failed:', err);
      // Show user-friendly error message
      const errorMessage = err && typeof err === 'object' && 'message' in err && typeof err.message === 'string' ? err.message : t('bookingFailed');
      showToast(errorMessage, 'error');
    } finally {
      setIsBooking(false);
    }
  };

  const handleDiscountApply = () => {
    // This will trigger the useEffect for pricing
    if (!discountCode.trim()) {
      showToast(tEventDetail('enterDiscountCode'), 'error');
      return;
    }
    
    showToast(tEventDetail('discountApplied'), 'success');
    console.log('Applying discount:', discountCode);
  };

  if (isLoading && !event) {
    return (
      <motion.div 
        className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="text-center">
          <motion.div
            className="relative mx-auto mb-6"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <div className="w-16 h-16 border-4 border-blue-200 dark:border-blue-800 rounded-full"></div>
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-transparent border-t-blue-500 dark:border-t-blue-400 rounded-full animate-spin"></div>
          </motion.div>
          <motion.p 
            className="text-gray-600 dark:text-gray-400 font-medium"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            {t('loadingEvent')}
          </motion.p>
          
          {/* Loading skeleton */}
          <div className="mt-8 max-w-md mx-auto space-y-4">
            <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded"></div>
            <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded w-3/4"></div>
            <div className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 dark:from-gray-700 dark:via-gray-600 dark:to-gray-700 animate-shimmer rounded w-1/2"></div>
          </div>
        </div>
      </motion.div>
    );
  }

  if (error || !event) {
    return (
      <motion.div 
        className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <motion.div 
          className="text-center max-w-md mx-auto px-4"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="mb-6">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            </motion.div>
            <motion.h1 
              className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              {error ? t('error') || 'Error' : t('eventNotFound') || 'Event Not Found'}
            </motion.h1>
            <motion.p 
              className="text-gray-600 dark:text-gray-400 mb-6"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.5 }}
            >
              {error || t('eventNotFoundDescription') || 'The event you are looking for could not be found.'}
            </motion.p>
          </div>
          
          <motion.div 
            className="space-y-3"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <motion.button
              onClick={() => window.location.reload()}
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-lg hover:shadow-xl"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {tCommon('refresh') || 'Refresh Page'}
            </motion.button>
            
            <motion.button
              onClick={() => router.push('/events')}
              className="w-full bg-gray-200/80 dark:bg-gray-700/80 text-gray-900 dark:text-gray-100 px-6 py-3 rounded-lg hover:bg-gray-300/80 dark:hover:bg-gray-600/80 transition-all duration-300 backdrop-blur-sm"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {t('backToEvents') || 'Back to Events'}
            </motion.button>
          </motion.div>
        </motion.div>
      </motion.div>
    );
  }

  return (
    <motion.div 
      className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6 }}
    >


      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Event Header */}
        <motion.div 
          className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 mb-8 overflow-hidden"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="relative">
            <OptimizedImage
              src={event.image || '/images/event-hero.svg'}
              alt={event.title || 'Event Image'}
              width={800}
              height={256}
              className="w-full h-64 object-cover rounded-t-2xl"
              priority
              fallbackSrc="/images/event-hero.jpg"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent rounded-t-2xl" />
            <motion.div 
              className="absolute top-4 left-4"
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg backdrop-blur-sm border border-white/20">
                <Sparkles className="w-4 h-4 mr-2" />
                {event.category.name}
              </span>
            </motion.div>
          </div>
          
          <motion.div 
            className="p-8"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <motion.h1 
              className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent mb-6"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.6 }}
            >
              {event.title}
            </motion.h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              {[
                { icon: Calendar, text: event.performances?.[0] ? formatDate(event.performances[0].date) : t('noPerformances'), delay: 0.7 },
                { icon: Clock, text: event.start_time, delay: 0.8 },
                { icon: MapPin, text: event.venue.name, delay: 0.9 },
                { icon: Users, text: `${event.venue.total_capacity} ${t('capacity')}`, delay: 1.0 }
              ].map((item, index) => (
                <motion.div 
                  key={index}
                  className="flex items-center p-3 rounded-xl bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-600 border border-gray-200/50 dark:border-gray-600/50 hover:shadow-md transition-all duration-300"
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: item.delay }}
                  whileHover={{ scale: 1.02, y: -2 }}
                >
                  <item.icon className="h-5 w-5 mr-3 text-blue-500 dark:text-blue-400" />
                  <span className="text-gray-700 dark:text-gray-300 font-medium">
                    {item.text}
                  </span>
                </motion.div>
              ))}
            </div>
            
            <motion.div 
              className="flex flex-wrap items-center gap-6 mb-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.1 }}
            >
              <div className="flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border border-yellow-200/50 dark:border-yellow-700/50">
                <Star className="h-5 w-5 text-yellow-500 dark:text-yellow-400 fill-current mr-2" />
                <span className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                  {event.average_rating} ({event.review_count} {t('reviews')})
                </span>
              </div>
              
              <div className="flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 border border-primary-200/50 dark:border-primary-700/50">
                <span className="text-sm font-medium text-primary-800 dark:text-primary-200">
                  {event.style}
                </span>
              </div>
            </motion.div>
            
            <motion.p 
              className="text-gray-700 dark:text-gray-300 leading-relaxed"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 1.2 }}
            >
              {event.description}
            </motion.p>
          </motion.div>
        </motion.div>

        {/* Booking Steps */}
        <motion.div 
          className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 mb-8 overflow-hidden"
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <div className="p-8">
            <motion.h2 
              className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              {t('bookingSteps')}
            </motion.h2>
            
            {/* Enhanced responsive layout matching Transfer booking */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {bookingSteps.map((step, index) => (
                <motion.div 
                  key={step.id} 
                  className="relative"
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.5 + (index * 0.1) }}
                >
                  <div className="flex flex-col items-center text-center p-4 rounded-xl transition-all duration-300 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <motion.div 
                      className={`flex items-center justify-center w-12 h-12 rounded-full border-2 mb-3 transition-all duration-300 ${
                        step.isComplete 
                          ? 'bg-gradient-to-r from-green-500 to-emerald-600 border-green-500 text-white shadow-lg shadow-green-500/25' 
                          : step.isActive
                            ? 'bg-gradient-to-r from-blue-500 to-purple-500 border-blue-500 text-white shadow-lg shadow-blue-500/25 animate-pulse-glow' 
                            : 'bg-gray-100 dark:bg-gray-600 border-gray-300 dark:border-gray-500 text-gray-400 dark:text-gray-300'
                      }`}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {step.isComplete ? (
                        <motion.div
                          initial={{ scale: 0, rotate: -180 }}
                          animate={{ scale: 1, rotate: 0 }}
                          transition={{ duration: 0.5 }}
                        >
                          <CheckCircle className="h-6 w-6" />
                        </motion.div>
                      ) : (
                        <span className="text-sm font-bold">{step.id}</span>
                      )}
                    </motion.div>
                    
                    <div className="min-w-0 flex-1">
                      <div className={`text-sm font-semibold mb-1 transition-colors duration-300 ${
                        step.isActive ? 'text-blue-600 dark:text-blue-400' : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {step.title}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 line-clamp-2">
                        {step.description}
                      </div>
                    </div>
                  </div>
                  
                  {/* Connection line for desktop */}
                  {index < bookingSteps.length - 1 && (
                    <div className="hidden xl:block absolute top-6 -right-2 w-4 h-0.5 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-600 dark:to-gray-700" />
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Booking Flow */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <motion.div 
            className="lg:col-span-2 space-y-6"
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            {/* Performance Selection */}
            <PerformanceSelector
              performances={event.performances || []}
              selectedPerformance={selectedPerformance}
              onPerformanceSelect={handlePerformanceSelect}
              formatDate={formatDate}
              formatTime={formatTime}
              formatPrice={formatPrice}
            />

                         {/* Selected Sections Summary */}
                         {selectedSections.length > 0 && (
                           <motion.div 
                             className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 mb-6 overflow-hidden"
                             initial={{ opacity: 0, y: 20 }}
                             animate={{ opacity: 1, y: 0 }}
                             transition={{ duration: 0.5 }}
                           >
                             <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
                               <motion.h3 
                                 className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                                 initial={{ y: 10, opacity: 0 }}
                                 animate={{ y: 0, opacity: 1 }}
                                 transition={{ duration: 0.5, delay: 0.1 }}
                               >
                                 {tEventDetail('selectedSections')} ({selectedSections.length})
                               </motion.h3>
                             </div>
                             <div className="p-6">
                               <div className="flex flex-wrap gap-3">
                                 {selectedSections.map((section, index) => (
                                   <motion.div 
                                     key={section.id} 
                                     className="flex items-center gap-2 bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 text-blue-800 dark:text-blue-200 px-4 py-2 rounded-full border border-blue-200/50 dark:border-blue-700/50 shadow-sm"
                                     initial={{ scale: 0, opacity: 0 }}
                                     animate={{ scale: 1, opacity: 1 }}
                                     transition={{ duration: 0.3, delay: 0.2 + (index * 0.1) }}
                                     whileHover={{ scale: 1.05 }}
                                   >
                                     <span className="text-sm font-semibold">{section.name}</span>
                                     <motion.button
                                       onClick={() => {
                                         setSelectedSections(prev => prev.filter(s => s.id !== section.id));
                                         if (selectedSection?.id === section.id) {
                                           setSelectedSection(null);
                                         }
                                       }}
                                       className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 ml-1 font-bold"
                                       whileHover={{ scale: 1.2 }}
                                       whileTap={{ scale: 0.9 }}
                                     >
                                       ×
                                     </motion.button>
                                   </motion.div>
                                 ))}
                               </div>
                             </div>
                           </motion.div>
                         )}

                         {/* Capacity Limits Info */}
                         {selectedSection && selectedTicketType && (
                           <motion.div 
                             className="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 backdrop-blur-sm border border-yellow-200/50 dark:border-yellow-700/50 rounded-2xl p-6 mb-6 shadow-lg"
                             initial={{ opacity: 0, scale: 0.95 }}
                             animate={{ opacity: 1, scale: 1 }}
                             transition={{ duration: 0.5 }}
                           >
                             <div className="flex items-center gap-3 mb-4">
                               <motion.div
                                 initial={{ rotate: -180, scale: 0 }}
                                 animate={{ rotate: 0, scale: 1 }}
                                 transition={{ duration: 0.5, delay: 0.2 }}
                               >
                                 <Info className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
                               </motion.div>
                               <motion.h4 
                                 className="text-base font-semibold text-yellow-800 dark:text-yellow-200"
                                 initial={{ x: -20, opacity: 0 }}
                                 animate={{ x: 0, opacity: 1 }}
                                 transition={{ duration: 0.5, delay: 0.3 }}
                               >
                                 {tEventDetail('capacityLimitations')}
                               </motion.h4>
                             </div>
                             <motion.div 
                               className="text-sm text-yellow-700 dark:text-yellow-300 space-y-2"
                               initial={{ y: 20, opacity: 0 }}
                               animate={{ y: 0, opacity: 1 }}
                               transition={{ duration: 0.5, delay: 0.4 }}
                             >
                               {(() => {
                                 const sectionTicketType = selectedSection.ticket_types?.find(
                                   (tt) => tt.ticket_type.id === selectedTicketType.id
                                 );
                                 const availableCapacity = sectionTicketType?.available_capacity || 0;
                                 const totalCapacity = sectionTicketType?.allocated_capacity || 0;
                                 
                                 return (
                                   <>
                                     <p className="flex items-center gap-2">
                                       <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                                       {tEventDetail('maxSeatsTotal')}
                                     </p>
                                     <p className="flex items-center gap-2">
                                       <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                                       {tEventDetail('seatsAvailableInSection', { capacity: availableCapacity, sectionName: selectedSection.name })}
                                     </p>
                                     <p className="flex items-center gap-2">
                                       <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                                       {tEventDetail('seatsReserved', { capacity: totalCapacity - availableCapacity })}
                                     </p>
                                   </>
                                 );
                               })()}
                             </motion.div>
                           </motion.div>
                         )}

                         {/* Seat Map */}
             {selectedPerformance && (
               <div>
                 <div className="flex items-center justify-between mb-4">
                   <motion.h3 
                     className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                     initial={{ x: -20, opacity: 0 }}
                     animate={{ x: 0, opacity: 1 }}
                     transition={{ duration: 0.5 }}
                   >
                     {t('selectSeats')}
                   </motion.h3>
                   <motion.button
                     onClick={refreshSections}
                     className="px-4 py-2 text-sm bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-300 shadow-lg hover:shadow-xl backdrop-blur-sm border border-blue-500/20"
                     whileHover={{ scale: 1.05, y: -2 }}
                     whileTap={{ scale: 0.95 }}
                     initial={{ x: 20, opacity: 0 }}
                     animate={{ x: 0, opacity: 1 }}
                     transition={{ duration: 0.5, delay: 0.1 }}
                   >
                     🔄 {tCommon('refresh') || 'Refresh'}
                   </motion.button>
                 </div>
                 
                 {/* Show message if performance has no sections */}
                 {loadedSections.length === 0 && (
                   <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-700 rounded-lg p-6 text-center">
                     <div className="flex items-center justify-center mb-3">
                       <AlertTriangle className="h-8 w-8 text-orange-500" />
                     </div>
                     <h4 className="text-lg font-medium text-orange-800 dark:text-orange-200 mb-2">
                       {tEventDetail('performanceHasNoSections')}
                     </h4>
                     <p className="text-orange-700 dark:text-orange-300 mb-4">
                       {tEventDetail('pleaseSelectAnotherPerformance')}
                     </p>
                     <button
                       onClick={() => {
                         setSelectedPerformance(null);
                         setSelectedSection(null);
                         setSelectedSections([]);
                         setSelectedSeats([]);
                         setLoadedSections([]);
                         setAvailableSeats([]);
                       }}
                       className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                     >
                       {tEventDetail('selectAnotherPerformance')}
                     </button>
                   </div>
                 )}
                 
                 {/* Show seat map only if there are sections */}
                 {loadedSections.length > 0 && (
                   <SeatMap
                     sections={loadedSections}
                     ticketTypes={event.ticket_types || []}
                     seats={availableSeats}
                     selectedSeats={selectedSeats}
                     onSeatSelect={handleSeatSelect}
                     onSeatDeselect={handleSeatDeselect}
                     onSectionSelect={handleSectionSelect}
                     selectedSection={selectedSection}
                     selectedTicketType={selectedTicketType}
                     formatPrice={formatPrice}
                   />
                 )}
               </div>
             )}



                         {/* Options Selection */}
             {selectedSection && event.options && event.options.length > 0 && (
               <motion.div 
                 className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
                 initial={{ opacity: 0, y: 30 }}
                 animate={{ opacity: 1, y: 0 }}
                 transition={{ duration: 0.6 }}
               >
                 <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
                   <motion.h3 
                     className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                     initial={{ y: 10, opacity: 0 }}
                     animate={{ y: 0, opacity: 1 }}
                     transition={{ duration: 0.5, delay: 0.1 }}
                   >
                     {t('additionalOptions')}
                   </motion.h3>
                 </div>
                 <div className="p-6">
                   {/* Limits Info */}
                   <motion.div 
                     className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200/50 dark:border-blue-700/50 rounded-xl"
                     initial={{ scale: 0.95, opacity: 0 }}
                     animate={{ scale: 1, opacity: 1 }}
                     transition={{ duration: 0.5, delay: 0.2 }}
                   >
                     <div className="flex items-center text-sm text-blue-800 dark:text-blue-200">
                       <Info className="h-5 w-5 mr-3 text-blue-600 dark:text-blue-400" />
                       <span className="font-medium">{tEventDetail('limitationsMaxItemsAndTotal')}</span>
                     </div>
                   </motion.div>
                   
                   <div className="space-y-4">
                     {event.options.map((option, index) => (
                       <motion.div 
                         key={option.id} 
                         className="flex items-center justify-between p-6 border border-gray-200/50 dark:border-gray-700/50 rounded-xl bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700/50 dark:to-gray-600/50 hover:shadow-md transition-all duration-300"
                         initial={{ opacity: 0, x: -20 }}
                         animate={{ opacity: 1, x: 0 }}
                         transition={{ duration: 0.5, delay: 0.3 + (index * 0.1) }}
                         whileHover={{ scale: 1.02 }}
                       >
                         <div className="flex-1">
                           <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">{option.name}</h4>
                           <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{option.description}</p>
                           <div className="flex items-center space-x-3">
                             <span className="px-3 py-1 bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 text-green-800 dark:text-green-200 text-sm font-semibold rounded-full border border-green-200/50 dark:border-green-700/50">
                               {formatPrice(option.price, option.currency)}
                             </span>
                             {option.max_quantity && (
                               <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-full">
                                 {tEventDetail('maxQuantityLabel', { maxQuantity: option.max_quantity })}
                               </span>
                             )}
                           </div>
                         </div>
                         <div className="flex items-center space-x-3">
                           <motion.button
                             onClick={() => {
                                const currentQuantity = selectedOptions.find(opt => opt.id === option.id)?.quantity || 0;
                                handleOptionChange({
                                  id: option.id,
                                  name: option.name,
                                  max_quantity: option.max_quantity,
                                  quantity: currentQuantity,
                                  price: option.price,
                                  currency: option.currency
                                }, Math.max(0, currentQuantity - 1));
                              }}
                             className="p-2 rounded-xl bg-gradient-to-r from-red-100 to-pink-100 dark:from-red-900/30 dark:to-pink-900/30 hover:from-red-200 hover:to-pink-200 dark:hover:from-red-800/40 dark:hover:to-pink-800/40 text-red-700 dark:text-red-300 border border-red-200/50 dark:border-red-700/50 shadow-sm"
                             whileHover={{ scale: 1.1 }}
                             whileTap={{ scale: 0.9 }}
                           >
                             <Minus className="h-4 w-4" />
                           </motion.button>
                           <span className="w-12 text-center text-gray-900 dark:text-gray-100 font-bold text-lg">
                             {selectedOptions.find(opt => opt.id === option.id)?.quantity || 0}
                           </span>
                           <motion.button
                             onClick={() => {
                                const currentQuantity = selectedOptions.find(opt => opt.id === option.id)?.quantity || 0;
                                const maxAllowed = option.max_quantity || 10;
                                handleOptionChange({
                                  id: option.id,
                                  name: option.name,
                                  max_quantity: option.max_quantity,
                                  quantity: currentQuantity,
                                  price: option.price,
                                  currency: option.currency
                                }, Math.min(maxAllowed, currentQuantity + 1));
                              }}
                             className="p-2 rounded-xl bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 hover:from-green-200 hover:to-emerald-200 dark:hover:from-green-800/40 dark:hover:to-emerald-800/40 text-green-700 dark:text-green-300 border border-green-200/50 dark:border-green-700/50 shadow-sm"
                             whileHover={{ scale: 1.1 }}
                             whileTap={{ scale: 0.9 }}
                           >
                             <Plus className="h-4 w-4" />
                           </motion.button>
                         </div>
                       </motion.div>
                     ))}
                   </div>
                 </div>
               </motion.div>
             )}
          </motion.div>

          {/* Sidebar */}
          <motion.div 
            className="space-y-6"
            initial={{ x: 20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            {/* Sticky Pricing Container */}
            <div className="sticky top-24 space-y-6">
                         {/* Pricing Breakdown */}
             <PricingBreakdown
               breakdown={pricingBreakdown}
               selectedSeats={selectedSeats}
               selectedOptions={selectedOptions}
               discountCode={discountCode}
               onDiscountCodeChange={setDiscountCode}
               onApplyDiscount={handleDiscountApply}
               formatPrice={formatPrice}
               showDetails={showPricingDetails}
               onToggleDetails={() => setShowPricingDetails(!showPricingDetails)}
             />

                         {/* Booking Summary */}
             {selectedSeats.length > 0 && (
               <motion.div 
                 className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-glass dark:shadow-glass-dark border border-gray-200/50 dark:border-gray-700/50 overflow-hidden"
                 initial={{ opacity: 0, scale: 0.95 }}
                 animate={{ opacity: 1, scale: 1 }}
                 transition={{ duration: 0.5 }}
               >
                 <div className="p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
                   <motion.h3 
                     className="text-lg font-semibold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300 bg-clip-text text-transparent"
                     initial={{ y: 10, opacity: 0 }}
                     animate={{ y: 0, opacity: 1 }}
                     transition={{ duration: 0.5, delay: 0.1 }}
                   >
                     {t('bookingSummary')}
                   </motion.h3>
                 </div>
                 
                 {/* Limits Warning */}
                 <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 border-b border-yellow-200 dark:border-yellow-700">
                   <div className="flex items-center text-sm text-yellow-800 dark:text-yellow-200">
                     <AlertTriangle className="h-4 w-4 mr-2" />
                     <span>
                                             {tEventDetail('seatsAndOptions', { 
                        seats: selectedSeats.length, 
                        options: selectedOptions.reduce((sum, opt) => sum + opt.quantity, 0) 
                      })}
                     </span>
                   </div>
                 </div>
                <div className="p-4 space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">{t('performance')}</span>
                    <span className="text-gray-900 dark:text-gray-100">{selectedPerformance ? formatDate(selectedPerformance.date) : '-'}</span>
                  </div>
                  {/* Group seats by section and ticket type */}
                  {Object.entries(selectedSeats.reduce((acc: Record<string, Seat[]>, seat) => {
                    // Safely resolve ticket type name for grouping
                    let ticketTypeName = '-';
                    if (seat.ticket_type) {
                      if (typeof seat.ticket_type === 'string' && event.ticket_types) {
                        // Try to resolve name from event.ticket_types by id
                        const found = event.ticket_types.find((tt: { id: string; name: string }) => tt.id === seat.ticket_type);
                        ticketTypeName = found?.name || seat.ticket_type;
                      } else if (typeof seat.ticket_type === 'object' && seat.ticket_type.name) {
                        ticketTypeName = seat.ticket_type.name;
                      } else {
                        ticketTypeName = seat.ticket_type as string;
                      }
                    } else if (selectedTicketType?.name) {
                      ticketTypeName = selectedTicketType.name;
                    }
                    const key = `${seat.section}__${ticketTypeName}`;
                    if (!acc[key]) acc[key] = [];
                    acc[key].push(seat);
                    return acc;
                  }, {} as Record<string, Seat[]>)).map(([key, seats]: [string, Seat[]]) => {
                    // Extract ticket type name for display
                    let ticketTypeName = '-';
                    const firstSeat = seats[0];
                    if (firstSeat.ticket_type) {
                      if (typeof firstSeat.ticket_type === 'string' && event.ticket_types) {
                        const found = event.ticket_types.find((tt: { id: string; name: string }) => tt.id === firstSeat.ticket_type);
                        ticketTypeName = found?.name || firstSeat.ticket_type;
                      } else if (typeof firstSeat.ticket_type === 'object' && firstSeat.ticket_type.name) {
                        ticketTypeName = firstSeat.ticket_type.name;
                      } else {
                        ticketTypeName = firstSeat.ticket_type as string;
                      }
                    } else if (selectedTicketType?.name) {
                      ticketTypeName = selectedTicketType.name;
                    }
                    return (
                      <div key={key} className="mt-2">
                        <div className="flex justify-between text-sm font-medium">
                          <span className="text-gray-600 dark:text-gray-400">{t('section')}</span>
                          <span className="text-gray-900 dark:text-gray-100">{seats[0].section}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600 dark:text-gray-400">{t('ticketType') || 'Ticket Type'}</span>
                          <span className="text-gray-900 dark:text-gray-100">{ticketTypeName || '-'}</span>
                        </div>
                        <div className="text-sm mt-1">
                          <span className="text-gray-600 dark:text-gray-400">{t('seats')}:</span>
                          <ul className="ml-2 mt-1">
                            {seats.map(seat => (
                              <li key={seat.id} className="flex justify-between">
                                <span className="text-gray-700 dark:text-gray-300">
                                  Row {seat.row_number}, Seat {seat.seat_number}
                                  {seat.is_premium ? ' (Premium)' : ''}
                                  {seat.is_wheelchair_accessible ? ' (Wheelchair)' : ''}
                                </span>
                                <span className="text-gray-900 dark:text-gray-100">{formatPrice(Number(seat.price), seat.currency)}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    );
                  })}
                  {/* Options */}
                  {selectedOptions.length > 0 && (
                    <div className="mt-2">
                      <div className="font-medium text-sm mb-1 text-gray-700 dark:text-gray-300">{t('options')}</div>
                      <ul className="ml-2">
                        {selectedOptions.map(opt => (
                          <li key={opt.id} className="flex justify-between">
                            <span className="text-gray-700 dark:text-gray-300">{opt.name} ({opt.quantity}x)</span>
                            <span className="text-gray-900 dark:text-gray-100">{formatPrice(Number(opt.price) * Number(opt.quantity), opt.currency || 'USD')}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {/* Total */}
                  <div className="flex justify-between font-semibold mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                    <span className="text-gray-900 dark:text-gray-100">{t('total') || 'Total'}</span>
                    <span className="text-gray-900 dark:text-gray-100">{formatPrice(
                      selectedSeats.reduce((sum, seat) => sum + Number(seat.price), 0) +
                      selectedOptions.reduce((sum, opt) => sum + Number(opt.price) * Number(opt.quantity), 0),
                      'USD')}
                    </span>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Booking Button */}
            <div className="flex items-center gap-3">
              {/* Quantity Input with Better Validation */}
              {availableSeats.length === 0 && selectedSection && selectedTicketType && (
                <div className="flex items-center gap-2 border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2">
                  <span className="text-sm text-gray-600 dark:text-gray-400 mr-2">{tEventDetail('quantity')}</span>
                  <button 
                    onClick={() => handleQuantityChange(Math.max(1, quantity - 1))} 
                    className="px-2 py-1 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded disabled:opacity-50"
                    disabled={quantity <= 1}
                  >
                    -
                  </button>
                  <span className="w-8 text-center text-gray-900 dark:text-gray-100 font-medium">{quantity}</span>
                  <button 
                    onClick={() => handleQuantityChange(quantity + 1)} 
                    className="px-2 py-1 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded"
                  >
                    +
                  </button>
                  {/* Show available capacity info */}
                  {(() => {
                    const sectionTicketType = selectedSection.ticket_types?.find(
                      (tt) => tt.ticket_type.id === selectedTicketType.id
                    );
                    const availableCapacity = sectionTicketType?.available_capacity || 0;
                    return (
                      <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                        {tEventDetail('seatsAvailable', { capacity: availableCapacity })}
                      </span>
                    );
                  })()}
                </div>
              )}
              <motion.button
                onClick={handleBooking}
                disabled={isBooking || !selectedPerformance || !selectedSection || !selectedTicketType}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-6 rounded-xl font-bold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl border border-blue-500/20"
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                {isBooking ? t('booking') : t('addToCart')}
              </motion.button>
            </div>

            {/* Cancellation Policy */}
            <ProductCancellationPolicy
              policies={[
                {
                  hours_before: 48,
                  refund_percentage: 100,
                  description: tEventDetail('freeCancelEvent48h')
                },
                {
                  hours_before: 24,
                  refund_percentage: 75,
                  description: tEventDetail('refund75PercentEvent24h')
                },
                {
                  hours_before: 12,
                  refund_percentage: 50,
                  description: tEventDetail('refund50PercentEvent12h')
                },
                {
                  hours_before: 6,
                  refund_percentage: 0,
                  description: tEventDetail('noRefundEvent6h')
                }
              ]}
              productType="event"
              productData={{
                date: selectedPerformance?.date,
                venue: selectedSection?.name || event.venue?.name,
                duration: tEventDetail('eventDuration')
              }}
              className="mb-4"
            />

                         {/* Security Notice */}
             <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
               <div className="flex items-start">
                 <Shield className="h-5 w-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                 <div className="text-sm text-gray-600 dark:text-gray-400">
                   <p className="font-medium mb-1">{t('secureBooking')}</p>
                   <p>{t('secureBookingDescription')}</p>
                 </div>
               </div>
             </div>
            </div>
          </motion.div>
        </div>
      </div>
      
      {/* Toast notifications are now handled globally by ToastProvider in layout */}
    </motion.div>
  );
} 