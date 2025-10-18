from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import sys
import os


class Command(BaseCommand):
    help = 'Start Celery worker for background tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--loglevel',
            default='info',
            help='Log level (debug, info, warning, error)'
        )
        parser.add_argument(
            '--concurrency',
            default='2',
            help='Number of worker processes'
        )
        parser.add_argument(
            '--queues',
            default='default',
            help='Comma-separated list of queues to process'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting Celery worker...')
        )
        
        # Build Celery worker command
        cmd = [
            'celery',
            '-A', 'peykan',
            'worker',
            '--loglevel=' + options['loglevel'],
            '--concurrency=' + options['concurrency'],
            '--queues=' + options['queues'],
            '--hostname=worker@%h',
            '--max-tasks-per-child=1000',
            '--max-memory-per-child=200000',  # 200MB
        ]
        
        try:
            # Start Celery worker
            self.stdout.write(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Celery worker failed with exit code {e.returncode}')
            )
            sys.exit(e.returncode)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Celery worker stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error starting Celery worker: {e}')
            )
            sys.exit(1)
