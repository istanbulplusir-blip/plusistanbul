# 🖼️ **راهنمای مدیریت تصاویر - Peykan Tourism Platform**

## 📋 **خلاصه**

این راهنما نحوه پیاده‌سازی مدیریت تصاویر در پروژه Peykan Tourism را توضیح می‌دهد که شامل Django + DRF در backend و Next.js 15 در frontend است.

## 🏗️ **معماری کلی**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django API    │    │   Media Storage │
│   (Next.js 15)  │◄──►│   (DRF)         │◄──►│   (Local/CDN)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 **Backend (Django + DRF)**

### **1. تنظیمات Media**

#### **settings.py**

```python
# Media files
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / 'media'

# Image processing settings
IMAGE_MAX_SIZE = (1920, 1080)  # Maximum dimensions
IMAGE_QUALITY = 85  # JPEG quality
IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
MAX_IMAGE_SIZE_MB = 10

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = config('FILE_UPLOAD_MAX_MEMORY_SIZE', default=10, cast=int) * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = config('DATA_UPLOAD_MAX_MEMORY_SIZE', default=10, cast=int) * 1024 * 1024
```

#### **urls.py**

```python
# Development: Serve media files with proper headers
if settings.DEBUG:
    def serve_media(request, path):
        response = serve(request, path, document_root=settings.MEDIA_ROOT)
        response['Cache-Control'] = 'public, max-age=3600'
        response['Access-Control-Allow-Origin'] = '*'
        return response

    urlpatterns += [
        path('media/<path:path>', serve_media, name='media'),
    ]
```

### **2. Utility Functions**

#### **shared/utils.py**

```python
def get_image_url(image_field, request=None):
    """Get absolute URL for an image field."""
    if not image_field:
        return None

    if hasattr(image_field, 'url'):
        file_path = image_field.url
    else:
        file_path = str(image_field)

    if request:
        return request.build_absolute_uri(file_path)

    # Build URL from settings
    if settings.DEBUG:
        base_url = f"http://localhost:8000"
    else:
        base_url = f"https://{settings.ALLOWED_HOSTS[0]}"

    return f"{base_url}{file_path}"

def validate_image_file(file_obj, max_size_mb=10, allowed_formats=None):
    """Validate uploaded image file."""
    # Implementation details...
```

### **3. Serializer Mixins**

#### **shared/serializers.py**

```python
class ImageFieldSerializerMixin:
    """Mixin to automatically convert ImageField to absolute URLs."""

    def get_image_url(self, obj, field_name='image'):
        image_field = getattr(obj, field_name, None)
        if not image_field:
            return None

        request = self.context.get('request')
        return get_image_url(image_field, request)

class BaseModelSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    """Base serializer with image URL support."""

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Add image URLs for all ImageField fields
        for field_name, field in instance._meta.fields.items():
            if field.get_internal_type() == 'ImageField':
                data[f'{field_name}_url'] = self.get_image_url(instance, field_name)

        return data
```

### **4. استفاده در Serializer ها**

#### **tours/serializers.py**

```python
class TourListSerializer(serializers.ModelSerializer, ImageFieldSerializerMixin):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Tour
        fields = [
            'id', 'slug', 'title', 'image', 'image_url', 'price', 'currency',
            # ... other fields
        ]
```

## 🎨 **Frontend (Next.js 15)**

### **1. تنظیمات Image Optimization**

#### **next.config.js**

```javascript
images: {
  // Image optimization settings
  formats: ['image/webp', 'image/avif'],
  deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
  imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  minimumCacheTTL: 60 * 60 * 24 * 30, // 30 days

  remotePatterns: [
    // Media files from Django backend
    {
      protocol: 'http',
      hostname: 'localhost',
      port: '8000',
      pathname: '/media/**',
    },
    {
      protocol: 'https',
      hostname: 'peykantravelistanbul.com',
      port: '',
      pathname: '/media/**',
    },
  ],
},
```

### **2. کامپوننت OptimizedImage**

#### **components/common/OptimizedImage.tsx**

