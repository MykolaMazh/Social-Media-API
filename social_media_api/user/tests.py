from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from social_media.models import Post

User = get_user_model()


REGISTER_URL = reverse("user:register_user")
ME_URL = reverse("user:me")
USERS_URL = reverse("user:users")
POST_URL_LIST = reverse("social_media:post-list")


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
        self.client.force_authenticate(self.user)

    def test_user_posts_access(self):
        payload = {
            "title": "Test post.",
            "content": "This is my test post.",
        }

        res = self.client.post(POST_URL_LIST, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.filter(author=self.user).first()
        self.assertIsNotNone(post, msg="The post should have been created")

        self.client.force_authenticate(user=None)

        res = self.client.post(POST_URL_LIST, payload)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
            msg="An unauthenticated user can't create",
        )

        res = self.client.get(POST_URL_LIST)
        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
            msg="An unauthenticated user should be able to list",
        )

        res = self.client.get(f"{POST_URL_LIST}{post.id}/")
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
            msg="An unauthenticated user shouldn’t be able to retrieve",
        )

    def test_staff_can_delete_posts(self):
        payload = {
            "title": "Test post.",
            "content": "This is my test post.",
        }

        self.client.post(POST_URL_LIST, payload)
        post = Post.objects.filter(author=self.user).first()

        staff_user = User.objects.create_user(
            email="staff@example.com", password="staffuser", is_staff=True
        )

        self.client.force_authenticate(user=staff_user)

        res = self.client.patch(
            f"{POST_URL_LIST}{post.id}/", {"title": "Title edited"}
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="Only author can edit the post",
        )

        res = self.client.delete(f"{POST_URL_LIST}{post.id}/")
        self.assertEqual(
            res.status_code,
            status.HTTP_204_NO_CONTENT,
            msg="Staff should be able to delete any post.",
        )
