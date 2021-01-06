"""
Подключение и настройки обработчика очереди(Celery).
"""
from celery import Celery
from .read_config import *

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')


app = Celery(PROJECT_NAME)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
