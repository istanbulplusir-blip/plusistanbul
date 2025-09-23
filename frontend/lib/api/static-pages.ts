/**
 * API functions for static pages (About, Terms, Privacy, FAQ, Contact)
 */

import { apiClient } from './client';

// Types
export interface StaticPage {
  id: string;
  page_type: 'about' | 'terms' | 'privacy' | 'faq' | 'contact';
  slug: string;
  title: string;
  content: string;
  excerpt?: string;
  image_url?: string;
  meta_description?: string;
  meta_keywords?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ContactInfo {
  id: string;
  company_name: string;
  address: string;
  phone_primary: string;
  phone_secondary?: string;
  email_general: string;
  email_support?: string;
  email_sales?: string;
  working_hours: string;
  working_days: string;
  latitude?: number;
  longitude?: number;
  instagram_url?: string;
  telegram_url?: string;
  whatsapp_number?: string;
  facebook_url?: string;
  twitter_url?: string;
  linkedin_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ContactMessage {
  full_name: string;
  email: string;
  phone?: string;
  subject: string;
  message: string;
}

export interface ContactMessageResponse {
  message: string;
  id: string;
}

/**
 * Static Pages API
 */
export const staticPagesApi = {
  /**
   * Get a static page by type
   */
  async getPageByType(pageType: string): Promise<StaticPage> {
    const response = await apiClient.get(`/shared/pages/by_type/?type=${pageType}`) as { data: StaticPage };
    return response.data;
  },

  /**
   * Get all static pages
   */
  async getAllPages(): Promise<StaticPage[]> {
    const response = await apiClient.get('/shared/pages/') as { data: { results?: StaticPage[] } | StaticPage[] };
    return (response.data as { results?: StaticPage[] }).results || response.data as StaticPage[];
  }
};

/**
 * Contact API
 */
export const contactApi = {
  /**
   * Get contact information
   */
  async getContactInfo(): Promise<ContactInfo> {
    const response = await apiClient.get('/shared/contact-info/') as { data: ContactInfo };
    return response.data;
  },

  /**
   * Send contact message
   */
  async sendContactMessage(messageData: ContactMessage): Promise<ContactMessageResponse> {
    const response = await apiClient.post('/shared/contact-messages/', messageData) as { data: ContactMessageResponse };
    return response.data;
  }
};

/**
 * Custom hooks for static pages
 */
import { useState, useEffect } from 'react';

export const useStaticPage = (pageType: string) => {
  const [page, setPage] = useState<StaticPage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPage = async () => {
      try {
        setLoading(true);
        setError(null);
        const pageData = await staticPagesApi.getPageByType(pageType);
        setPage(pageData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch page');
        console.error(`Error fetching ${pageType} page:`, err);
      } finally {
        setLoading(false);
      }
    };

    if (pageType) {
      fetchPage();
    }
  }, [pageType]);

  return { page, loading, error };
};

export const useContactInfo = () => {
  const [contactInfo, setContactInfo] = useState<ContactInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchContactInfo = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await contactApi.getContactInfo();
        setContactInfo(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch contact info');
        console.error('Error fetching contact info:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchContactInfo();
  }, []);

  return { contactInfo, loading, error };
};
