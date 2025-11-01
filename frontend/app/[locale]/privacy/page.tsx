'use client';

import { useTranslations } from 'next-intl';
import { Shield, Database, Lock, UserCheck, Mail } from 'lucide-react';
import StaticPageLayout from '../../../components/common/StaticPageLayout';

export default function PrivacyPage() {
  const t = useTranslations('privacy');

  return (
    <StaticPageLayout
      title={t('title')}
      description={t('description')}
      icon={Shield}
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

        {/* Data Collection Section */}
        <div className="mb-10">
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
              <Database className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {t('content.dataCollection.title')}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {t('content.dataCollection.description')}
              </p>
            </div>
          </div>
        </div>

        {/* Data Usage Section */}
        <div className="mb-10">
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {t('content.dataUsage.title')}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {t('content.dataUsage.description')}
              </p>
            </div>
          </div>
        </div>

        {/* Data Security Section */}
        <div className="mb-10">
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
              <Lock className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {t('content.dataSecurity.title')}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {t('content.dataSecurity.description')}
              </p>
            </div>
          </div>
        </div>

        {/* User Rights Section */}
        <div className="mb-10">
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center">
              <UserCheck className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {t('content.userRights.title')}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {t('content.userRights.description')}
              </p>
            </div>
          </div>
        </div>

        {/* Contact Section */}
        <div className="mb-6">
          <div className="flex items-start gap-4 mb-4">
            <div className="flex-shrink-0 w-12 h-12 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center">
              <Mail className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                {t('content.contact.title')}
              </h2>
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {t('content.contact.description')}
              </p>
            </div>
          </div>
        </div>
      </div>
    </StaticPageLayout>
  );
}
