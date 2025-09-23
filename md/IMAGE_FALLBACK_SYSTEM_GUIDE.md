# 🖼️ **Image Fallback System Guide - Peykan Tourism**

## 📋 **Overview**

This document describes the comprehensive image fallback system implemented to handle missing or incomplete product images in both backend and frontend, ensuring a consistent user experience.

## 🏗️ **Architecture**

### **Backend (Django DRF)**

- **BaseProductModel**: Abstract base with optional image field
- **ImageFieldSerializerMixin**: Provides fallback URLs based on model type
- **Default Images**: Stored in `/media/defaults/` directory

### **Frontend (Next.js)**

- **OptimizedImage**: Component with error handling and fallbacks
- **ProductCard**: Intelligent fallback selection based on product type
- **Fallback Chain**: Backend → Frontend → Hardcoded defaults

## 🔧 **Backend Implementation**

### **1. Model Changes**

```python
# core/models.py - BaseProductModel
class BaseProductModel(BaseTranslatableModel):
    image = models.ImageField(
        upload_to='products/',
        null=True,           # ✅ Now optional
        blank=True,          # ✅ Can be empty in forms
        verbose_name=_('Image')
    )

    def get_image_url(self, request=None):
        """Get image URL with fallback to default image."""
        if self.image:
            if request:
                return request.build_absolute_uri(self.image.url)
            return self.image.url
        return '/media/defaults/no-image.png'  # ✅ Fallback
```

### **2. Serializer Mixin**

```python
# shared/serializers.py - ImageFieldSerializerMixin
class ImageFieldSerializerMixin:
    def get_default_image_url(self, model_type='product'):
        """Get default image URL based on model type."""
        defaults = {
            'product': '/media/defaults/no-image.png',
            'tour': '/media/defaults/tour-default.png',
            'event': '/media/defaults/event-default.png',
            'venue': '/media/defaults/venue-default.png',
            'artist': '/media/defaults/artist-default.png',
            'transfer': '/media/defaults/transfer-default.png',
        }
        return defaults.get(model_type, defaults['product'])

    def get_image_url(self, obj, field_name='image', model_type='product'):
        """Get absolute URL with fallback."""
        image_field = getattr(obj, field_name, None)
        if not image_field:
            return self.get_default_image_url(model_type)  # ✅ Fallback
        # ... rest of logic
```

### **3. Model-Specific Serializers**

```python
# tours/serializers.py
class TourListSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    def get_image_url(self, obj):
        """Get image URL with tour-specific fallback."""
        return super().get_image_url(obj, 'image', 'tour')

# events/serializers.py
class EventListSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    def get_image_url(self, obj):
        """Get image URL with event-specific fallback."""
        return super().get_image_url(obj, 'image', 'event')
```

## 🎨 **Frontend Implementation**

### **1. OptimizedImage Component**

```typescript
// components/common/OptimizedImage.tsx
const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  fallbackSrc = "/images/event-image.jpg", // ✅ Frontend fallback
  // ... other props
}) => {
  const [imageSrc, setImageSrc] = useState<string>(src || fallbackSrc);
  const [hasError, setHasError] = useState<boolean>(false);

  const handleError = () => {
    if (!hasError && imageSrc !== fallbackSrc) {
      setImageSrc(fallbackSrc); // ✅ Switch to fallback on error
      setHasError(true);
    }
  };

  // ... rest of component
};
```

### **2. ProductCard Intelligence**

```typescript
// components/common/ProductCard.tsx
const getProductImage = () => {
  const imageSource = product.image_url || product.image;

  if (imageSource) {
    // ✅ Handle backend fallback URLs
    if (imageSource.includes("/media/defaults/")) {
      const backendUrl =
        process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") ||
        "http://localhost:8000";
      return `${backendUrl}${imageSource}`;
    }
    return getImageUrl(imageSource, "medium");
  }

  // ✅ Frontend fallbacks based on product type
  if (product.type === "tour") {
    return "/images/tour-image.jpg";
  } else if (product.type === "event") {
    return "/images/event-image.jpg";
  }

  return "/images/event-image.jpg";
};
```

## 🗂️ **Default Images Structure**

```
backend/media/defaults/
├── no-image.png          # Generic fallback
├── tour-default.png      # Tour-specific fallback
├── event-default.png     # Event-specific fallback
├── venue-default.png     # Venue-specific fallback
├── artist-default.png    # Artist-specific fallback
└── transfer-default.png  # Transfer-specific fallback
```

## 🔄 **Fallback Chain Priority**

1. **Backend Image**: `obj.image` (if exists)
2. **Backend Fallback**: `/media/defaults/{model-type}-default.png`
3. **Frontend Fallback**: `/images/{product-type}-image.jpg`
4. **Hardcoded Default**: `/images/event-image.jpg`

## 📊 **API Response Examples**

### **With Image**

```json
{
  "id": "uuid",
  "title": "Istanbul City Tour",
  "image_url": "http://localhost:8000/media/products/tour1.jpg",
  "type": "tour"
}
```

### **Without Image (Using Fallback)**

```json
{
  "id": "uuid",
  "title": "Istanbul City Tour",
  "image_url": "/media/defaults/tour-default.png", // ✅ Fallback
  "type": "tour"
}
```

## 🧪 **Testing**

### **Backend Test**

```bash
cd backend
python manage.py runserver 8000
# Test API endpoints with missing images
```

### **Frontend Test**

```bash
cd frontend
npm run dev
# Test product cards with missing images
```

## ✅ **Benefits**

1. **Consistent UX**: Always shows an image, never broken
2. **API Reliability**: No errors from missing images
3. **Type-Specific Fallbacks**: Appropriate images for each product type
4. **Performance**: No broken image requests
5. **Maintainability**: Centralized fallback logic

## 🚀 **Usage Examples**

### **Creating a Product Without Image**

```python
# This will now work without errors
tour = Tour.objects.create(
    title="New Tour",
    price=50.00,
    # image field is optional now
)
# API will return fallback image URL
```

### **Frontend Display**

```typescript
// ProductCard automatically handles missing images
<ProductCard
  product={tour} // Even without image, fallback will be used
  viewMode="grid"
/>
```

## 🔧 **Maintenance**

### **Adding New Default Images**

1. Add image to `backend/media/defaults/`
2. Update `get_default_image_url()` in `ImageFieldSerializerMixin`
3. Test with relevant model type

### **Updating Fallback Logic**

1. Modify `ImageFieldSerializerMixin` methods
2. Update model-specific serializers if needed
3. Test fallback chain

## 📝 **Notes**

- **Migration Required**: Run `python manage.py migrate` after model changes
- **Media Files**: Ensure `/media/defaults/` directory exists
- **Environment Variables**: Set `NEXT_PUBLIC_API_URL` in frontend
- **Caching**: Consider CDN caching for default images in production

---

**Last Updated**: August 28, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
