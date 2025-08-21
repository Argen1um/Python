import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPortal.settings')

app = Celery('NewsPortal')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-weekly-articles': {
        'task': 'news_portal.tasks.send_weekly_articles',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Понедельник 8:00
    },
}