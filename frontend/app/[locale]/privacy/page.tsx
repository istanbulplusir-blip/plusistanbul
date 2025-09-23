'use client';

import { useTranslations } from 'next-intl';
import { Shield } from 'lucide-react';
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
    />
  );
}
