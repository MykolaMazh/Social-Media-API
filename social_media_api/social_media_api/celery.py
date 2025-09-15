import os
from celery import Celery
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "social_media_api.settings.dev"
)

app = Celery(
    "social_media_api", broker="redis://localhost", backend="redis://localhost"
)
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.enable_utc = False
app.conf.timezone = settings.TIME_ZONE

app.autodiscover_tasks()
