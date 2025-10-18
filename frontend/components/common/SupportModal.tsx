'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, MessageCircle, Phone, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { useTranslations, useLocale } from 'next-intl';

interface SupportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ContactInfo {
  whatsapp_number: string;
  phone_primary: string;
  email_support: string;
  address: string;
  working_hours: string;
  working_days: string;
  instagram_url: string;
  telegram_url: string;
}

interface SupportFAQ {
  id: string;
  category: string;
  category_display: string;
  question: string;
  whatsapp_message: string;
  order: number;
  is_active: boolean;
  whatsapp_link?: string;
}

// Fallback contact information when backend is unavailable
const FALLBACK_CONTACT_INFO: ContactInfo = {
  whatsapp_number: '+90 555 123 4567',
  phone_primary: '+90 212 555 0123',
  email_support: 'support@peykantravelistanbul.com',
  address: 'Istanbul, Turkey',
  working_hours: '9:00 AM - 6:00 PM',
  working_days: 'Monday - Friday',
  instagram_url: 'https://instagram.com/peykantravel',
  telegram_url: 'https://t.me/peykansupport'
};

export default function SupportModal({ isOpen, onClose }: SupportModalProps) {
  const t = useTranslations('support');
  const [contactInfo, setContactInfo] = useState<ContactInfo | null>(null);
  const [whatsappInfo, setWhatsappInfo] = useState<{phone: string; whatsapp_url: string} | null>(null);
  const [supportFAQs, setSupportFAQs] = useState<SupportFAQ[]>([]);
  const [userMessage, setUserMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingFAQs, setIsLoadingFAQs] = useState(false);
  const [error, setError] = useState('');
  const [useFallback, setUseFallback] = useState(false);
  const [selectedFAQ, setSelectedFAQ] = useState<SupportFAQ | null>(null);
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['booking']));
  const locale = useLocale();

  const loadContactInfo = useCallback(async () => {
    try {
      setIsLoading(true);
      setError('');
      setUseFallback(false);
      
      const response = await fetch('/api/v1/shared/contact-info');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // More flexible validation - just check if we have some data
      if (data && typeof data === 'object') {
        setContactInfo(data);
      } else {
        throw new Error('Invalid contact information received');
      }
    } catch (err) {
      console.error('Error loading contact info:', err);
      setError(t('errorLoadingContactInfo'));
      setUseFallback(true);
      // Use fallback data when backend fails
      setContactInfo(FALLBACK_CONTACT_INFO);
    } finally {
      setIsLoading(false);
    }
  }, [t]);

  const loadWhatsAppInfo = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/shared/whatsapp-info/');
      if (response.ok) {
        const data = await response.json();
        setWhatsappInfo({
          phone: data.phone,
          whatsapp_url: data.whatsapp_url
        });
        console.log('✅ WhatsApp info loaded successfully:', data);
      } else {
        console.warn('⚠️ Failed to load WhatsApp info, using fallback');
      }
    } catch (err) {
      console.error('❌ Error loading WhatsApp info:', err);
    }
  }, []);

  // Load contact info when modal opens
  useEffect(() => {
    if (isOpen) {
      loadContactInfo();
      loadWhatsAppInfo();
      loadSupportFAQs();
    }
  }, [isOpen, loadContactInfo, loadWhatsAppInfo]);

  const loadSupportFAQs = async () => {
    try {
      setIsLoadingFAQs(true);
      
      const response = await fetch('/api/v1/shared/support-faqs');
      if (response.ok) {
        const data = await response.json();
        // Ensure data is an array
        if (Array.isArray(data)) {
          setSupportFAQs(data);
        } else if (data && data.results && Array.isArray(data.results)) {
          // Handle paginated response
          setSupportFAQs(data.results);
        } else {
          console.warn('Unexpected FAQ data format:', data);
          setSupportFAQs([]);
        }
      } else {
        console.warn('Failed to load support FAQs:', response.status);
        setSupportFAQs([]);
      }
    } catch (err) {
      console.error('Error loading support FAQs:', err);
      setSupportFAQs([]);
    } finally {
      setIsLoadingFAQs(false);
    }
  };

  const handleFAQSelect = (faq: SupportFAQ) => {
    setSelectedFAQ(faq);
    setUserMessage(faq.whatsapp_message);
  };

  const handleCategoryToggle = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const handleSendMessage = () => {
    if (!userMessage.trim()) return;
    
    // Use centralized WhatsApp info if available, otherwise fallback to contact info
    let whatsappUrl = null;
    
    if (whatsappInfo?.whatsapp_url) {
      // Use centralized WhatsApp service
      const encodedMessage = encodeURIComponent(userMessage);
      whatsappUrl = `${whatsappInfo.whatsapp_url}?text=${encodedMessage}`;
    } else if (contactInfo?.whatsapp_number) {
      // Fallback to contact info
      const formattedPhone = contactInfo.whatsapp_number.replace(/\s/g, '');
      const encodedMessage = encodeURIComponent(userMessage);
      whatsappUrl = `https://wa.me/${formattedPhone}?text=${encodedMessage}`;
    } else {
      // Final fallback
      const formattedPhone = FALLBACK_CONTACT_INFO.whatsapp_number.replace(/\s/g, '');
      const encodedMessage = encodeURIComponent(userMessage);
      whatsappUrl = `https://wa.me/${formattedPhone}?text=${encodedMessage}`;
    }
    
    if (whatsappUrl) {
      window.open(whatsappUrl, '_blank');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatPhoneNumber = (phone: string | undefined) => {
    if (!phone) return '';
    return phone.replace(/\D/g, '');
  };



  // Get current contact info (backend data or fallback)
  const currentContactInfo = contactInfo || FALLBACK_CONTACT_INFO;

  // RTL/LTR logic - Only for FAQ responses and quick message section
  const isRTL = locale === 'fa';
  const faqTextAlignment = isRTL ? 'text-right' : 'text-left';
  const messageTextAlignment = isRTL ? 'text-right' : 'text-left';

  // Group FAQs by category
  const faqsByCategory = Array.isArray(supportFAQs) ? supportFAQs.reduce((acc, faq) => {
    if (!acc[faq.category]) {
      acc[faq.category] = [];
    }
    acc[faq.category].push(faq);
    return acc;
  }, {} as Record<string, SupportFAQ[]>) : {};

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'booking':
        return '📅';
      case 'cancellation':
        return '❌';
      case 'transfer':
        return '🚗';
      case 'general':
        return '❓';
      default:
        return '❓';
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div 
          className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-end justify-end z-50 p-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          {/* Modern Chat Popup */}
          <motion.div 
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 w-full max-w-md h-[70vh] flex flex-col"
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
            {/* Header */}
            <div className="relative p-4 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-t-2xl">
              <motion.button
                onClick={onClose}
                className={`absolute top-3 w-8 h-8 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center transition-all duration-300 ${isRTL ? 'left-3' : 'right-3'}`}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <X className="w-4 h-4 text-white" />
              </motion.button>
              
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <MessageCircle className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold">
                    {t('title')}
                  </h3>
                  <p className="text-sm text-white/90">
                    {t('subtitle')}
                  </p>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="px-4 pt-4 pb-4 space-y-1 flex-1 overflow-y-auto">
              {/* Fallback Data Notice */}
              {useFallback && (
                <motion.div 
                  className="p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-xl"
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.2 }}
                >
                  <p className="text-sm text-yellow-700 dark:text-yellow-300">
                    {t('usingFallbackData')}
                  </p>
                </motion.div>
              )}

              {/* Support FAQs Section */}
              <motion.div 
                className="space-y-3"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    {t('quickQuestions')}
                  </h4>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">
                    {t('quickQuestionsDesc')}
                  </p>
                </div>

                {isLoadingFAQs ? (
                  <div className="flex items-center justify-center py-4">
                    <div className="w-5 h-5 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
                    <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                      {t('loadingFAQs')}
                    </span>
                  </div>
                ) : Array.isArray(supportFAQs) && supportFAQs.length > 0 ? (
                  <div className="space-y-2">
                    {Object.entries(faqsByCategory || {}).map(([category, faqs]) => (
                      <div key={category} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                        <button
                          onClick={() => handleCategoryToggle(category)}
                          className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 flex items-center justify-between text-left transition-colors"
                        >
                          <div className="flex items-center gap-2">
                            <span className="text-lg">{getCategoryIcon(category)}</span>
                            <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                              {t(`categories.${category}`)}
                            </span>
                          </div>
                          {expandedCategories.has(category) ? (
                            <ChevronUp className="w-4 h-4 text-gray-500" />
                          ) : (
                            <ChevronDown className="w-4 h-4 text-gray-500" />
                          )}
                        </button>
                        
                        <AnimatePresence>
                          {expandedCategories.has(category) && (
                            <motion.div
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: 'auto' }}
                              exit={{ opacity: 0, height: 0 }}
                              transition={{ duration: 0.2 }}
                              className="overflow-hidden"
                            >
                              <div className="p-2 space-y-1">
                                {Array.isArray(faqs) && faqs.map((faq) => (
                                  <button
                                    key={faq.id}
                                    onClick={() => handleFAQSelect(faq)}
                                    className={`w-full p-2 rounded text-sm transition-colors ${faqTextAlignment} ${
                                      selectedFAQ?.id === faq.id
                                        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200'
                                        : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                                    }`}
                                  >
                                    {faq.question}
                                  </button>
                                ))}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4 text-sm text-gray-500 dark:text-gray-400">
                    {t('noFAQs')}
                  </div>
                )}
              </motion.div>

              {/* Contact Information Cards */}
              <motion.div 
                className="grid grid-cols-2 gap-3"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.2 }}
              >
                {/* Phone Card */}
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl">
                  <div className={`flex items-center justify-between ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}>
                    <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}>
                      <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                        <Phone className="w-3 h-3 text-white" />
                      </div>
                      <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
                        {t('phone')}
                      </span>
                    </div>
                    <a
                      href={`tel:${formatPhoneNumber(currentContactInfo.phone_primary)}`}
                      className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
                    >
                      {t('call')}
                    </a>
                  </div>
                  <p className={`text-sm text-blue-700 dark:text-blue-300 mt-1 ${faqTextAlignment}`}>
                    {currentContactInfo.phone_primary}
                  </p>
                </div>

                {/* Working Hours Card */}
                <div className="p-3 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-700 rounded-xl">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center">
                      <Clock className="w-3 h-3 text-white" />
                    </div>
                    <span className="text-sm font-medium text-orange-800 dark:text-orange-200">
                      {t('workingHours')}
                    </span>
                  </div>
                  <p className="text-sm text-orange-700 dark:text-orange-300 mt-1">
                    {currentContactInfo.working_days}
                  </p>
                  <p className="text-sm text-orange-700 dark:text-orange-300">
                    {currentContactInfo.working_hours}
                  </p>
                </div>
              </motion.div>

              {/* Error Message */}
              <AnimatePresence>
                {error && (
                  <motion.div 
                    className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-xl"
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                  >
                    <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Quick Message Section */}
              <motion.div 
                className="space-y-3"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.3 }}
              >
                <div className={messageTextAlignment}>
                  <label htmlFor="message" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {selectedFAQ ? t('customizeMessage') : t('quickMessage')}
                  </label>
                  <textarea
                    id="message"
                    value={userMessage}
                    onChange={(e) => setUserMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={selectedFAQ ? selectedFAQ.whatsapp_message : t('messagePlaceholder')}
                    className={`w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 resize-none transition-all duration-300 ${messageTextAlignment}`}
                    rows={3}
                  />
                </div>



                {/* WhatsApp Button */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3 }}
                >
                  <button
                    onClick={() => {
                      // Use FALLBACK_CONTACT_INFO if backend doesn't have whatsapp_number
                      const currentContactInfo = (contactInfo && contactInfo.whatsapp_number) ? contactInfo : FALLBACK_CONTACT_INFO;
                      
                      if (currentContactInfo?.whatsapp_number) {
                        const formattedPhone = currentContactInfo.whatsapp_number.replace(/\s/g, '');
                        const messageToSend = userMessage.trim() || t('defaultMessage');
                        const encodedMessage = encodeURIComponent(messageToSend);
                        const link = `https://wa.me/${formattedPhone}?text=${encodedMessage}`;
                        window.open(link, '_blank');
                      }
                    }}
                    className="w-full h-11 bg-green-500 hover:bg-green-600 text-white rounded-xl transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
                  >
                    <MessageCircle className="w-4 h-4" />
                    {t('openWhatsApp')}
                  </button>
                </motion.div>
              </motion.div>

              {/* Loading State */}
              {isLoading && (
                <motion.div 
                  className="flex items-center justify-center py-4"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <div className="w-6 h-6 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
                </motion.div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