```typescript
const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width = 800,
  height = 600,
  className,
  priority = false,
  fallbackSrc = "/images/placeholder.jpg",
  sizes = "(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw",
  quality = 85,
  placeholder = "empty",
  onError,
  onLoad,
}) => {
  const [imageSrc, setImageSrc] = useState<string>(src || fallbackSrc);
  const [hasError, setHasError] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Handle image error with fallback
  const handleError = () => {
    if (!hasError && imageSrc !== fallbackSrc) {
      setImageSrc(fallbackSrc);
      setHasError(true);
      onError?.();
    }
  };

  return (
    <div className={cn("relative overflow-hidden", className)}>
      <Image
        src={imageSrc}
        alt={alt}
        width={width}
        height={height}
        className={cn(
          "transition-opacity duration-300",
          isLoading ? "opacity-0" : "opacity-100"
        )}
        priority={priority}
        sizes={sizes}
        quality={quality}
        placeholder={placeholder}
        onError={handleError}
        onLoad={() => setIsLoading(false)}
      />

      {/* Loading and error states */}
      {isLoading && <LoadingPlaceholder />}
      {hasError && <ErrorFallback />}
    </div>
  );
};
```

### **3. Utility Functions**

#### **lib/utils.ts**

```typescript
export function getImageUrl(
  imageUrl: string | null | undefined,
  size: "thumbnail" | "small" | "medium" | "large" | "original" = "medium"
): string {
  if (!imageUrl) {
    return "/images/placeholder.jpg";
  }

  // For media files from Django backend
  if (imageUrl.startsWith("media/")) {
    return `/${imageUrl}`;
  }

  // If it's a relative path, assume it's from media
  if (!imageUrl.startsWith("http") && !imageUrl.startsWith("/")) {
    return `/media/${imageUrl}`;
  }

  return imageUrl;
}

export function getImageDimensions(
  size: "thumbnail" | "small" | "medium" | "large" | "original"
) {
  const dimensions = {
    thumbnail: { width: 150, height: 100 },
    small: { width: 300, height: 200 },
    medium: { width: 600, height: 400 },
    large: { width: 900, height: 600 },
    original: { width: 1920, height: 1080 },
  };

  return dimensions[size] || dimensions.medium;
}
```

### **4. استفاده در کامپوننت‌ها**

#### **components/common/ProductCard.tsx**

```typescript
import OptimizedImage from "./OptimizedImage";
import { getImageUrl } from "@/lib/utils";

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  const getProductImage = () => {
    if (product.type === "tour") {
      return getImageUrl(product.image_url || product.image, "medium");
    }
    return getImageUrl(product.image, "medium");
  };

  return (
    <div className="product-card">
      <OptimizedImage
        src={getProductImage()}
        alt={product.title || "Product Image"}
        width={400}
        height={300}
        className="w-full h-48 object-cover rounded-lg"
        fallbackSrc="/images/placeholder.jpg"
        priority={false}
      />
      {/* ... rest of component */}
    </div>
  );
};
```

## 🚀 **Production Deployment**

### **1. Cloud Storage (AWS S3)**

#### **settings_production.py**

```python
# AWS S3 Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN')

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

#### **requirements.txt**

```txt
# Production storage
boto3==1.34.0
django-storages==1.14.2
```

### **2. CDN Configuration**

#### **next.config.js**

```javascript
async rewrites() {
  const apiUrl = process.env.NODE_ENV === 'production'
    ? 'https://peykantravelistanbul.com'
    : 'http://localhost:8000';

  return [
    // Proxy media files to CDN in production
    {
      source: '/media/:path*',
      destination: process.env.NODE_ENV === 'production'
        ? 'https://your-cdn-domain.com/media/:path*'
        : `${apiUrl}/media/:path*`,
    },
  ];
}
```

## 📁 **ساختار فایل‌ها**

```
backend/
├── media/                    # Media files storage
│   ├── products/            # Product images
│   ├── venues/              # Venue images
│   ├── artists/             # Artist images
│   ├── avatars/             # User avatars
│   └── itinerary/           # Tour itinerary images
├── shared/
│   ├── utils.py             # Image utility functions
│   └── serializers.py       # Image serializer mixins
└── peykan/
    ├── settings.py          # Media settings
    └── urls.py              # Media serving

