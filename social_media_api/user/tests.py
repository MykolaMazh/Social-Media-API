from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


REGISTER_URL = reverse("user:register_user")
ME_URL = reverse("user:me")
USERS_URL = reverse("user:users")


class UserApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

    def test_register_user(self):
        payload = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "about_me": "Hello",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user_exists = User.objects.filter(email=payload["email"]).exists()
        self.assertTrue(user_exists)

    def test_update_current_user(self):
        user1 = User.objects.create_user(
            email="test11@example.com",
            password="testpass123",
        )
        user2 = User.objects.create_user(
            email="test2@example.com",
            password="testpass1234",
        )
        self.client.force_authenticate(self.user)
        payload = {
            "about_me": "Updated about me",
            "following": [user1.pk, user2.pk],
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.about_me, payload["about_me"])
        following_users = self.user.following.all()
        self.assertTrue(
            all(user in following_users for user in [user1, user2])
        )

    def test_no_way_update_email(self):
        self.client.force_authenticate(self.user)
        payload = {
            "email": "new_email@gmail.com",
        }
        self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, payload["email"])


class PostApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

    def test_register_user(self):
        payload = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "about_me": "Hello",
        }
        res = self.client.post(REGISTER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user_exists = User.objects.filter(email=payload["email"]).exists()
        self.assertTrue(user_exists)

    def test_update_current_user(self):
        user1 = User.objects.create_user(
            email="test11@example.com",
            password="testpass123",
        )
        user2 = User.objects.create_user(
            email="test2@example.com",
            password="testpass1234",
        )
        self.client.force_authenticate(self.user)
        payload = {
            "about_me": "Updated about me",
            "following": [user1.pk, user2.pk],
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.about_me, payload["about_me"])
        following_users = self.user.following.all()
        self.assertTrue(
            all(user in following_users for user in [user1, user2])
        )

    def test_no_way_update_email(self):
        self.client.force_authenticate(self.user)
        payload = {
            "email": "new_email@gmail.com",
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, payload["email"])
