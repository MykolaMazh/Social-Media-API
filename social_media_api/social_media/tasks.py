from celery import shared_task
from django.urls import reverse
import requests

BASE_URL = "http://127.0.0.1:8000"
POST_LIST_URL = reverse("social_media:post-list")


@shared_task
def post_post():
    print(POST_LIST_URL)
    response = requests.get(f"{BASE_URL}{POST_LIST_URL}")
    return response.content
