from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firstProject.settings')

app = Celery('firstProject')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.broker_url = 'redis://localhost:6379/0'

app.autodiscover_tasks()
