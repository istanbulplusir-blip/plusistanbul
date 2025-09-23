import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const loadingVariants = cva(
  // Base styles
  [
    'inline-flex items-center justify-center',
    'text-gray-400 dark:text-gray-500',
  ],
  {
    variants: {
      size: {
        sm: 'w-4 h-4',
        md: 'w-6 h-6',
        lg: 'w-8 h-8',
        xl: 'w-12 h-12',
      },
      variant: {
        spinner: 'animate-spin',
        dots: 'animate-pulse',
        bars: 'animate-pulse',
      },
    },
    defaultVariants: {
      size: 'md',
      variant: 'spinner',
    },
  }
);

export interface LoadingProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof loadingVariants> {
  text?: string;
  fullScreen?: boolean;
}

const Loading = React.forwardRef<HTMLDivElement, LoadingProps>(
  ({ className, size, variant, text, fullScreen, ...props }, ref) => {
    const renderSpinner = () => (
      <svg
        className="animate-spin"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
    );

    const renderDots = () => (
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
    );

    const renderBars = () => (
      <div className="flex space-x-1">
        <div className="w-1 h-4 bg-current rounded animate-pulse" style={{ animationDelay: '0ms' }} />
        <div className="w-1 h-4 bg-current rounded animate-pulse" style={{ animationDelay: '150ms' }} />
        <div className="w-1 h-4 bg-current rounded animate-pulse" style={{ animationDelay: '300ms' }} />
      </div>
    );

    const renderContent = () => {
      switch (variant) {
        case 'dots':
          return renderDots();
        case 'bars':
          return renderBars();
        default:
          return renderSpinner();
      }
    };

    const content = (
      <div
        ref={ref}
        className={cn(
          loadingVariants({ size, variant }),
          'flex flex-col items-center justify-center',
          className
        )}
        role="status"
        aria-label="Loading"
        {...props}
      >
        {renderContent()}
        {text && (
          <span className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            {text}
          </span>
        )}
      </div>
    );

    if (fullScreen) {
      return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
          {content}
        </div>
      );
    }

    return content;
  }
);

Loading.displayName = 'Loading';

// Skeleton Loading Component
const Skeleton = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    variant?: 'text' | 'circular' | 'rectangular';
    width?: string | number;
    height?: string | number;
  }
>(({ className, variant = 'text', width, height, ...props }, ref) => {
  const getDimensions = () => {
    if (width && height) {
      return { width, height };
    }
    
    switch (variant) {
      case 'circular':
        return { width: '40px', height: '40px' };
      case 'rectangular':
        return { width: '100%', height: '200px' };
      default:
        return { width: '100%', height: '1em' };
    }
  };

  const dimensions = getDimensions();

  return (
    <div
      ref={ref}
      className={cn(
        'animate-pulse bg-gray-200 dark:bg-gray-700',
        variant === 'circular' && 'rounded-full',
        variant === 'rectangular' && 'rounded-lg',
        variant === 'text' && 'rounded',
        className
      )}
      style={{
        width: dimensions.width,
        height: dimensions.height,
      }}
      {...props}
    />
  );
});

Skeleton.displayName = 'Skeleton';

export { Loading, Skeleton, loadingVariants }; 