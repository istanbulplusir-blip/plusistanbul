# Image Handling Guide

This document explains the image handling system implemented to prevent 404 errors and broken image rendering.

## Overview

The image handling system consists of:

1. **Image Validation Module** (`lib/imageValidation.ts`)
2. **OptimizedImage Component** (`components/common/OptimizedImage.tsx`)
3. **Enhanced Utils** (`lib/utils.ts`)

## Key Features

### 1. Automatic Fallback Handling

- All images have proper fallback chains
- Invalid or missing images automatically use safe placeholders
- No more broken image icons in the UI

### 2. Backend URL Validation

- Handles backend media URLs correctly
- Prevents double-slash issues (`/images//media/...`)
- Identifies and handles known problematic images

### 3. Placeholder Image Management

- Centralized list of valid placeholder images
- Consistent fallback images across the application
- Type-specific fallbacks (tours, events, cars, etc.)

## Valid Placeholder Images

The following images are confirmed to exist in `public/images/`:

- `/images/placeholder-car.jpg` (default fallback)
- `/images/event-image.jpg`
- `/images/event-hero.jpg`
- `/images/about-image.jpg`
- `/images/tour-image.jpg`
- `/images/black-van-top.jpg`
- `/images/concert-hall.jpg`
- `/images/event-center-image.jpg`
- `/images/hero-main.jpg`
- `/images/info-bg.jpg`
- `/images/istanbul-fallback.jpg`
- `/images/simple-bg.jpg`

## Known Problematic Images

The system automatically handles these known problematic backend images:

- `istanbul-cultural-tour.jpg` (404 error)
- Any other images that return 404 errors

## Usage Examples

### Basic Image Loading

```tsx
import OptimizedImage from "@/components/common/OptimizedImage";

<OptimizedImage
  src={imageUrl}
  alt="Description"
  fallbackSrc="/images/placeholder-car.jpg"
  width={400}
  height={300}
/>;
```

### Using getImageUrl Utility

```tsx
import { getImageUrl } from "@/lib/utils";

const imageUrl = getImageUrl(product.image); // Automatically handles validation
```

### Product-Specific Fallbacks

```tsx
// For tours
<OptimizedImage
  src={tour.image}
  fallbackSrc="/images/tour-image.jpg"
  alt={tour.title}
/>

// For events
<OptimizedImage
  src={event.image}
  fallbackSrc="/images/event-image.jpg"
  alt={event.title}
/>
```

## Error Handling

### Console Warnings

The system provides helpful console warnings for debugging:

- `Invalid image path: /path/to/image. Using fallback.`
- `Known problematic backend image: image.jpg. Using fallback.`
- `Image failed to load: url. Using fallback: fallback-url.`

### Fallback Chain

1. **Primary Image**: The intended image URL
2. **Custom Fallback**: Component-specific fallback (if provided)
3. **Type Fallback**: Type-specific fallback (tour, event, car, etc.)
4. **Default Fallback**: `/images/placeholder-car.jpg`

## Backend URL Handling

### Media Paths

- `media/tours/image.jpg` → `http://localhost:8000/media/tours/image.jpg`
- `/media/tours/image.jpg` → `http://localhost:8000/media/tours/image.jpg`

### Double Slash Fix

- `/images//media/tours/image.jpg` → `/images/media/tours/image.jpg`
- Automatically cleans up malformed URLs

## Adding New Placeholder Images

1. Add the image file to `public/images/`
2. Add the path to `VALID_PLACEHOLDER_IMAGES` in `imageValidation.ts`
3. Update this documentation

## Adding Problematic Images

If you discover new problematic backend images:

1. Add the filename to `PROBLEMATIC_BACKEND_IMAGES` in `imageValidation.ts`
2. The system will automatically use fallbacks for these images

## Best Practices

1. **Always provide fallbackSrc** for critical images
2. **Use type-specific fallbacks** when possible
3. **Test with network throttling** to ensure fallbacks work
4. **Monitor console warnings** for new problematic images
5. **Keep placeholder images optimized** (small file sizes)

## Troubleshooting

### Common Issues

1. **404 Errors**: Check if the image exists in the backend media directory
2. **Double Slash URLs**: The system automatically fixes these
3. **Missing Fallbacks**: Ensure fallbackSrc is provided for important images
4. **Slow Loading**: Use appropriate image sizes and optimization

### Debug Mode

Enable debug logging by checking browser console for:

- Image validation warnings
- Fallback usage notifications
- Error handling messages

## Migration Guide

### From Old Image Handling

**Before:**

```tsx
<img src={imageUrl || "/images/placeholder.jpg"} alt="..." />
```

**After:**

```tsx
<OptimizedImage
  src={imageUrl}
  alt="..."
  fallbackSrc="/images/placeholder-car.jpg"
/>
```

### Benefits of Migration

1. **No more broken images**
2. **Better performance** with Next.js Image optimization
3. **Consistent fallbacks** across the application
4. **Better error handling** and debugging
5. **Automatic URL validation** and cleanup

## Performance Considerations

- Images are automatically optimized by Next.js
- Fallbacks prevent layout shifts
- Lazy loading is enabled by default
- Proper sizing prevents unnecessary downloads

This system ensures a robust, user-friendly image experience across the entire application.
