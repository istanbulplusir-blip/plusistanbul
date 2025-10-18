'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';
import { Loading } from '@/components/ui/Loading';
import { agentApi, Tour } from '@/lib/api/agents';


interface TourSelectorProps {
  bookingData: {
    tour: Tour | null;
    variant: unknown;
    date: unknown;
    participants: unknown;
    options: unknown;
    customer: unknown;
    pricing: unknown;
  };
  onComplete: (data: { tour: Tour }) => void;
  onPrevious: () => void;
  onNext: () => void;
  isFirstStep: boolean;
  isLastStep: boolean;
}

export default function TourSelector({ 
  bookingData, 
  onComplete, 
  onPrevious, 
  isFirstStep 
}: TourSelectorProps) {
  const t = useTranslations('Agent.booking.tourSelector');
  const [tours, setTours] = useState<Tour[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTour, setSelectedTour] = useState<Tour | null>(bookingData.tour);
  const [filteredTours, setFilteredTours] = useState<Tour[]>([]);

  useEffect(() => {
    // Fetch tours from API
    const fetchTours = async () => {
      try {
        setLoading(true);
        const toursData = await agentApi.tours.getTours();
        setTours(toursData);
        setFilteredTours(toursData);
      } catch (error) {
        console.error('Error fetching tours:', error);
        // Fallback to mock data if API fails
        const mockTours: Tour[] = [
          {
            id: 1,
            title: 'تور فرهنگی تهران',
            description: 'بازدید از موزه‌ها و بناهای تاریخی تهران',
            base_price: 100,
            agent_price: 85,
            duration: '8 ساعت',
            location: 'تهران',
            image: '/images/destinations/tehran.jpg',
            category: 'فرهنگی',
            is_active: true
          },
          {
            id: 2,
            title: 'تور طبیعت‌گردی شمال',
            description: 'گردش در جنگل‌ها و کوه‌های شمال ایران',
            base_price: 150,
            agent_price: 127,
            duration: '12 ساعت',
            location: 'مازندران',
            image: '/images/destinations/mazandaran.jpg',
            category: 'طبیعت',
            is_active: true
          },
          {
            id: 3,
            title: 'تور تاریخی اصفهان',
            description: 'بازدید از بناهای تاریخی و معماری اصفهان',
            base_price: 120,
            agent_price: 102,
            duration: '10 ساعت',
            location: 'اصفهان',
            image: '/images/destinations/isfahan.jpg',
            category: 'تاریخی',
            is_active: true
          }
        ];
        setTours(mockTours);
        setFilteredTours(mockTours);
      } finally {
        setLoading(false);
      }
    };

    fetchTours();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const filtered = tours.filter(tour =>
        tour.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tour.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tour.location.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredTours(filtered);
    } else {
      setFilteredTours(tours);
    }
  }, [searchTerm, tours]);

  const handleTourSelect = (tour: Tour) => {
    setSelectedTour(tour);
  };

  const handleContinue = () => {
    if (selectedTour) {
      onComplete({ tour: selectedTour });
    }
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="relative">
        <Input
          type="text"
          placeholder={t('searchPlaceholder')}
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

      {/* Tours Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTours.map((tour) => (
          <Card
            key={tour.id}
            className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
              selectedTour?.id === tour.id 
                ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                : 'hover:ring-1 hover:ring-gray-300'
            }`}
            onClick={() => handleTourSelect(tour)}
          >
            <div className="p-6">
              {/* Image */}
              <div className="relative w-full h-48 mb-4 bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden">
                <Image
                  src={tour.image}
                  alt={tour.title}
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                />
              </div>

              {/* Content */}
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {tour.title}
                  </h3>
                  <Badge variant="secondary">{tour.category}</Badge>
                </div>

                <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                  {tour.description}
                </p>

                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {tour.location}
                </div>

                <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {tour.duration}
                </div>

                {/* Pricing */}
                <div className="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
                  <div className="space-y-1">
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {t('regularPrice')}: ${tour.base_price}
                    </div>
                    <div className="text-lg font-bold text-green-600 dark:text-green-400">
                      {t('agentPrice')}: ${tour.agent_price}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-green-600 dark:text-green-400 font-medium">
                      {t('savings')}: ${tour.base_price - tour.agent_price!}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {Math.round(((tour.base_price - tour.agent_price!) / tour.base_price) * 100)}% {t('discount')}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {filteredTours.length === 0 && (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.29-1.009-5.824-2.709M15 6.291A7.962 7.962 0 0012 5c-2.34 0-4.29 1.009-5.824 2.709" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
            {t('noToursFound')}
          </h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {t('noToursDescription')}
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
          disabled={!selectedTour}
          className="bg-blue-600 hover:bg-blue-700"
        >
          {t('continue')}
        </Button>
      </div>
    </div>
  );
}