frontend/
├── components/
│   └── common/
│       └── OptimizedImage.tsx  # Image component
├── lib/
│   └── utils.ts             # Image utility functions
├── public/
│   └── images/              # Static images
└── next.config.js           # Image optimization config
```

## 🔒 **امنیت و Validation**

### **1. File Validation**

```python
def validate_image_file(file_obj, max_size_mb=10, allowed_formats=None):
    """Validate uploaded image file."""
    if allowed_formats is None:
        allowed_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp']

    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_size_bytes:
        return False, f"File size must be less than {max_size_mb}MB"

    # Check file format
    file_extension = file_obj.name.split('.')[-1].lower()
    if file_extension not in allowed_formats:
        return False, f"Only {', '.join(allowed_formats)} formats are allowed"

    # Validate image content
    try:
        with Image.open(file_obj) as img:
            img.verify()
        file_obj.seek(0)
        return True, None
    except Exception:
        return False, "Invalid image file"
```

### **2. CORS Configuration**

```python
# CORS Media settings
CORS_ALLOW_MEDIA = True
CORS_MEDIA_HEADERS = [
    'content-type',
    'content-length',
    'cache-control',
    'last-modified',
    'etag',
]
```

## 📊 **Performance Optimization**

### **1. Image Optimization**

- **Formats**: WebP, AVIF for modern browsers
- **Sizes**: Responsive image sizes
- **Caching**: 30-day cache for images
- **Lazy Loading**: Automatic lazy loading for images below the fold

### **2. CDN Benefits**

- **Global Distribution**: Faster loading worldwide
- **Caching**: Reduced server load
- **Compression**: Automatic image compression
- **HTTPS**: Secure image delivery

## 🧪 **Testing**

### **1. Backend Testing**

```python
def test_image_validation():
    """Test image file validation."""
    from shared.utils import validate_image_file

    # Test valid image
    valid_file = create_test_image_file()
    is_valid, error = validate_image_file(valid_file)
    assert is_valid is True

    # Test invalid format
    invalid_file = create_test_file_with_extension('.txt')
    is_valid, error = validate_image_file(invalid_file)
    assert is_valid is False
    assert 'formats are allowed' in error
```

### **2. Frontend Testing**

```typescript
describe("OptimizedImage", () => {
  it("should render with fallback on error", () => {
    render(
      <OptimizedImage
        src="invalid-url"
        alt="Test"
        fallbackSrc="/fallback.jpg"
      />
    );

    // Should show fallback image
    expect(screen.getByAltText("Test")).toHaveAttribute("src", "/fallback.jpg");
  });
});
```

## 🚨 **Troubleshooting**

### **1. Common Issues**

#### **Image not loading**

- Check CORS settings
- Verify media URL configuration
- Check file permissions

#### **Performance issues**

- Enable image optimization
- Use appropriate image sizes
- Implement lazy loading

#### **Storage issues**

- Check disk space
- Verify storage backend configuration
- Monitor file upload limits

### **2. Debug Commands**

```bash
# Check media directory permissions
ls -la backend/media/

# Test image serving
curl -I http://localhost:8000/media/products/test.jpg

# Check Django settings
python manage.py shell -c "from django.conf import settings; print(settings.MEDIA_URL)"
```

## 📚 **References**

- [Django File Uploads](https://docs.djangoproject.com/en/4.2/topics/files/)
- [Next.js Image Optimization](https://nextjs.org/docs/api-reference/next/image)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [AWS S3 Storage](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)

## 🤝 **Contributing**

برای بهبود این سیستم:

1. تست‌های جدید اضافه کنید
2. Performance optimization پیاده‌سازی کنید
3. Error handling بهبود دهید
4. Documentation به‌روزرسانی کنید

---

**نکته**: این راهنما برای محیط development تنظیم شده است. برای production، حتماً تنظیمات امنیتی و CDN را فعال کنید.
