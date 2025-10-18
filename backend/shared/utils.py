"""
Utility functions for Peykan Tourism Platform.
"""

import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from PIL import Image
import uuid


def get_image_url(image_field, request=None):
    """
    Get absolute URL for an image field.
    
    Args:
        image_field: ImageField instance or path string
        request: HttpRequest object for building absolute URLs
    
    Returns:
        str: Absolute URL to the image
    """
    if not image_field:
        return None
    
    # If it's already a URL, return as is
    if isinstance(image_field, str) and (image_field.startswith('http://') or image_field.startswith('https://')):
        return image_field
    
    # Get the file path
    if hasattr(image_field, 'url'):
        file_path = image_field.url
    else:
        file_path = str(image_field)
    
    # If we have a request, build absolute URL
    if request:
        return request.build_absolute_uri(file_path)
    
    # Otherwise, build URL from settings
    if settings.DEBUG:
        # In development, use localhost
        base_url = f"http://localhost:8000"
    else:
        # In production, use domain
        base_url = f"https://{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'peykantravelistanbul.com'}"
    
    return f"{base_url}{file_path}"


def generate_unique_filename(original_filename, upload_to='uploads/'):
    """
    Generate a unique filename for uploaded files.
    
    Args:
        original_filename: Original filename
        upload_to: Upload directory path
    
    Returns:
        str: Unique filename with path
    """
    # Get file extension
    name, ext = os.path.splitext(original_filename)
    
    # Generate unique name
    unique_name = f"{uuid.uuid4().hex}{ext}"
    
    # Add timestamp for better organization
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    
    return os.path.join(upload_to, f"{timestamp}_{unique_name}")


def optimize_image(image_path, max_size=(800, 600), quality=85):
    """
    Optimize image for web use.
    
    Args:
        image_path: Path to the image file
        max_size: Maximum dimensions (width, height)
        quality: JPEG quality (1-100)
    
    Returns:
        bool: True if optimization was successful
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Resize if larger than max_size
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            return True
            
    except Exception as e:
        print(f"Error optimizing image {image_path}: {e}")
        return False


def get_image_dimensions(image_field):
    """
    Get image dimensions.
    
    Args:
        image_field: ImageField instance
    
    Returns:
        tuple: (width, height) or None if error
    """
    try:
        if hasattr(image_field, 'path') and os.path.exists(image_field.path):
            with Image.open(image_field.path) as img:
                return img.size
        return None
    except Exception:
        return None


def validate_image_file(file_obj, max_size_mb=10, allowed_formats=None):
    """
    Validate uploaded image file.
    
    Args:
        file_obj: UploadedFile object
        max_size_mb: Maximum file size in MB
        allowed_formats: List of allowed formats (e.g., ['jpg', 'png', 'gif'])
    
    Returns:
        tuple: (is_valid, error_message)
    """
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
    
    # Check if it's actually an image
    try:
        with Image.open(file_obj) as img:
            img.verify()
        file_obj.seek(0)  # Reset file pointer
        return True, None
    except Exception:
        return False, "Invalid image file"


def get_placeholder_image_url(category='product', size='medium'):
    """
    Get placeholder image URL based on category and size.
    
    Args:
        category: Image category ('product', 'user', 'venue', etc.)
        size: Image size ('small', 'medium', 'large')
    
    Returns:
        str: Placeholder image URL
    """
    size_map = {
        'small': '300x200',
        'medium': '600x400',
        'large': '900x600'
    }
    
    dimensions = size_map.get(size, '600x400')
    
    # Use Picsum for placeholder images
    return f"https://picsum.photos/{dimensions}?random={hash(category)}"


def clean_old_images(directory, days_old=30):
    """
    Clean old unused image files.
    
    Args:
        directory: Directory to clean
        days_old: Remove files older than this many days
    
    Returns:
        int: Number of files removed
    """
    import time
    from datetime import datetime, timedelta
    
    cutoff_time = datetime.now() - timedelta(days=days_old)
    removed_count = 0
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_time:
                    os.remove(file_path)
                    removed_count += 1
    except Exception as e:
        print(f"Error cleaning old images: {e}")
    
    return removed_count
