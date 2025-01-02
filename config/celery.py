import os
import warnings

import django
from celery import Celery

warnings.filterwarnings("ignore")


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
os.environ.setdefault("FLOWER_UNAUTHENTICATED_API", "true")

django.setup()

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(related_name="tasks")
