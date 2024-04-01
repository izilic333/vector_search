import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vidoso.settings')

app = Celery('search_engine')
# app.loader.override_backends['django-db'] = 'django_celery_results.backends.database:DatabaseBackend'


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    return f'Request: {self.request!r}'
