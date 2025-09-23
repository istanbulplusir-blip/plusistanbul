import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'peykan.settings')

app = Celery('peykan')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Celery Beat Schedule
app.conf.beat_schedule = {
    'cleanup-expired-reservations': {
        'task': 'events.tasks.cleanup_expired_reservations',
        'schedule': 300.0,  # Every 5 minutes
    },
    'cleanup-expired-carts': {
        'task': 'cart.tasks.cleanup_expired_carts',
        'schedule': 600.0,  # Every 10 minutes
    },
    'update-capacity-cache': {
        'task': 'events.tasks.update_capacity_cache',
        'schedule': 1800.0,  # Every 30 minutes
    },
}

# Celery Configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    broker_connection_retry_on_startup=True,
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
