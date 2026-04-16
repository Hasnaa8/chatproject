import os
from celery import Celery

# 1. Set the default Django settings module for the 'celery' program.
# Make sure 'chatproject' is spelled correctly here!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatproject.settings')

app = Celery('chatproject')

# 2. Use a string here so the worker doesn't have to serialize
# the configuration object to child processes.
# namespace='CELERY' means all celery-related configs must have a CELERY_ prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 3. Load task modules from all registered Django apps.
app.autodiscover_tasks()