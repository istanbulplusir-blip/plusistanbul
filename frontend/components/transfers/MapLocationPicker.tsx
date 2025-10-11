'use client';

import React, { useState, useEffect, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { MapPin, Search, X, Loader2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { TransferLocation } from '@/lib/types/api';

// Dynamic imports for SSR compatibility
const MapContainer = dynamic(() => import('react-leaflet').then(mod => ({ default: mod.MapContainer })), {
  ssr: false,
  loading: () => (
    <div className="h-96 bg-gray-200 animate-pulse rounded-lg flex items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
    </div>
  )
});

const TileLayer = dynamic(() => import('react-leaflet').then(mod => ({ default: mod.TileLayer })), {
  ssr: false
});

const Marker = dynamic(() => import('react-leaflet').then(mod => ({ default: mod.Marker })), {
  ssr: false
});

const Popup = dynamic(() => import('react-leaflet').then(mod => ({ default: mod.Popup })), {
  ssr: false
});

// useMapEvents is a hook, not a component, so we don't need dynamic import for it
import { useMapEvents } from 'react-leaflet';
import L from 'leaflet';

// Fix for default markers in React Leaflet
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom component for map events using useMapEvents hook
function MapEventsComponent({ onMapClick }: { onMapClick: (lat: number, lng: number) => void }) {
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onMapClick(lat, lng);
    }
  });
  
  return null; // This component doesn't render anything
}

interface MapLocationPickerProps {
  selectedLocation: TransferLocation | null;
  onLocationSelect: (location: TransferLocation) => void;
  onLocationClear: () => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export default function MapLocationPicker({
  selectedLocation,
  onLocationSelect,
  onLocationClear,
  placeholder,
  className = "",
  disabled = false
}: MapLocationPickerProps) {
  const t = useTranslations('transfers');
  const [isOpen, setIsOpen] = useState(false);
  const [locations, setLocations] = useState<TransferLocation[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [mapLoading, setMapLoading] = useState(true);

  // Default center for Istanbul
  const defaultCenter: [number, number] = [41.0082, 28.9784]; // Istanbul
  const [mapCenter, setMapCenter] = useState<[number, number]>(defaultCenter);
  const [zoom, setZoom] = useState(10);

  // Fetch locations
  useEffect(() => {
    const fetchLocations = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/v1/transfers/locations/', {
          credentials: 'include'
        });
        if (response.ok) {
          const data = await response.json();
          setLocations(data.results || []);
        } else {
          console.error('Failed to fetch locations:', response.statusText);
        }
      } catch (error) {
        console.error('Error fetching locations:', error);
      } finally {
        setLoading(false);
      }
    };

