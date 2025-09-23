'use client';

import { ReactNode } from 'react';
import { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Button } from '../ui/Button';

interface StaticPageLayoutProps {
  title: string;
  description: string;
  icon: LucideIcon;
  showCTA?: boolean;
  ctaTitle?: string;
  ctaDescription?: string;
  ctaButtonText?: string;
  ctaButtonLink?: string;
  children?: ReactNode;
}

export default function StaticPageLayout({
  title,
  description,
  icon: Icon,
  showCTA = false,
  ctaTitle,
  ctaDescription,
  ctaButtonText,
  ctaButtonLink,
  children
}: StaticPageLayoutProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header Section */}
      <div className="relative overflow-hidden bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <div className="inline-flex items-center justify-center w-16 h-16 bg-white/20 rounded-full mb-6">
              <Icon className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6">
              {title}
            </h1>
            <p className="text-xl text-blue-100 max-w-3xl mx-auto leading-relaxed">
              {description}
            </p>
          </motion.div>
        </div>
      </div>

      {/* Content Section */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-white rounded-2xl shadow-xl p-8 sm:p-12"
        >
          {children || (
            <div className="prose prose-lg max-w-none">
              <p className="text-gray-600 leading-relaxed">
                This page is currently under development. Please check back later for more information.
              </p>
            </div>
          )}
        </motion.div>
      </div>

      {/* CTA Section */}
      {showCTA && ctaTitle && ctaDescription && ctaButtonText && ctaButtonLink && (
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 py-16">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <h2 className="text-3xl font-bold text-white mb-4">
                {ctaTitle}
              </h2>
              <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
                {ctaDescription}
              </p>
              <Link href={ctaButtonLink}>
                <Button
                  size="lg"
                  className="bg-white text-blue-600 hover:bg-blue-50 transition-colors"
                >
                  {ctaButtonText}
                </Button>
              </Link>
            </motion.div>
          </div>
        </div>
      )}
    </div>
  );
}
