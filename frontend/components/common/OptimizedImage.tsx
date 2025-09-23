'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { cn } from '@/lib/utils';

interface OptimizedImageProps {
  src: string | null | undefined;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  priority?: boolean;
  fallbackSrc?: string;
  sizes?: string;
  quality?: number;
  placeholder?: 'blur' | 'empty';
  blurDataURL?: string;
  onError?: () => void;
  onLoad?: () => void;
  fill?: boolean;
  style?: React.CSSProperties;
}

const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width = 800,
  height = 600,
  className,
  priority = false,
  fallbackSrc,
  sizes = '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw',
  quality = 85,
  placeholder = 'empty',
  blurDataURL,
  fill = false,
  style,
  onError,
  onLoad,
}) => {
  const [imageSrc, setImageSrc] = useState<string>(src || fallbackSrc || '/images/event-image.jpg');
  const [hasError, setHasError] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Update imageSrc when src prop changes
  useEffect(() => {
    if (src && src !== imageSrc) {
      setImageSrc(src);
      setHasError(false);
      setIsLoading(true);
    }
  }, [src, imageSrc]);

  // Handle image error
  const handleError = () => {
    if (!hasError && imageSrc !== (fallbackSrc || '/images/event-image.jpg')) {
      setImageSrc(fallbackSrc || '/images/event-image.jpg');
      setHasError(true);
      onError?.();
    }
  };

  // Handle image load
  const handleLoad = () => {
    setIsLoading(false);
    onLoad?.();
  };

  // Get optimized image URL with better fallback logic
  const getOptimizedImageUrl = (imageUrl: string): string => {
    if (!imageUrl) {
      return fallbackSrc || '/images/event-image.jpg';
    }

    if (imageUrl === fallbackSrc) {
      return imageUrl;
    }

    // Handle malformed URLs and placeholders
    if (imageUrl === 'null' || imageUrl === 'undefined' || imageUrl.includes('via.placeholder.com')) {
      return fallbackSrc || '/images/event-image.jpg';
    }

    // If it's already a placeholder or external URL, return as is
    if (imageUrl.startsWith('/images/') || imageUrl.startsWith('http')) {
      return imageUrl;
    }

    // For media files from backend, use direct URL
    if (imageUrl.startsWith('media/')) {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';
      return `${backendUrl}/${imageUrl}`;
    }

    // If it's already a full backend URL, return as is
    if (imageUrl.startsWith('http://localhost:8000/') || imageUrl.startsWith('http://127.0.0.1:8000/')) {
      return imageUrl;
    }

    return imageUrl;
  };

  const finalSrc = getOptimizedImageUrl(imageSrc || fallbackSrc || '/images/event-image.jpg');

  // Ensure alt is always a valid string
  const safeAlt = alt || 'Image';

  return (
    <div className={cn('relative overflow-hidden w-full h-full', className)}>
      <Image
        src={finalSrc}
        alt={safeAlt}
        {...(fill ? {} : { width, height })}
        className={cn(
          'transition-opacity duration-300',
          isLoading ? 'opacity-0' : 'opacity-100'
        )}
        priority={priority}
        sizes={sizes}
        quality={quality}
        placeholder={placeholder}
        blurDataURL={blurDataURL}
        fill={fill}
        style={fill ? style : {
          ...style,
          width: 'auto',
          height: 'auto'
        }}
        onError={handleError}
        onLoad={handleLoad}
      />
      
      {/* Loading placeholder */}
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse flex items-center justify-center">
          <div className="text-gray-400 text-sm">Loading...</div>
        </div>
      )}
      
      {/* Error fallback */}
      {hasError && (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
          <div className="text-gray-400 text-sm text-center">
            <div>Image not available</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OptimizedImage;
