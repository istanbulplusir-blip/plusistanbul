"""
URL configuration for Peykan Tourism Ecommerce Platform.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

def health_check(request):
    """Simple health check endpoint for Docker."""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Peykan Tourism API is running',
        'version': '1.0.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    # Lightweight health endpoint for uptime checks
    path('api/health', lambda request: JsonResponse({
        'status': 'ok'
    })),
    path('api/v1/health', lambda request: JsonResponse({
        'status': 'ok'
    })),
    
    # Health check endpoint
    path('api/v1/health/', health_check, name='health_check'),
    path('health/', health_check, name='health_check_alt'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1
    path('api/v1/', include([
        path('auth/', include('users.urls')),
        path('tours/', include('tours.urls')),
        path('events/', include('events.urls')),
        path('transfers/', include('transfers.urls')),
        path('car-rentals/', include('car_rentals.urls')),
        path('cart/', include('cart.urls')),
        path('orders/', include('orders.urls')),
        path('payments/', include('payments.urls')),
        path('agents/', include('agents.urls')),
        path('shared/', include('shared.urls')),
    ])),
    
    # Direct API endpoints (without v1 prefix) for frontend compatibility
    path('api/agents/', include('agents.urls', namespace='agents_direct')),
]

# Debug toolbar (development only)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Serve media files in development with proper headers
    from django.views.static import serve
    from django.conf import settings
    
    def serve_media(request, path):
        """Serve media files with proper headers for development."""
        response = serve(request, path, document_root=settings.MEDIA_ROOT)
        response['Cache-Control'] = 'public, max-age=3600'  # 1 hour cache
        response['Access-Control-Allow-Origin'] = '*'
        return response
    
    # Add media serving with custom view
    urlpatterns += [
        path('media/<path:path>', serve_media, name='media'),
    ]
    
    # Serve static files in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 