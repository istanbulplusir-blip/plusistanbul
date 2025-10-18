from django.apps import AppConfig


class SharedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shared'
    verbose_name = 'Shared'
    
    def ready(self):
        """Import models when app is ready."""
        # Remove problematic model import that causes circular imports
        pass 