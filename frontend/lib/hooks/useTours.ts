import { useState, useEffect } from 'react';

export interface Tour {
  id: string;
  slug: string;
  title: string;
  description?: string;
  image?: string;
  image_url?: string;
  location?: string;
  price?: string;
  starting_price?: number | null;
  currency?: string;
  duration_hours?: number;
  min_participants?: number;
  max_participants?: number;
  is_active?: boolean;
  created_at?: string;
  rating?: number;
  category?: {
    id: string;
    name: string;
  };
  next_schedule_date?: string | null;
  next_schedule_capacity_total?: number;
  next_schedule_capacity_available?: number;
  has_upcoming?: boolean;
  type?: 'tour';
}

export interface TourListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Tour[];
}

// Hook for tours list
export const useTours = (params?: {
  limit?: number;
  search?: string;
  category?: string;
  location?: string;
  price_min?: number;
  price_max?: number;
  duration_min?: number;
  duration_max?: number;
  date?: string;
  participants?: number;
  language?: string;
  page?: number;
  page_size?: number;
}) => {
  const [tours, setTours] = useState<Tour[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTours = async () => {
      try {
        setIsLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';
        
        // Build query parameters
        const queryParams = new URLSearchParams();
        if (params?.limit) queryParams.append('page_size', params.limit.toString());
        if (params?.search) queryParams.append('search', params.search);
        if (params?.category) queryParams.append('category', params.category);
        if (params?.location) queryParams.append('location', params.location);
        if (params?.price_min) queryParams.append('price_min', params.price_min.toString());
        if (params?.price_max) queryParams.append('price_max', params.price_max.toString());
        if (params?.duration_min) queryParams.append('duration_min', params.duration_min.toString());
        if (params?.duration_max) queryParams.append('duration_max', params.duration_max.toString());
        if (params?.date) queryParams.append('date', params.date);
        if (params?.participants) queryParams.append('participants', params.participants.toString());
        if (params?.language) queryParams.append('language', params.language);
        if (params?.page) queryParams.append('page', params.page.toString());
        if (params?.page_size) queryParams.append('page_size', params.page_size.toString());

        const response = await fetch(`${apiUrl}/tours/tours/?${queryParams.toString()}`, { 
          credentials: 'include' 
        });
        
        if (response.ok) {
          const data = await response.json();
          const raw = (Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []) as Tour[];
          
          // Normalize tours data
          const normalized: Tour[] = raw.map((t: Tour) => ({
            id: t.id,
            slug: t.slug,
            title: t.title || 'بدون عنوان',
            description: t.description || '',
            image: t.image || '',
            image_url: t.image_url || t.image || '/images/tour-image.jpg',
            location: t.location || '',
            price: String(t.starting_price ?? t.price ?? ''),
            starting_price: t.starting_price ?? null,
            currency: t.currency || 'EUR',
            duration_hours: t.duration_hours || 0,
            min_participants: t.min_participants || 1,
            max_participants: t.max_participants || 0,
            is_active: t.is_active ?? true,
            created_at: t.created_at || '',
            rating: t.rating || 0,
            category: t.category || { id: '', name: '' },
            next_schedule_date: t.next_schedule_date ?? null,
            next_schedule_capacity_total: t.next_schedule_capacity_total ?? 0,
            next_schedule_capacity_available: t.next_schedule_capacity_available ?? 0,
            has_upcoming: t.has_upcoming ?? false,
            type: 'tour' as const
          }));
          
          setTours(normalized);
        } else {
          setError('Failed to fetch tours');
        }
      } catch (err) {
        console.error('Error fetching tours:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTours();
  }, [params]);

  return { tours, isLoading, error };
};

// Hook for tour detail
export const useTourDetail = (slug: string) => {
  const [tour, setTour] = useState<Tour | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTourDetail = async () => {
      if (!slug) return;
      
      try {
        setIsLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';
        
        const response = await fetch(`${apiUrl}/tours/tours/${slug}/`, { 
          credentials: 'include' 
        });
        
        if (response.ok) {
          const data = await response.json();
          setTour(data);
        } else {
          setError('Failed to fetch tour details');
        }
      } catch (err) {
        console.error('Error fetching tour detail:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTourDetail();
  }, [slug]);

  return { tour, isLoading, error };
};

// Hook for tour categories
export const useTourCategories = () => {
  const [categories, setCategories] = useState<Array<{ id: string; name: string }>>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setIsLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';
        
        const response = await fetch(`${apiUrl}/tours/categories/`, { 
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
          setError('Failed to fetch tour categories');
        }
      } catch (err) {
        console.error('Error fetching tour categories:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCategories();
  }, []);

  return { categories, isLoading, error };
};
