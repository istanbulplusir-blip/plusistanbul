'use client';

import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import Image from 'next/image';
import { useStaticPage } from '../../../lib/api/static-pages';
import { SkeletonLoader } from '../../../components/ui/SkeletonLoader';
import { Button } from '../../../components/ui/Button';
import { Heart, Users, Award, Globe } from 'lucide-react';
import Link from 'next/link';

export default function AboutPage() {
  const t = useTranslations('about');
  const { page, loading, error } = useStaticPage('about');

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="section-container section-padding">
          <div className="space-y-8">
            <SkeletonLoader className="h-16 w-3/4 mx-auto" />
            <SkeletonLoader className="h-64 w-full" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <SkeletonLoader className="h-48" />
              <SkeletonLoader className="h-48" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="section-container section-padding">
          <div className="text-center">
            <h1 className="heading-1 mb-8">{t('title')}</h1>
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
              <p className="text-red-600 dark:text-red-400">{error}</p>
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
            <h1 className="heading-1 mb-6">
              {page?.title || t('title')}
            </h1>
            {page?.excerpt && (
              <p className="body-text max-w-3xl mx-auto">
                {page.excerpt}
              </p>
            )}
          </motion.div>

          {/* Hero Image */}
          {page?.image_url && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative h-64 sm:h-80 lg:h-96 rounded-2xl overflow-hidden shadow-2xl mb-16"
            >
              <Image
                src={page.image_url}
                alt={page.title}
                fill
                className="object-cover"
                quality={85}
                priority
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
            </motion.div>
          )}
        </div>
      </section>

      {/* Main Content */}
      {page?.content && (
        <section className="section-padding">
          <div className="section-container">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="prose prose-lg dark:prose-invert max-w-4xl mx-auto"
            >
              <div 
                dangerouslySetInnerHTML={{ __html: page.content }}
                className="leading-relaxed"
              />
            </motion.div>
          </div>
        </section>
      )}

      {/* Values Section */}
      <section className="section-padding bg-white/50 dark:bg-gray-800/50">
        <div className="section-container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-center mb-12"
          >
            <h2 className="heading-2 mb-4">{t('values.title')}</h2>
            <p className="body-text max-w-2xl mx-auto">{t('values.description')}</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: Heart,
                title: t('values.passion.title'),
                description: t('values.passion.description'),
                color: 'text-red-500'
              },
              {
                icon: Users,
                title: t('values.community.title'),
                description: t('values.community.description'),
                color: 'text-blue-500'
              },
              {
                icon: Award,
                title: t('values.excellence.title'),
                description: t('values.excellence.description'),
                color: 'text-yellow-500'
              },
              {
                icon: Globe,
                title: t('values.global.title'),
                description: t('values.global.description'),
                color: 'text-green-500'
              }
            ].map((value, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.5 + index * 0.1 }}
                className="card p-6 text-center hover-lift"
              >
                <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-700 mb-4 ${value.color}`}>
                  <value.icon className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-semibold mb-3 text-gray-900 dark:text-white">
                  {value.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  {value.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Statistics Section */}
      <section className="section-padding">
        <div className="section-container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="text-center mb-12"
          >
            <h2 className="heading-2 mb-4">{t('stats.title')}</h2>
            <p className="body-text max-w-2xl mx-auto">{t('stats.description')}</p>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { number: '10,000+', label: t('stats.customers') },
              { number: '500+', label: t('stats.tours') },
              { number: '50+', label: t('stats.destinations') },
              { number: '5', label: t('stats.years') }
            ].map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.7 + index * 0.1 }}
                className="text-center"
              >
                <div className="text-4xl lg:text-5xl font-bold text-primary mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600 dark:text-gray-300 font-medium">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section-padding bg-gradient-to-r from-blue-600 to-teal-600">
        <div className="section-container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="text-center text-white"
          >
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">
              {t('cta.title')}
            </h2>
            <p className="text-xl mb-8 max-w-2xl mx-auto text-blue-100">
              {t('cta.description')}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/tours">
                <Button 
                  variant="outline" 
                  size="lg"
                  className="bg-white/20 border-white/30 text-white hover:bg-white/30"
                >
                  {t('cta.exploreTours')}
                </Button>
              </Link>
              <Link href="/contact">
                <Button 
                  variant="secondary" 
                  size="lg"
                  className="bg-white text-blue-600 hover:bg-blue-50"
                >
                  {t('cta.contactUs')}
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
