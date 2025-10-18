/**
 * Error Handler component for Agent operations
 */

import React from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface AgentErrorHandlerProps {
  error: string | null;
  onRetry?: () => void;
  onClear?: () => void;
  title?: string;
  description?: string;
}

export default function AgentErrorHandler({ 
  error, 
  onRetry, 
  onClear,
  title = 'خطا در عملیات',
  description = 'متأسفانه خطایی رخ داده است. لطفاً دوباره تلاش کنید.'
}: AgentErrorHandlerProps) {
  if (!error) return null;

  return (
    <Card className="border-red-200 bg-red-50 dark:bg-red-900/20">
      <div className="p-6">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-6 w-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
              {title}
            </h3>
            <div className="mt-2 text-sm text-red-700 dark:text-red-300">
              <p>{description}</p>
              <p className="mt-1 font-mono text-xs bg-red-100 dark:bg-red-800 p-2 rounded">
                {error}
              </p>
            </div>
            <div className="mt-4 flex space-x-3">
              {onRetry && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={onRetry}
                  className="border-red-300 text-red-700 hover:bg-red-100 dark:border-red-600 dark:text-red-300 dark:hover:bg-red-800"
                >
                  تلاش مجدد
                </Button>
              )}
              {onClear && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={onClear}
                  className="border-red-300 text-red-700 hover:bg-red-100 dark:border-red-600 dark:text-red-300 dark:hover:bg-red-800"
                >
                  بستن
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
