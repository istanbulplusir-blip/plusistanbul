'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Search, Map } from 'lucide-react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { useTranslations } from 'next-intl';

interface Location {
  id: string;
  name: string;
  description?: string;
  address: string;
  city: string;
  country: string;
  latitude?: number;
  longitude?: number;
  location_type: 'airport' | 'hotel' | 'station' | 'city_center' | 'port' | 'other';
}

interface LocationSelectorProps {
  value: string;
  onChange: (location: string, coordinates?: { lat: number; lng: number }) => void;
  placeholder: string;
  locations: Location[];
  allowCustom?: boolean;
  locationType?: 'pickup' | 'dropoff';
  error?: string;
  className?: string;
}

export default function LocationSelector({
  value,
  onChange,
  placeholder,
  locations,
  allowCustom = true,
  error,
  className = ''
}: LocationSelectorProps) {
  const t = useTranslations('carRentalBooking');
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<'predefined' | 'custom'>('predefined');
  const [customLocation, setCustomLocation] = useState('');
  const [customCoordinates] = useState<{ lat: number; lng: number } | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Filter locations based on search term
  const filteredLocations = (locations || []).filter(location =>
    location.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    location.address?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    location.city?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Group locations by type
  const groupedLocations = filteredLocations.reduce((acc, location) => {
    const locationType = location.location_type || 'other';
    if (!acc[locationType]) {
      acc[locationType] = [];
    }
    acc[locationType].push(location);
    return acc;
  }, {} as Record<string, Location[]>);

  const locationTypeLabels = {
    airport: t('locationTypes.airport'),
    hotel: t('locationTypes.hotel'),
    station: t('locationTypes.station'),
    city_center: t('locationTypes.cityCenter'),
    port: t('locationTypes.port'),
    other: t('locationTypes.other')
  };

  // Handle location selection
  const handleLocationSelect = (location: Location) => {
    onChange(location.name || '', location.latitude && location.longitude ? {
      lat: location.latitude,
      lng: location.longitude
    } : undefined);
    setIsOpen(false);
    setSearchTerm('');
  };

  // Handle custom location
  const handleCustomLocation = () => {
    if (customLocation.trim()) {
      onChange(customLocation, customCoordinates || undefined);
      setIsOpen(false);
    }
  };

  // Handle map selection (placeholder for future implementation)
  const handleMapSelection = () => {
    // This would open a map modal in a real implementation
    console.log('Open map for location selection');
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node) &&
          inputRef.current && !inputRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className={`relative ${className}`}>
      <div className="relative">
        <Input
          ref={inputRef}
          value={value}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            if (allowCustom) {
              setCustomLocation(e.target.value);
              setSelectedType('custom');
            }
          }}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          className={`pr-10 ${error ? 'border-red-500' : ''}`}
        />
        <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
      </div>

      {error && (
        <p className="text-red-500 text-sm mt-1">{error}</p>
      )}

      <AnimatePresence>
        {isOpen && (
          <motion.div
            ref={dropdownRef}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg max-h-80 overflow-y-auto"
          >
            {/* Location Type Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setSelectedType('predefined')}
                className={`flex-1 px-4 py-2 text-sm font-medium ${
                  selectedType === 'predefined'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {t('predefinedLocations')}
              </button>
              {allowCustom && (
                <button
                  onClick={() => setSelectedType('custom')}
                  className={`flex-1 px-4 py-2 text-sm font-medium ${
                    selectedType === 'custom'
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {t('customLocation')}
                </button>
              )}
            </div>

            {selectedType === 'predefined' ? (
              <div className="p-2">
                {Object.keys(groupedLocations).length === 0 ? (
                  <div className="text-center py-4 text-gray-500">
                    {t('noLocationsFound')}
                  </div>
                ) : (
                  Object.entries(groupedLocations).map(([type, locations]) => (
                    <div key={type} className="mb-4">
                      <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                        {locationTypeLabels[type as keyof typeof locationTypeLabels] || t('locationTypes.other')}
                      </div>
                      {locations.map((location, index) => (
                        <button
                          key={location.id || location.name || `location-${type}-${index}`}
                          onClick={() => handleLocationSelect(location)}
                          className="w-full text-left p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-md transition-colors"
                        >
                          <div className="flex items-start">
                            <MapPin className="w-4 h-4 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                            <div className="flex-1 min-w-0">
                              <div className="font-medium text-gray-900 dark:text-white truncate">
                                {location.name || 'Unknown Location'}
                              </div>
                              <div className="text-sm text-gray-500 truncate">
                                {location.address || ''}
                              </div>
                              <div className="text-xs text-gray-400">
                                {location.city || ''}, {location.country || ''}
                              </div>
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  ))
                )}
              </div>
            ) : (
              <div className="p-4">
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {t('customLocationAddress')}
                    </label>
                    <Input
                      value={customLocation}
                      onChange={(e) => setCustomLocation(e.target.value)}
                      placeholder={t('enterCustomLocation')}
                    />
                  </div>
                  
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleMapSelection}
                    className="w-full"
                  >
                    <Map className="w-4 h-4 mr-2" />
                    {t('selectFromMap')}
                  </Button>
                  
                  <Button
                    type="button"
                    onClick={handleCustomLocation}
                    disabled={!customLocation.trim()}
                    className="w-full"
                  >
                    {t('confirmLocation')}
                  </Button>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
