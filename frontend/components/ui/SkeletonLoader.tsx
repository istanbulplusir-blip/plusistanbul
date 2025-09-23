import React from 'react';
import { Skeleton } from '@/lib/design-system';

interface SkeletonLoaderProps {
  variant?: 'card' | 'list' | 'detail' | 'form';
  count?: number;
  className?: string;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ 
  variant = 'card', 
  count = 1,
  className = ''
}) => {
  const renderCardSkeleton = () => (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 space-y-3">
      <Skeleton variant="rectangular" height="200px" className="rounded-lg" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
        <Skeleton className="h-3 w-2/3" />
      </div>
      <div className="flex justify-between items-center pt-2">
        <Skeleton className="h-6 w-20" />
        <Skeleton className="h-8 w-24 rounded-lg" />
      </div>
    </div>
  );

  const renderListSkeleton = () => (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="flex items-center space-x-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <Skeleton variant="circular" width="60px" height="60px" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
            <Skeleton className="h-3 w-2/3" />
          </div>
          <Skeleton className="h-8 w-20 rounded-lg" />
        </div>
      ))}
    </div>
  );

  const renderDetailSkeleton = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <Skeleton variant="rectangular" height="300px" className="rounded-lg" />
        <div className="space-y-3">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
          <Skeleton className="h-4 w-2/3" />
          <Skeleton className="h-4 w-1/3" />
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-3">
          <Skeleton className="h-6 w-1/3" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </div>
        <div className="space-y-3">
          <Skeleton className="h-6 w-1/3" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </div>
      </div>
    </div>
  );

  const renderFormSkeleton = () => (
    <div className="space-y-6">
      <div className="space-y-4">
        <Skeleton className="h-6 w-1/4" />
        <Skeleton className="h-10 w-full rounded-lg" />
      </div>
      <div className="space-y-4">
        <Skeleton className="h-6 w-1/4" />
        <Skeleton className="h-10 w-full rounded-lg" />
      </div>
      <div className="space-y-4">
        <Skeleton className="h-6 w-1/4" />
        <Skeleton className="h-20 w-full rounded-lg" />
      </div>
      <div className="flex space-x-4">
        <Skeleton className="h-10 w-24 rounded-lg" />
        <Skeleton className="h-10 w-24 rounded-lg" />
      </div>
    </div>
  );

  const renderSkeleton = () => {
    switch (variant) {
      case 'list':
        return renderListSkeleton();
      case 'detail':
        return renderDetailSkeleton();
      case 'form':
        return renderFormSkeleton();
      default:
        return (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Array.from({ length: count }).map((_, index) => (
              <div key={index}>{renderCardSkeleton()}</div>
            ))}
          </div>
        );
    }
  };

  return <div className={`animate-fade-in ${className}`}>{renderSkeleton()}</div>;
}; 