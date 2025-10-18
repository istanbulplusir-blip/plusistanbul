/**
 * SWR hooks for Event data management.
 */

import { useState, useEffect } from 'react';
import { mutate } from 'swr';

export interface Event {
  id: string;
  slug: string;
  title: string;
  short_description?: string;
  image?: string;
  image_url?: string;
  category?: {
    id: string;
    name: string;
  };
  venue?: {
    id: string;
    name: string;
  };
  artists?: Array<{
    id: string;
    name: string;
  }>;
  average_rating?: number;
  review_count?: number;
  min_price?: number;
  max_price?: number;
  is_active: boolean;
  created_at: string;
}

// Hook for events list
export const useEvents = (params?: {
  limit?: number;
  search?: string;
  category?: string;
  venue?: string;
  price_min?: number;
  price_max?: number;
  date_from?: string;
  date_to?: string;
  language?: string;
  page?: number;
  page_size?: number;
}) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setIsLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';
        
        // Build query parameters
        const queryParams = new URLSearchParams();
        if (params?.limit) queryParams.append('page_size', params.limit.toString());
        if (params?.search) queryParams.append('search', params.search);
        if (params?.category) queryParams.append('category', params.category);
        if (params?.venue) queryParams.append('venue', params.venue);
        if (params?.price_min) queryParams.append('price_min', params.price_min.toString());
        if (params?.price_max) queryParams.append('price_max', params.price_max.toString());
        if (params?.date_from) queryParams.append('date_from', params.date_from);
        if (params?.date_to) queryParams.append('date_to', params.date_to);
        if (params?.language) queryParams.append('language', params.language);
        if (params?.page) queryParams.append('page', params.page.toString());
        if (params?.page_size) queryParams.append('page_size', params.page_size.toString());

        const response = await fetch(`${apiUrl}/events/events/?${queryParams.toString()}`, { 
          credentials: 'include' 
        });
        
        if (response.ok) {
          const data = await response.json();
          const raw = (Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []) as Event[];
          
          // Normalize events data
          const normalized: Event[] = raw.map((e: Event) => ({
            id: e.id,
            slug: e.slug,
            title: e.title || 'بدون عنوان',
            short_description: e.short_description || '',
            image: e.image || '',
            image_url: e.image_url || e.image || '/images/event-hero.jpg',
            category: e.category || { id: '', name: '' },
            venue: e.venue || { id: '', name: '' },
            artists: e.artists || [],
            average_rating: e.average_rating || 0,
            review_count: e.review_count || 0,
            min_price: e.min_price || 0,
            max_price: e.max_price || 0,
            is_active: e.is_active ?? true,
            created_at: e.created_at || ''
          }));
          
          setEvents(normalized);
        } else {
          setError('Failed to fetch events');
        }
      } catch (err) {
        console.error('Error fetching events:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvents();
  }, [params]);

  return { events, isLoading, error };
};

// Hook for event detail
export const useEventDetail = (slug: string) => {
  const [event, setEvent] = useState<Event | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEventDetail = async () => {
      if (!slug) return;
      
      try {
        setIsLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';
        
        const response = await fetch(`${apiUrl}/events/events/${slug}/`, { 
          credentials: 'include' 
        });
        
        if (response.ok) {
          const data = await response.json();
          setEvent(data);
        } else {
          setError('Failed to fetch event details');
        }
      } catch (err) {
        console.error('Error fetching event detail:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchEventDetail();
  }, [slug]);

  return { event, isLoading, error };
};

// Hook for event categories
export const useEventCategories = () => {
  const [categories, setCategories] = useState<Array<{ id: string; name: string }>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setIsLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';
        
        const response = await fetch(`${apiUrl}/events/categories/`, { 
          credentials: 'include' 
        });
        
        if (response.ok) {
          const data = await response.json();
          const raw = (Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []);
          
          const normalized = raw.map((cat: { id?: string; name?: string }) => ({
            id: cat.id || '',
            name: cat.name || ''
          }));
          
          setCategories(normalized);
        } else {
          setError('Failed to fetch event categories');
        }
      } catch (err) {
        console.error('Error fetching event categories:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategories();
  }, []);

  return { categories, isLoading, error };
};

// Mutate functions for manual cache updates
export const mutateEvents = () => mutate('events');
export const mutateEvent = (eventId: string) => mutate(['event', eventId]);
export const mutateEventSearch = () => mutate('event-search'); 