'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import { useContactInfo, contactApi, ContactMessage } from '../../../lib/api/static-pages';
import { SkeletonLoader } from '../../../components/ui/SkeletonLoader';
import { Button } from '../../../components/ui/Button';
import { Input } from '../../../components/ui/Input';
import { 
  MapPin, 
  Phone, 
  Mail, 
  Clock, 
  Send,
  CheckCircle
} from 'lucide-react';
import { FaInstagram, FaTelegram, FaWhatsapp, FaFacebook, FaTwitter, FaLinkedin } from 'react-icons/fa';
import toast from 'react-hot-toast';

export default function ContactPage() {
  const t = useTranslations('contact');
  const { contactInfo, loading, error } = useContactInfo();
  const [formData, setFormData] = useState<ContactMessage>({
    full_name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.full_name || !formData.email || !formData.subject || !formData.message) {
      toast.error(t('form.validation.required'));
      return;
    }

    setIsSubmitting(true);
    
    try {
      await contactApi.sendContactMessage(formData);
      setSubmitSuccess(true);
      toast.success(t('form.success'));
      
      // Reset form
      setFormData({
        full_name: '',
        email: '',
        phone: '',
        subject: '',
        message: ''
      });
    } catch (err) {
      console.error('Error sending message:', err);
      toast.error(t('form.error'));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="section-container section-padding">
          <div className="space-y-8">
            <SkeletonLoader className="h-16 w-3/4 mx-auto" />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <SkeletonLoader className="h-96" />
              <SkeletonLoader className="h-96" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <section className="section-padding">
        <div className="section-container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-16"
          >
            <h1 className="heading-1 mb-6">{t('title')}</h1>
            <p className="body-text max-w-3xl mx-auto">
              {t('description')}
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Contact Information */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="space-y-8"
            >
              <div>
                <h2 className="heading-2 mb-8">{t('info.title')}</h2>
                
                {error ? (
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
                    <p className="text-red-600 dark:text-red-400">{error}</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Address */}
                    {contactInfo?.address && (
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                          <MapPin className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                            {t('info.address')}
                          </h3>
                          <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                            {contactInfo.address}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Phone */}
                    {contactInfo?.phone_primary && (
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                          <Phone className="w-6 h-6 text-green-600 dark:text-green-400" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                            {t('info.phone')}
                          </h3>
                          <p className="text-gray-600 dark:text-gray-300">
                            <a href={`tel:${contactInfo.phone_primary}`} className="hover:text-green-600 dark:hover:text-green-400 transition-colors">
                              {contactInfo.phone_primary}
                            </a>
                          </p>
                          {contactInfo.phone_secondary && (
                            <p className="text-gray-600 dark:text-gray-300">
                              <a href={`tel:${contactInfo.phone_secondary}`} className="hover:text-green-600 dark:hover:text-green-400 transition-colors">
                                {contactInfo.phone_secondary}
                              </a>
                            </p>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Email */}
                    {contactInfo?.email_general && (
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                          <Mail className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                            {t('info.email')}
                          </h3>
                          <p className="text-gray-600 dark:text-gray-300">
                            <a href={`mailto:${contactInfo.email_general}`} className="hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
                              {contactInfo.email_general}
                            </a>
                          </p>
                          {contactInfo.email_support && (
                            <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
                              {t('info.support')}: <a href={`mailto:${contactInfo.email_support}`} className="hover:text-purple-600 dark:hover:text-purple-400 transition-colors">
                                {contactInfo.email_support}
                              </a>
                            </p>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Working Hours */}
                    {contactInfo?.working_hours && (
                      <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-12 h-12 bg-orange-100 dark:bg-orange-900/30 rounded-lg flex items-center justify-center">
                          <Clock className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                            {t('info.hours')}
                          </h3>
                          <p className="text-gray-600 dark:text-gray-300">
                            {contactInfo.working_hours}
                          </p>
                          {contactInfo.working_days && (
                            <p className="text-gray-600 dark:text-gray-300 text-sm">
                              {contactInfo.working_days}
                            </p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Social Media */}
              {contactInfo && (
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
                    {t('info.social')}
                  </h3>
                  <div className="flex gap-4">
                    {contactInfo.instagram_url && (
                      <a
                        href={contactInfo.instagram_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-10 h-10 bg-pink-100 dark:bg-pink-900/30 rounded-lg flex items-center justify-center text-pink-600 dark:text-pink-400 hover:scale-110 transition-transform"
                      >
                        <FaInstagram className="w-5 h-5" />
                      </a>
                    )}
                    {contactInfo.telegram_url && (
                      <a
                        href={contactInfo.telegram_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center text-blue-600 dark:text-blue-400 hover:scale-110 transition-transform"
                      >
                        <FaTelegram className="w-5 h-5" />
                      </a>
                    )}
                    {contactInfo.whatsapp_number && (
                      <a
                        href={`https://wa.me/${contactInfo.whatsapp_number}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center text-green-600 dark:text-green-400 hover:scale-110 transition-transform"
                      >
                        <FaWhatsapp className="w-5 h-5" />
                      </a>
                    )}
                    {contactInfo.facebook_url && (
                      <a
                        href={contactInfo.facebook_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center text-blue-600 dark:text-blue-400 hover:scale-110 transition-transform"
                      >
                        <FaFacebook className="w-5 h-5" />
                      </a>
                    )}
                    {contactInfo.twitter_url && (
                      <a
                        href={contactInfo.twitter_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-10 h-10 bg-sky-100 dark:bg-sky-900/30 rounded-lg flex items-center justify-center text-sky-600 dark:text-sky-400 hover:scale-110 transition-transform"
                      >
                        <FaTwitter className="w-5 h-5" />
                      </a>
                    )}
                    {contactInfo.linkedin_url && (
                      <a
                        href={contactInfo.linkedin_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center text-blue-600 dark:text-blue-400 hover:scale-110 transition-transform"
                      >
                        <FaLinkedin className="w-5 h-5" />
                      </a>
                    )}
                  </div>
                </div>
              )}
            </motion.div>

            {/* Contact Form */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="card p-8"
            >
              <h2 className="heading-2 mb-8">{t('form.title')}</h2>

              {submitSuccess ? (
                <div className="text-center py-12">
                  <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                    {t('form.successTitle')}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 mb-6">
                    {t('form.successMessage')}
                  </p>
                  <Button onClick={() => setSubmitSuccess(false)}>
                    {t('form.sendAnother')}
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {t('form.fullName')} <span className="text-red-500">*</span>
                      </label>
                      <Input
                        type="text"
                        name="full_name"
                        value={formData.full_name}
                        onChange={handleInputChange}
                        required
                        placeholder={t('form.fullNamePlaceholder')}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        {t('form.email')} <span className="text-red-500">*</span>
                      </label>
                      <Input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        required
                        placeholder={t('form.emailPlaceholder')}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      {t('form.phone')}
                    </label>
                    <Input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      placeholder={t('form.phonePlaceholder')}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      {t('form.subject')} <span className="text-red-500">*</span>
                    </label>
                    <Input
                      type="text"
                      name="subject"
                      value={formData.subject}
                      onChange={handleInputChange}
                      required
                      placeholder={t('form.subjectPlaceholder')}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      {t('form.message')} <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      name="message"
                      value={formData.message}
                      onChange={handleInputChange}
                      required
                      rows={6}
                      placeholder={t('form.messagePlaceholder')}
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none"
                    />
                  </div>

                  <Button
                    type="submit"
                    size="lg"
                    disabled={isSubmitting}
                    className="w-full"
                  >
                    {isSubmitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        {t('form.sending')}
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4 mr-2" />
                        {t('form.send')}
                      </>
                    )}
                  </Button>
                </form>
              )}
            </motion.div>
          </div>
        </div>
      </section>
    </div>
  );
}
