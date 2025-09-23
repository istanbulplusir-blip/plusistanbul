'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Car, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import CarRentalCard from './CarRentalCard';
import { useFeaturedCarRentals } from '@/lib/hooks/useCarRentals';

interface CarRentalSectionProps {
  title?: string;
  subtitle?: string;
  showViewAll?: boolean;
  limit?: number;
  className?: string;
}

export default function CarRentalSection({
  title = 'Featured Car Rentals',
  subtitle = 'Discover our most popular vehicles',
  showViewAll = true,
  limit = 6,
  className = ''
}: CarRentalSectionProps) {
  const { data, error, isLoading } = useFeaturedCarRentals();

  const carRentals = data?.results?.slice(0, limit) || [];

  const formatPrice = (price: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  if (isLoading) {
    return (
      <section className={`py-16 ${className}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              {title}
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              {subtitle}
            </p>
          </div>
          
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600 dark:text-gray-400">Loading cars...</span>
          </div>
        </div>
      </section>
    );
  }

  if (error || carRentals.length === 0) {
    return null;
  }

  return (
    <section className={`py-16 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
          >
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full mb-4">
              <Car className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              {title}
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              {subtitle}
            </p>
          </motion.div>
        </div>

        {/* Car Rentals Grid */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 mb-12"
        >
          {carRentals.map((carRental, index) => (
            <motion.div
              key={carRental.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <CarRentalCard
                carRental={carRental}
                viewMode="grid"
                formatPrice={formatPrice}
              />
            </motion.div>
          ))}
        </motion.div>

        {/* View All Button */}
        {showViewAll && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <Link href="/car-rentals">
              <Button
                size="lg"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3"
              >
                View All Car Rentals
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
          </motion.div>
        )}
      </div>
    </section>
  );
}
