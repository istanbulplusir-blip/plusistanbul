'use client';

import { useTranslations } from 'next-intl';
import { Scale } from 'lucide-react';
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
    />
  );
}
