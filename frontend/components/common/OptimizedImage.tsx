'use client';

import React, { useState, useEffect } from 'react';
import Image from 'next/image';
import { cn } from '@/lib/utils';
import { processImageUrl, getSafeFallbackImage } from '@/lib/imageValidation';

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
  const [imageSrc, setImageSrc] = useState<string>(processImageUrl(src, fallbackSrc));
  const [hasError, setHasError] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Update imageSrc when src prop changes
  useEffect(() => {
    const newImageSrc = processImageUrl(src, fallbackSrc);
    if (newImageSrc !== imageSrc) {
      setImageSrc(newImageSrc);
      setHasError(false);
      setIsLoading(true);
    }
  }, [src, fallbackSrc, imageSrc]);

  // Handle image error
  const handleError = () => {
    const safeFallback = getSafeFallbackImage(fallbackSrc);
    if (!hasError && imageSrc !== safeFallback) {
      console.warn(`Image failed to load: ${imageSrc}. Using fallback: ${safeFallback}`);
      setImageSrc(safeFallback);
      setHasError(true);
      onError?.();
    }
  };

  // Handle image load
  const handleLoad = () => {
    setIsLoading(false);
    onLoad?.();
  };

  const finalSrc = processImageUrl(imageSrc, fallbackSrc);

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