    if (isOpen) {
      fetchLocations();
    }
  }, [isOpen]);

  // Advanced search with API
  const [searchResults, setSearchResults] = useState<{
    database_locations: TransferLocation[];
    external_locations: TransferLocation[];
  }>({ database_locations: [], external_locations: [] });
  const [searchLoading, setSearchLoading] = useState(false);

  // Debounced search
  useEffect(() => {
    if (!searchTerm.trim()) {
      setSearchResults({ database_locations: [], external_locations: [] });
      return;
    }

    const timeoutId = setTimeout(async () => {
      setSearchLoading(true);
      try {
        const response = await fetch('/api/v1/transfers/locations/search_locations/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ query: searchTerm })
        });

        if (response.ok) {
          const data = await response.json();
          setSearchResults({
            database_locations: data.database_locations || [],
            external_locations: data.external_locations || []
          });
        }
      } catch (error) {
        console.error('Search error:', error);
      } finally {
        setSearchLoading(false);
      }
    }, 500); // 500ms debounce

    return () => clearTimeout(timeoutId);
  }, [searchTerm]);

  // Filter locations based on search
  const filteredLocations = searchTerm.trim() 
    ? [...searchResults.database_locations, ...searchResults.external_locations]
    : locations.filter(location =>
        location.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        location.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
        location.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
        location.country.toLowerCase().includes(searchTerm.toLowerCase())
      );

  const handleLocationSelect = useCallback((location: TransferLocation) => {
    onLocationSelect(location);
    setIsOpen(false);
    setMapCenter([location.coordinates.lat, location.coordinates.lng]);
    setZoom(12);
  }, [onLocationSelect]);

  const handleMapClick = useCallback(async (lat: number, lng: number) => {
    try {
      // ابتدا اعتبارسنجی مکان
      const validationResponse = await fetch('/api/v1/transfers/locations/validate_location/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ lat, lng })
      });

      if (validationResponse.ok) {
        const validationData = await validationResponse.json();
        
        if (!validationData.is_valid) {
          // نمایش پیام خطا به کاربر
          alert(`${validationData.message}\n\n${validationData.suggestion}`);
          return;
        }
        
        // اگر مکان معتبر است، ادامه فرآیند
        if (validationData.warning) {
          const proceed = confirm(`${validationData.message}\n\n${validationData.warning}\n\n${t('continueConfirmation')}`);
          if (!proceed) return;
        }
      }

      // فراخوانی API reverse geocoding
      const response = await fetch('/api/v1/transfers/locations/reverse_geocode/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ lat, lng })
      });

      if (response.ok) {
        const data = await response.json();
        
        // ایجاد مکان جدید از اطلاعات دریافتی
        const newLocation: TransferLocation = {
          id: `temp-${Date.now()}`, // ID موقت
          name: data.name,
          description: data.description || '',
          address: data.address,
          city: data.city,
          country: data.country,
          latitude: lat,
          longitude: lng,
          coordinates: { lat, lng },
          location_type: data.location_type,
          location_type_display: data.location_type_display || data.location_type,
          is_active: true,
          is_popular: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        // اضافه کردن به لیست مکان‌ها
        setLocations(prev => {
          // بررسی عدم تکرار
          const exists = prev.some(loc => 
            Math.abs(loc.coordinates.lat - lat) < 0.001 && 
            Math.abs(loc.coordinates.lng - lng) < 0.001
          );
          
          if (exists) return prev;
          return [newLocation, ...prev];
        });
        
        // انتخاب خودکار مکان جدید
        handleLocationSelect(newLocation);
      } else {
        console.error('Reverse geocoding failed:', await response.text());
        // در صورت خطا، همچنان امکان ایجاد مکان ساده وجود دارد
        const simpleLocation: TransferLocation = {
          id: `temp-${Date.now()}`,
          name: t('location'),
          description: '',
          address: `${lat.toFixed(6)}, ${lng.toFixed(6)}`,
          city: '',
          country: '',
          latitude: lat,
          longitude: lng,
          coordinates: { lat, lng },
          location_type: 'custom',
          location_type_display: 'Custom',
          is_active: true,
          is_popular: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        setLocations(prev => [simpleLocation, ...prev]);
        handleLocationSelect(simpleLocation);
      }
    } catch (error) {
      console.error('Error in map click handler:', error);
      // در صورت خطا، ایجاد مکان ساده
      const simpleLocation: TransferLocation = {
        id: `temp-${Date.now()}`,
        name: t('location'),
        description: '',
        address: `${lat.toFixed(6)}, ${lng.toFixed(6)}`,
        city: '',
        country: '',
        latitude: lat,
        longitude: lng,
        coordinates: { lat, lng },
        location_type: 'custom',
        location_type_display: 'Custom',
        is_active: true,
        is_popular: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      setLocations(prev => [simpleLocation, ...prev]);
      handleLocationSelect(simpleLocation);
    }
  }, [handleLocationSelect, t]);

  const handleClose = useCallback(() => {
    setIsOpen(false);
    setSearchTerm('');
  }, []);

  const handleClear = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onLocationClear();
  }, [onLocationClear]);

  // Note: Custom icons will be implemented when needed

  return (
    <div className={`relative ${className}`}>
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(true)}
        disabled={disabled}
        className="w-full flex items-center justify-between p-3 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-gray-500" />
          <span className="text-sm text-gray-700 truncate">
            {selectedLocation ? selectedLocation.name : (placeholder || t('locationSelection'))}
          </span>
        </div>
        {selectedLocation && (
          <div
            onClick={handleClear}
            className="p-1 hover:bg-gray-200 rounded transition-colors cursor-pointer"
          >
            <X className="h-4 w-4 text-gray-500" />
          </div>
        )}
      </button>

      {/* Map Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 dark:bg-black dark:bg-opacity-70">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-6xl mx-4 max-h-[90vh] overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{t('locationSelection')}</h3>
              <button
                type="button"
                onClick={handleClose}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>

            {/* Search Bar */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-gray-500" />
                <input
                  type="text"
                  placeholder={t('searchLocation')}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                />
                {searchLoading && (
                  <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 animate-spin text-gray-400 dark:text-gray-500" />
                )}
              </div>
              {searchTerm && (
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  {t('databaseCount')} {searchResults.database_locations.length} {t('externalCount')} {searchResults.external_locations.length}
                </div>
              )}
            </div>

            <div className="flex flex-col lg:flex-row">
              {/* Map */}
              <div className="flex-1 lg:order-1">
                <div className="h-64 lg:h-96">
                  <MapContainer
                    center={mapCenter}
                    zoom={zoom}
                    style={{ height: '100%', width: '100%' }}
                    whenReady={() => setMapLoading(false)}
                  >
                    <TileLayer
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    
                    <MapEventsComponent onMapClick={handleMapClick} />
                    
                    {!mapLoading && filteredLocations.map((location) => (
                      <Marker
                        key={location.id}
                        position={[location.coordinates.lat, location.coordinates.lng]}
                        eventHandlers={{
                          click: () => handleLocationSelect(location),
                        }}
                      >
                        <Popup>
                          <div className="p-2 text-right">
                            <h3 className="font-semibold text-sm">{location.name}</h3>
                            <p className="text-xs text-gray-600">{location.address}</p>
                            <p className="text-xs text-gray-500">{location.city}, {location.country}</p>
                            {location.is_popular && (
                              <span className="inline-block mt-1 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                محبوب
                              </span>
                            )}
                          </div>
                        </Popup>
                      </Marker>
                    ))}
                  </MapContainer>
                </div>
              </div>

              {/* Location List */}
              <div className="w-full lg:w-80 border-t lg:border-t-0 lg:border-l border-gray-200 dark:border-gray-700 lg:order-2">
                <div className="p-3 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {searchTerm ? t('searchResults') : t('availableLocations')}
                  </h4>
                </div>
                <div className="max-h-64 lg:max-h-96 overflow-y-auto">
                  {loading ? (
                    <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                      <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                      {t('loading')}
                    </div>
                  ) : searchLoading ? (
                    <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                      <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                      {t('searching')}
                    </div>
                  ) : filteredLocations.length > 0 ? (
                    <div className="max-h-96 overflow-y-auto">
                      {/* Database Locations */}
                      {searchTerm && searchResults.database_locations.length > 0 && (
                        <div className="p-2 bg-blue-50 dark:bg-blue-900/20 border-b border-blue-200 dark:border-blue-700">
                          <h5 className="text-xs font-medium text-blue-800 dark:text-blue-300">{t('databaseLocations')}</h5>
                        </div>
                      )}
                      {searchTerm 
                        ? searchResults.database_locations.map((location) => (
                            <button
                              key={location.id}
                              type="button"
                              onClick={() => handleLocationSelect(location)}
                              className="w-full p-3 text-right hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:bg-gray-50 dark:focus:bg-gray-700 border-b border-gray-100 dark:border-gray-600"
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <h4 className="font-medium text-sm text-gray-900 dark:text-gray-100">{location.name}</h4>
                                  <p className="text-xs text-gray-600 dark:text-gray-400">{location.city}, {location.country}</p>
                                  <p className="text-xs text-gray-500 dark:text-gray-500 truncate">{location.address}</p>
                                </div>
                                <div className="flex flex-col items-end gap-1">
                                  {location.is_popular && (
                                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                      {t('popular')}
                                    </span>
                                  )}
                                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                    {t('available')}
                                  </span>
                                </div>
                              </div>
                            </button>
                          ))
                        : locations.filter(location =>
                            location.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            location.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            location.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            location.country.toLowerCase().includes(searchTerm.toLowerCase())
                          ).map((location) => (
                            <button
                              key={location.id}
                              type="button"
                              onClick={() => handleLocationSelect(location)}
                              className="w-full p-3 text-right hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:bg-gray-50 dark:focus:bg-gray-700 border-b border-gray-100 dark:border-gray-600"
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <h4 className="font-medium text-sm text-gray-900 dark:text-gray-100">{location.name}</h4>
                                  <p className="text-xs text-gray-600 dark:text-gray-400">{location.city}, {location.country}</p>
                                  <p className="text-xs text-gray-500 dark:text-gray-500 truncate">{location.address}</p>
                                </div>
                                <div className="flex flex-col items-end gap-1">
                                  {location.is_popular && (
                                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                      محبوب
                                    </span>
                                  )}
                                  <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                                    {location.location_type || 'مکان'}
                                  </span>
                                </div>
                              </div>
                            </button>
                          ))
                      }
                      
                      {/* External Locations */}
                      {searchTerm && searchResults.external_locations.length > 0 && (
                        <>
                          <div className="p-2 bg-yellow-50 border-b border-yellow-200">
                            <h5 className="text-xs font-medium text-yellow-800">{t('externalLocations')}</h5>
                          </div>
                          {searchResults.external_locations.map((location) => (
                            <button
                              key={location.id}
                              type="button"
                              onClick={() => handleLocationSelect(location)}
                              className="w-full p-3 text-right hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:bg-gray-50 dark:focus:bg-gray-700 border-b border-gray-100 dark:border-gray-600"
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <h4 className="font-medium text-sm text-gray-900 dark:text-gray-100">{location.name}</h4>
                                  <p className="text-xs text-gray-600 dark:text-gray-400">{location.city}, {location.country}</p>
                                  <p className="text-xs text-gray-500 dark:text-gray-500 truncate">{location.address}</p>
                                </div>
                                <div className="flex flex-col items-end gap-1">
                                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                                    {t('external')}
                                  </span>
                                  <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">
                                    {t('needsReview')}
                                  </span>
                                </div>
                              </div>
                            </button>
                          ))}
                        </>
                      )}
                    </div>
                  ) : (
                    <div className="p-4 text-center text-gray-500">
                      {searchTerm ? t('noLocationsWithSearch') : t('noLocationsFound')}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {searchTerm 
                    ? `${searchResults.database_locations.length} ${t('databaseCount')} ${searchResults.external_locations.length} ${t('externalCount')}`
                    : `${filteredLocations.length} ${t('locationCount')}`
                  }
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-500">
                  {searchTerm 
                    ? t('databaseLocationsPriority')
                    : t('clickMapOrSelect')
                  }
                </div>
              </div>
              {searchTerm && (
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-500">
                  {t('externalLocationsWarning')}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

