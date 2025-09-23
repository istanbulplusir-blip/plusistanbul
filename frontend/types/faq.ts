/**
 * FAQ types for Peykan Tourism Platform.
 */

export interface FAQ {
  id: string;
  slug: string;
  question: string;
  answer: string;
  category: string;
  order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FAQListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: FAQ[];
}

export interface FAQCategoryResponse {
  categories: string[];
}

export interface FAQApiResponse {
  success: boolean;
  message?: string;
  error?: string;
  data?: FAQ | FAQ[] | FAQListResponse;
}
