'use client';

import { useState, useCallback, useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { 
  User, 
  Star, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw,
  Eye,
  EyeOff
} from 'lucide-react';
import { TicketType } from '@/lib/types/api';

// Define the interface to match the data structure from parent
interface EventSectionData {
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
}

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

interface SeatMapProps {
  sections: EventSectionData[];
  ticketTypes: TicketType[];
  seats?: Seat[];
  selectedSeats: Seat[];
  onSeatSelect: (seat: Seat) => void;
  onSeatDeselect: (seat: Seat) => void;
  onSectionSelect: (section: EventSectionData) => void;
  selectedSection: EventSectionData | null;
  selectedTicketType: TicketType | null;
  maxSelectableSeats?: number;
  formatPrice: (amount: number, currency: string) => string;
}

export default function SeatMap({
  sections,
  seats = [],
  selectedSeats,
  onSeatSelect,
  onSeatDeselect,
  onSectionSelect,
  selectedSection,
  selectedTicketType,
  maxSelectableSeats = 8,
  formatPrice
}: SeatMapProps) {
  const t = useTranslations('seatMap');
  const [zoomLevel, setZoomLevel] = useState(1);
  const [showLegend, setShowLegend] = useState(true);
  const [viewMode, setViewMode] = useState<'sections' | 'seats'>('sections');
  const [hoveredSection, setHoveredSection] = useState<EventSectionData | null>(null);

  // Seat data should be provided by parent via API; no mock generation here

  // Get seats for selected section
  const sectionSeats = useMemo(() => {
    if (!selectedSection) return [] as Seat[];
    // Filter provided seats by selected section
    return seats.filter(s => s.section === selectedSection.name);
  }, [selectedSection, seats]);

  // Group seats by row for display
  const seatsByRow = useMemo(() => {
    const grouped: { [key: string]: Seat[] } = {};
    sectionSeats.forEach(seat => {
      if (!grouped[seat.row_number]) {
        grouped[seat.row_number] = [];
      }
      grouped[seat.row_number].push(seat);
    });
    
    // Sort seats within each row
    Object.keys(grouped).forEach(row => {
      grouped[row].sort((a, b) => parseInt(a.seat_number) - parseInt(b.seat_number));
    });
    
    return grouped;
  }, [sectionSeats]);

  const handleSeatClick = useCallback((seat: Seat) => {
    // Allow selection of available and reserved seats (reserved seats can be "stolen" from other users)
    if (seat.status === 'sold' || seat.status === 'blocked') return;
    
    const isSelected = selectedSeats.some(s => s.id === seat.id);
    
    if (isSelected) {
      onSeatDeselect(seat);
    } else {
      if (selectedSeats.length >= maxSelectableSeats) {
        alert(t('maxSeatsReached', { max: maxSelectableSeats }));
        return;
      }
      
      // If seat is reserved, show warning
      if (seat.status === 'reserved') {
        if (!confirm(t('seatReservedWarning') || 'This seat is currently reserved by another user. Do you want to take it? This will cancel their reservation.')) {
          return;
        }
      }
      
      onSeatSelect({ ...seat, status: 'selected', ticket_type: selectedTicketType?.name });
    }
  }, [selectedSeats, maxSelectableSeats, onSeatSelect, onSeatDeselect, t, selectedTicketType]);

  // Auto-switch to seats view when section is selected
  const handleSectionSelect = useCallback((section: EventSectionData) => {
    onSectionSelect(section);
    setViewMode('seats'); // Automatically switch to seats view
  }, [onSectionSelect]);

  const getSeatClassName = useCallback((seat: Seat) => {
    const isSelected = selectedSeats.some(s => s.id === seat.id);
    const baseClasses = 'w-6 h-6 m-0.5 rounded-sm border text-xs flex items-center justify-center cursor-pointer transition-all hover:scale-110';
    
    if (isSelected) {
      return `${baseClasses} bg-blue-600 border-blue-700 text-white shadow-md`;
    }
    
    switch (seat.status) {
      case 'available':
        if (seat.is_premium) {
          return `${baseClasses} bg-yellow-100 dark:bg-yellow-900/30 border-yellow-300 dark:border-yellow-600 text-yellow-800 dark:text-yellow-200 hover:bg-yellow-200 dark:hover:bg-yellow-900/50`;
        }
        if (seat.is_wheelchair_accessible) {
          return `${baseClasses} bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-600 text-green-800 dark:text-green-200 hover:bg-green-200 dark:hover:bg-green-900/50`;
        }
        return `${baseClasses} bg-gray-100 dark:bg-gray-700 border-gray-300 dark:border-gray-500 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600`;
      case 'reserved':
        return `${baseClasses} bg-orange-200 dark:bg-orange-900/30 border-orange-300 dark:border-orange-600 text-orange-800 dark:text-orange-200 cursor-not-allowed opacity-70`;
      case 'sold':
        return `${baseClasses} bg-red-200 dark:bg-red-900/30 border-red-300 dark:border-red-600 text-red-800 dark:text-red-200 cursor-not-allowed opacity-70`;
      case 'blocked':
        return `${baseClasses} bg-gray-300 dark:bg-gray-600 border-gray-400 dark:border-gray-500 text-gray-600 dark:text-gray-400 cursor-not-allowed opacity-50`;
      default:
        return baseClasses;
    }
  }, [selectedSeats]);

  const getSectionClassName = useCallback((section: EventSectionData) => {
    const isSelected = selectedSection?.id === section.id;
    const isHovered = hoveredSection?.id === section.id;
    const occupancyRate = ((section.total_capacity - section.available_capacity) / section.total_capacity) * 100;
    
    let colorClass = 'bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-600 text-green-800 dark:text-green-200'; // Default: available
    if (occupancyRate > 80) colorClass = 'bg-red-100 dark:bg-red-900/30 border-red-300 dark:border-red-600 text-red-800 dark:text-red-200';
    else if (occupancyRate > 50) colorClass = 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-300 dark:border-yellow-600 text-yellow-800 dark:text-yellow-200';
    
    return `relative p-4 rounded-lg border-2 cursor-pointer transition-all ${
      isSelected 
        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 shadow-lg' 
        : isHovered 
          ? `${colorClass} shadow-md scale-105` 
          : `${colorClass} hover:shadow-md`
    }`;
  }, [selectedSection, hoveredSection]);

  const handleZoom = useCallback((direction: 'in' | 'out' | 'reset') => {
    setZoomLevel(prev => {
      switch (direction) {
        case 'in': return Math.min(prev + 0.2, 2);
        case 'out': return Math.max(prev - 0.2, 0.5);
        case 'reset': return 1;
        default: return prev;
      }
    });
  }, []);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
        <div className="flex flex-col space-y-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {t('seatSelection')}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {selectedSeats.length} / {maxSelectableSeats} {t('seatsSelected')}
            </p>
          </div>
          
          <div className="flex flex-col space-y-3 sm:flex-row sm:items-center sm:space-y-0 sm:space-x-2">
            {/* View Mode Toggle */}
            <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
              <button
                onClick={() => setViewMode('sections')}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'sections'
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
                }`}
              >
                {t('sections')}
              </button>
              <button
                onClick={() => setViewMode('seats')}
                disabled={!selectedSection}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'seats'
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 shadow-sm'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 disabled:opacity-50'
                }`}
              >
                {t('seats')}
              </button>
            </div>
            
            {/* Controls */}
            <div className="flex items-center justify-center space-x-1 border-t border-gray-200 dark:border-gray-600 pt-3 sm:border-t-0 sm:border-l sm:pl-2 sm:pt-0">
              <button
                onClick={() => handleZoom('out')}
                className="p-2 sm:p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 rounded touch-manipulation"
                disabled={zoomLevel <= 0.5}
                title={t('zoomOut')}
              >
                <ZoomOut className="h-4 w-4" />
              </button>
              
              <button
                onClick={() => handleZoom('reset')}
                className="p-2 sm:p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 rounded touch-manipulation"
                title={t('resetZoom')}
              >
                <RotateCcw className="h-4 w-4" />
              </button>
              
              <button
                onClick={() => handleZoom('in')}
                className="p-2 sm:p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 rounded touch-manipulation"
                disabled={zoomLevel >= 2}
                title={t('zoomIn')}
              >
                <ZoomIn className="h-4 w-4" />
              </button>
              
              <button
                onClick={() => setShowLegend(!showLegend)}
                className="p-2 sm:p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-600 rounded touch-manipulation"
                title={showLegend ? t('hideLegend') : t('showLegend')}
              >
                {showLegend ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row">
        {/* Main Map Area */}
        <div 
          className="flex-1 p-2 sm:p-4 overflow-auto"
          style={{ 
            transform: `scale(${zoomLevel})`, 
            transformOrigin: 'top left',
            minHeight: '300px'
          }}
        >
          {/* Stage Area */}
          <div className="text-center mb-6 sm:mb-8">
            <div className="bg-gray-800 dark:bg-gray-700 text-white py-2 px-4 sm:px-8 rounded-lg inline-block">
              <span className="font-medium">{t('stage')}</span>
            </div>
          </div>

          {viewMode === 'sections' ? (
            /* Sections View */
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
              {sections.map((section) => {
                const occupancyRate = ((section.total_capacity - section.available_capacity) / section.total_capacity) * 100;
                
                return (
                  <div
                    key={section.id || `section_${section.name}_${Math.random().toString(36).substr(2, 9)}`}
                    className={getSectionClassName(section)}
                    onClick={() => handleSectionSelect(section)}
                    onMouseEnter={() => setHoveredSection(section)}
                    onMouseLeave={() => setHoveredSection(null)}
                  >
                    <div className="text-center">
                      <h4 className="font-bold text-lg mb-1 text-gray-900 dark:text-gray-100">{section.name}</h4>
                      <div className="text-sm opacity-90 mb-2 text-gray-700 dark:text-gray-300">
                        {section.available_capacity} / {section.total_capacity}
                      </div>
                      <div className="text-xs opacity-75 mb-2 text-gray-600 dark:text-gray-400">
                        {formatPrice(section.base_price, section.currency)}
                      </div>
                      
                      {/* Features */}
                      <div className="flex justify-center space-x-1">
                        {section.is_wheelchair_accessible && (
                          <User className="h-3 w-3" />
                        )}
                        {section.is_premium && (
                          <Star className="h-3 w-3" />
                        )}
                      </div>

                      {/* Ticket Types Preview */}
                      {section.ticket_types && section.ticket_types.length > 0 && (
                        <div className="mt-2 text-xs">
                          <div className="text-gray-600 dark:text-gray-400 mb-1">{t('ticketTypes')}:</div>
                          <div className="space-y-1">
                            {section.ticket_types.slice(0, 2).map((tt) => (
                              <div key={tt.id} className="flex justify-between">
                                <span className="text-gray-700 dark:text-gray-300 truncate">{tt.ticket_type.name}</span>
                                <span className="font-medium ml-1">{formatPrice(tt.final_price, section.currency)}</span>
                              </div>
                            ))}
                            {section.ticket_types.length > 2 && (
                              <div className="text-gray-500 dark:text-gray-400 text-center">
                                +{section.ticket_types.length - 2} {t('more')}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      
                      {/* Occupancy Bar */}
                      <div className="mt-2 bg-white dark:bg-gray-800 bg-opacity-50 dark:bg-opacity-30 rounded-full h-1">
                        <div
                          className="bg-current h-1 rounded-full transition-all"
                          style={{ width: `${occupancyRate}%` }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            /* Seats View */
            selectedSection && (
              <div className="max-w-4xl mx-auto">
                <div className="text-center mb-6">
                  <h4 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    {t('section')} {selectedSection.name}
                  </h4>
                  <p className="text-gray-600 dark:text-gray-400">
                    {formatPrice(selectedSection.base_price, selectedSection.currency)} • {selectedSection.available_capacity} {t('available')}
                  </p>
                  
                  {/* Mobile-friendly section change button */}
                  <button
                    onClick={() => setViewMode('sections')}
                    className="mt-3 px-4 py-2 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg text-sm font-medium hover:bg-blue-200 dark:hover:bg-blue-900/30 transition-colors sm:hidden"
                  >
                    {t('changeSection')}
                  </button>
                </div>
                
                <div className="space-y-3 sm:space-y-2">
                  {Object.entries(seatsByRow)
                    .sort(([a], [b]) => parseInt(a) - parseInt(b))
                    .map(([rowNumber, rowSeats]) => (
                      <div key={rowNumber} className="flex flex-col sm:flex-row sm:items-center sm:justify-center space-y-2 sm:space-y-0 sm:space-x-1">
                        {/* Row Label */}
                        <div className="text-center sm:text-left sm:w-8 text-sm font-medium text-gray-500 dark:text-gray-400">
                          {rowNumber}
                        </div>
                        
                        {/* Seats */}
                        <div className="flex flex-wrap justify-center sm:justify-start gap-1 sm:space-x-0.5">
                          {rowSeats.map((seat) => (
                            <div
                              key={seat.id}
                              className={getSeatClassName(seat)}
                              onClick={() => handleSeatClick(seat)}
                              title={`${t('seat')} ${seat.seat_number} - ${t('row')} ${seat.row_number}${
                                seat.is_wheelchair_accessible ? ` - ${t('wheelchairAccessible')}` : ''
                              }${seat.is_premium ? ` - ${t('premium')}` : ''}`}
                            >
                              {seat.is_wheelchair_accessible ? (
                                <User className="h-3 w-3" />
                              ) : seat.is_premium ? (
                                <Star className="h-3 w-3" />
                              ) : (
                                seat.seat_number
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )
          )}
        </div>

        {/* Legend */}
        {showLegend && (
          <div className="w-full lg:w-64 bg-gray-50 dark:bg-gray-700 border-t lg:border-t-0 lg:border-l border-gray-200 dark:border-gray-600 p-4">
            <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">{t('legend')}</h4>
            
            <div className="grid grid-cols-2 lg:grid-cols-1 gap-3 text-sm">
              <div className="flex items-center">
                <div className="w-5 h-5 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-500 rounded-sm mr-2"></div>
                <span className="text-gray-700 dark:text-gray-300">{t('available')}</span>
              </div>
              
              <div className="flex items-center">
                <div className="w-5 h-5 bg-blue-600 border border-blue-700 rounded-sm mr-2"></div>
                <span className="text-gray-700 dark:text-gray-300">{t('selected')}</span>
              </div>
              
              <div className="flex items-center">
                <div className="w-5 h-5 bg-yellow-100 dark:bg-yellow-900/30 border border-yellow-300 dark:border-yellow-600 rounded-sm mr-2 flex items-center justify-center">
                  <Star className="h-3 w-3 text-yellow-600 dark:text-yellow-400" />
                </div>
                <span className="text-gray-700 dark:text-gray-300">{t('premium')}</span>
              </div>
              
              <div className="flex items-center">
                <div className="w-5 h-5 bg-green-100 dark:bg-green-900/30 border border-green-300 dark:border-green-600 rounded-sm mr-2 flex items-center justify-center">
                  <User className="h-3 w-3 text-green-600 dark:text-green-400" />
                </div>
                <span className="text-gray-700 dark:text-gray-300">{t('wheelchairAccessible')}</span>
              </div>
              
              <div className="flex items-center">
                <div className="w-5 h-5 bg-orange-200 dark:bg-orange-900/30 border border-orange-300 dark:border-orange-600 rounded-sm mr-2"></div>
                <span className="text-gray-700 dark:text-gray-300">{t('reserved')}</span>
              </div>
              
              <div className="flex items-center">
                <div className="w-5 h-5 bg-red-200 dark:bg-red-900/30 border border-red-300 dark:border-red-600 rounded-sm mr-2"></div>
                <span className="text-gray-700 dark:text-gray-300">{t('sold')}</span>
              </div>
            </div>
            
            {/* Section Ticket Type Pricing */}
            {selectedSection && selectedSection.ticket_types && selectedSection.ticket_types.length > 0 && (
              <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
                <h5 className="font-medium text-gray-900 dark:text-gray-100 mb-3">{t('ticketTypePricing')}</h5>
                <div className="space-y-2 text-sm">
                  {selectedSection.ticket_types.map((sectionTicketType) => (
                    <div key={sectionTicketType.id} className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-600 rounded-md">
                      <div className="flex-1">
                        <div className="font-medium text-gray-900 dark:text-gray-100">
                          {sectionTicketType.ticket_type.name}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {sectionTicketType.available_capacity}/{sectionTicketType.allocated_capacity} {t('available')}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium text-gray-900 dark:text-gray-100">
                          {formatPrice(sectionTicketType.final_price, selectedSection.currency)}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {sectionTicketType.price_modifier}x {t('base')}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedSeats.length > 0 && (
              <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
                <h5 className="font-medium text-gray-900 dark:text-gray-100 mb-2">{t('selectedSeats')}</h5>
                <div className="space-y-1 text-sm">
                  {selectedSeats.map((seat) => (
                    <div key={seat.id} className="flex justify-between">
                      <span className="text-gray-700 dark:text-gray-300">{seat.section} {seat.row_number}-{seat.seat_number}</span>
                      <span className="font-medium text-gray-900 dark:text-gray-100">{formatPrice(seat.price, seat.currency)}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-2 pt-2 border-t border-gray-300 dark:border-gray-600">
                  <div className="flex justify-between font-semibold">
                    <span className="text-gray-900 dark:text-gray-100">{t('total')}</span>
                    <span className="text-gray-900 dark:text-gray-100">
                      {formatPrice(
                        selectedSeats.reduce((sum, seat) => sum + Number(seat.price), 0),
                        'USD'
                      )}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 