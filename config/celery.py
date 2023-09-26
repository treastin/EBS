from celery import Celery
from celery.schedules import crontab
import os

from config import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery("config", broker=settings.CELERY_BROKER)

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-mail': {
        'task': 'apps.tasks.tasks.send_mail_func',
        'schedule': crontab(hour='9') # noqa
    }

}
