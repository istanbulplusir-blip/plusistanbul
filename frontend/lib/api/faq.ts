/**
 * FAQ API service for Peykan Tourism Platform.
 */

import { apiClient } from './client';
import { FAQ, FAQListResponse, FAQCategoryResponse } from '../../types/faq';

const FAQ_API_BASE = '/shared/faqs/';

export const faqApi = {
  /**
   * Get all FAQs with optional filtering and pagination.
   */
  async getFAQs(params?: {
    category?: string;
    page?: number;
    page_size?: number;
    ordering?: string;
  }): Promise<FAQListResponse> {
    const response = await apiClient.get(FAQ_API_BASE, { params });
    return (response as { data: FAQListResponse }).data;
  },

  /**
   * Get FAQ by ID.
   */
  async getFAQById(id: string): Promise<FAQ> {
    const response = await apiClient.get(`${FAQ_API_BASE}${id}/`);
    return (response as { data: FAQ }).data;
  },

  /**
   * Get FAQ by slug.
   */
  async getFAQBySlug(slug: string): Promise<FAQ> {
    const response = await apiClient.get(`${FAQ_API_BASE}${slug}/`);
    return (response as { data: FAQ }).data;
  },

  /**
   * Get available FAQ categories.
   */
  async getFAQCategories(): Promise<FAQCategoryResponse> {
    const response = await apiClient.get(`${FAQ_API_BASE}categories/`);
    return (response as { data: FAQCategoryResponse }).data;
  },

  /**
   * Get FAQs by category.
   */
  async getFAQsByCategory(category: string): Promise<FAQ[]> {
    const response = await apiClient.get(`${FAQ_API_BASE}by_category/`, {
      params: { category }
    });
    return (response as { data: FAQ[] }).data;
  },

  /**
   * Get active FAQs for public display.
   */
  async getActiveFAQs(): Promise<FAQ[]> {
    const response = await apiClient.get(FAQ_API_BASE, {
      params: { is_active: true, ordering: 'order,created_at' }
    });
    return (response as { data: FAQListResponse }).data.results || (response as { data: FAQListResponse }).data;
  }
};
