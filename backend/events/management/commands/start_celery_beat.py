from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import sys
import os


class Command(BaseCommand):
    help = 'Start Celery beat scheduler for periodic tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--loglevel',
            default='info',
            help='Log level (debug, info, warning, error)'
        )
        parser.add_argument(
            '--scheduler',
            default='django_celery_beat.schedulers:DatabaseScheduler',
            help='Scheduler class to use'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Celery beat scheduler...')
        )
        
        # Build Celery beat command
        cmd = [
            'celery',
            '-A', 'peykan',
            'beat',
            '--loglevel=' + options['loglevel'],
            '--scheduler=' + options['scheduler'],
            '--max-interval=300',  # Maximum interval between checks (5 minutes)
        ]
        
        try:
            # Start Celery beat
            self.stdout.write(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Celery beat failed with exit code {e.returncode}')
            )
            sys.exit(e.returncode)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Celery beat stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error starting Celery beat: {e}')
            )
            sys.exit(1)
