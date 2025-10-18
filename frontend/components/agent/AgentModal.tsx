'use client';

import { ReactNode } from 'react';
import { useLocale } from 'next-intl';
import { cn } from '@/lib/utils';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface AgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showCloseButton?: boolean;
  className?: string;
}

export default function AgentModal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
  className
}: AgentModalProps) {
  const locale = useLocale();
  const isRTL = locale === 'fa';

  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'w-80',
    md: 'w-96',
    lg: 'w-[500px]',
    xl: 'w-[600px]'
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className={cn(
        "relative top-20 mx-auto p-5 border shadow-lg rounded-md bg-white dark:bg-gray-800",
        sizeClasses[size],
        className
      )}>
        <div className="mt-3">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              {title}
            </h3>
            {showCloseButton && (
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            )}
          </div>
          
          <div className={cn(
            "space-y-4",
            isRTL && "text-right"
          )}>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
