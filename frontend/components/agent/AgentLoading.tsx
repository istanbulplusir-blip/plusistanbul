/**
 * Loading component for Agent operations
 */

import React from 'react';

interface AgentLoadingProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
}

export default function AgentLoading({ 
  message = 'در حال بارگذاری...', 
  size = 'md' 
}: AgentLoadingProps) {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  };

  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative">
        <div className={`${sizeClasses[size]} border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin`}></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <svg className={`${size === 'sm' ? 'w-4 h-4' : size === 'md' ? 'w-6 h-6' : 'w-8 h-8'} text-blue-600`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
      <div className="mt-4 text-center">
        <h3 className={`${textSizeClasses[size]} font-semibold text-gray-900 dark:text-white`}>
          {message}
        </h3>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          لطفاً صبر کنید...
        </p>
      </div>
    </div>
  );
}
