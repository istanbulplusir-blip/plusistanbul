/**
 * Image validation and fallback utilities
 * Ensures all image URLs are valid and have proper fallbacks
 */

// List of valid placeholder images that exist in the project
export const VALID_PLACEHOLDER_IMAGES = [
  '/images/placeholder-car.jpg',
  '/images/event-image.jpg',
  '/images/event-hero.jpg',
  '/images/about-image.jpg',
  '/images/tour-image.jpg',
  '/images/black-van-top.jpg',
  '/images/concert-hall.jpg',
  '/images/event-center-image.jpg',
  '/images/hero-main.jpg',
  '/images/info-bg.jpg',
  '/images/istanbul-fallback.jpg',
  '/images/simple-bg.jpg',
] as const;

// Default fallback image
export const DEFAULT_FALLBACK_IMAGE = '/images/placeholder-car.jpg';

// Known problematic backend images that should use fallbacks
const PROBLEMATIC_BACKEND_IMAGES = [
  'istanbul-cultural-tour.jpg',
  'non-existent-image.jpg'
] as const;

/**
 * Validates if an image path exists in our valid placeholder list
 */
export function isValidPlaceholderImage(imagePath: string): boolean {
  return VALID_PLACEHOLDER_IMAGES.includes(imagePath as any);
}

/**
 * Gets a safe fallback image URL
 * @param fallbackSrc - Custom fallback source
 * @param defaultFallback - Default fallback if custom is invalid
 * @returns A valid fallback image URL
 */
export function getSafeFallbackImage(
  fallbackSrc?: string,
  defaultFallback: string = DEFAULT_FALLBACK_IMAGE
): string {
  if (fallbackSrc && isValidPlaceholderImage(fallbackSrc)) {
    return fallbackSrc;
  }
  return defaultFallback;
}

/**
 * Enhanced image URL getter with validation
 * @param imagePath - The image path to process
 * @param fallbackSrc - Custom fallback source
 * @returns A validated image URL
 */
export function getValidatedImageUrl(
  imagePath: string | undefined,
  fallbackSrc?: string
): string {
  if (!imagePath) {
    return getSafeFallbackImage(fallbackSrc);
  }

  if (imagePath.startsWith('http')) {
    return imagePath;
  }

  // Handle media paths from backend
  if (imagePath.startsWith('media/') || imagePath.startsWith('/media/')) {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';
    const cleanPath = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
    return `${backendUrl}${cleanPath}`;
  }

  // If it's a placeholder, validate it exists
  if (imagePath.startsWith('/images/')) {
    if (isValidPlaceholderImage(imagePath)) {
      return imagePath;
    } else {
      console.warn(`Invalid placeholder image: ${imagePath}. Using fallback.`);
      return getSafeFallbackImage(fallbackSrc);
    }
  }

  return `/images/${imagePath}`;
}

/**
 * Checks if a backend image URL is known to be problematic
 * @param imageUrl - The image URL to check
 * @returns True if the image is known to be problematic
 */
function isProblematicBackendImage(imageUrl: string): boolean {
  return PROBLEMATIC_BACKEND_IMAGES.some(problematic => 
    imageUrl.includes(problematic)
  );
}

/**
 * Validates and processes image URLs for OptimizedImage component
 * @param src - Source image URL
 * @param fallbackSrc - Fallback image URL
 * @returns Processed and validated image URL
 */
export function processImageUrl(
  src: string | null | undefined,
  fallbackSrc?: string
): string {
  if (!src) {
    return getSafeFallbackImage(fallbackSrc);
  }

  // Handle malformed URLs
  if (src === 'null' || src === 'undefined' || src.includes('via.placeholder.com')) {
    return getSafeFallbackImage(fallbackSrc);
  }

  // Fix double slash issues
  if (src.includes('//')) {
    src = src.replace(/\/+/g, '/');
  }

  // Check for known problematic backend images
  if (isProblematicBackendImage(src)) {
    console.warn(`Known problematic backend image: ${src}. Using fallback.`);
    return getSafeFallbackImage(fallbackSrc);
  }

  // If it's already a placeholder or external URL, validate and return
  if (src.startsWith('/images/') || src.startsWith('http')) {
    if (src.startsWith('/images/') && !isValidPlaceholderImage(src)) {
      console.warn(`Invalid image path: ${src}. Using fallback.`);
      return getSafeFallbackImage(fallbackSrc);
    }
    return src;
  }

  // For media files from backend, use direct URL
  if (src.startsWith('media/') || src.startsWith('/media/')) {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || 'http://localhost:8000';
    const cleanPath = src.startsWith('/') ? src : `/${src}`;
    return `${backendUrl}${cleanPath}`;
  }

  // If it's already a full backend URL, return as is
  if (src.startsWith('http://localhost:8000/') || src.startsWith('http://127.0.0.1:8000/')) {
    return src;
  }

  return src;
}
