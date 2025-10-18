/**
 * Custom hook for FAQ data management.
 */

import { useState, useEffect, useCallback } from 'react';
import { FAQ } from '../types/faq';
import { faqApi } from '../lib/api/faq';

interface UseFAQRETURN {
  faqs: FAQ[];
  loading: boolean;
  error: string | null;
  categories: string[];
  selectedCategory: string | null;
  setSelectedCategory: (category: string | null) => void;
  refreshFAQs: () => Promise<void>;
}

export const useFAQ = (): UseFAQRETURN => {
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const fetchFAQs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [faqsData, categoriesData] = await Promise.all([
        faqApi.getActiveFAQs(),
        faqApi.getFAQCategories()
      ]);
      
      setFaqs(faqsData);
      // Remove duplicates from categories to prevent duplicate keys
      setCategories([...new Set(categoriesData.categories)]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch FAQs');
      console.error('Error fetching FAQs:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchFAQsByCategory = useCallback(async (category: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const faqsData = await faqApi.getFAQsByCategory(category);
      setFaqs(faqsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch FAQs by category');
      console.error('Error fetching FAQs by category:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshFAQs = useCallback(async () => {
    if (selectedCategory) {
      await fetchFAQsByCategory(selectedCategory);
    } else {
      await fetchFAQs();
    }
  }, [selectedCategory, fetchFAQs, fetchFAQsByCategory]);

  // Effect to fetch FAQs when component mounts or category changes
  useEffect(() => {
    if (selectedCategory) {
      fetchFAQsByCategory(selectedCategory);
    } else {
      fetchFAQs();
    }
  }, [selectedCategory, fetchFAQs, fetchFAQsByCategory]);

  return {
    faqs,
    loading,
    error,
    categories,
    selectedCategory,
    setSelectedCategory,
    refreshFAQs
  };
};
