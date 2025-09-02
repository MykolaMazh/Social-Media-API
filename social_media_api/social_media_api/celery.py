import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_media_api.settings")

app = Celery(
    "social_media_api", broker="redis://localhost", backend="redis://localhost"
)
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
