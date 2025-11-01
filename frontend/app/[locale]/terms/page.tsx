'use client';

import { useTranslations } from 'next-intl';
import { Scale, FileCheck, Briefcase, Calendar, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';
import StaticPageLayout from '../../../components/common/StaticPageLayout';

export default function TermsPage() {
  const t = useTranslations('terms');

  return (
    <StaticPageLayout
      title={t('title')}
      description={t('description')}
      icon={Scale}
      showCTA={true}
      ctaTitle={t('cta.title')}
      ctaDescription={t('cta.description')}
      ctaButtonText={t('cta.button')}
      ctaButtonLink="/contact"
    >
      <div className="prose prose-lg max-w-none">
        {/* Introduction */}
        <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-8 text-lg">
          {t('content.intro')}
        </p>

        {/* Acceptance Section */}
        <div className="mb-10">
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
              <FileCheck className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {t('content.acceptance.title')}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {t('content.acceptance.description')}
              </p>
            </div>
          </div>
        </div>

        {/* Services Section */}
        <div className="mb-10">
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
              <Briefcase className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {t('content.services.title')}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {t('content.services.description')}
              </p>
            </div>
          </div>
        </div>

        {/* Booking Policy Section */}
        <div className="mb-10">
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {t('content.bookingPolicy.title')}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {t('content.bookingPolicy.description')}
              </p>
            </div>
          </div>
        </div>

        {/* Cancellation Policy Section */}
        <div className="mb-10">
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center">
              <XCircle className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {t('content.cancellationPolicy.title')}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {t('content.cancellationPolicy.description')}
              </p>
            </div>
          </div>
        </div>

        {/* Liability Section */}
        <div className="mb-10">
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {t('content.liability.title')}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {t('content.liability.description')}
              </p>
            </div>
          </div>
        </div>

        {/* Changes Section */}
        <div className="mb-6">
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex items-center justify-center">
              <RefreshCw className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {t('content.changes.title')}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {t('content.changes.description')}
              </p>
            </div>
          </div>
        </div>
      </div>
    </StaticPageLayout>
  );
}
