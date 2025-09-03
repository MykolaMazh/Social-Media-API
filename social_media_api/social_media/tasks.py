from celery import shared_task
from django.urls import reverse
import requests

from social_media.models import Post

BASE_URL = "http://127.0.0.1:8000"
POST_LIST_URL = reverse("social_media:post-list")
HEADER = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU3NDQ0OTkxLCJpYXQiOjE3NTY1ODA5OTEsImp0aSI6IjllZDVmMTc1YjY0NDRkNTViNzVjMGI4NDMzM2QwYmJjIiwidXNlcl9pZCI6IjQifQ.rS9-It9ecjYvK3CxsI5FGio-sH4jmlKghLGL1vyOhC4"


POST = {
    "title": "Man City transfers: Donnarumma completes move as Ederson exits",
    "content": """Manchester City have completed the signing of goalkeeper Gianluigi Donnarumma from Paris Saint-Germain.

The Italy international has moved to the Etihad Stadium in a deal worth €30 million ($40.2m). He's signed a five-year contract to replace Ederson in Pep Guardiola's squad.
Ederson's eight-year stay at City is at an end after the Brazilian joined Fenerbahce for €14m.
"To have signed for Manchester City is such a special and proud moment for me," said Donnarumma.
"I am joining a squad packed with world-class talent and a team led by the one of the greatest managers in the history of football in Pep Guardiola.

""",
    "tags": [2, 3],
}

POST_IMG = "/home/nickolasso/Downloads/dolaruma.jpeg"


@shared_task
def post_publish():
    with open(POST_IMG, "rb") as image:
        response = requests.post(
            f"{BASE_URL}{POST_LIST_URL}",
            data=POST,
            headers={"Authorization": HEADER},
            files={"photo": image},
        )
    return response.content
