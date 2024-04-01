from celery import shared_task
from django.core.management import call_command


@shared_task
def task_populate_article_chunks(*args, **kwargs):
    call_command('populate_article_chunks', *args, **kwargs)
