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

    def create_post(self):
        payload = {
            "title": "Test post.",
            "content": "This is my test post.",
        }

        self.res = self.client.post(POST_URL_LIST, payload)
        self.post = Post.objects.first()
        self.post_url_detail = reverse(
            "social_media:post-detail", args=[self.post.id]
        )

    def create_user(self, user: str, **kwargs):
        new_user = User.objects.create_user(
            email=f"{user}@example.com", password=f"{user}test", **kwargs
        )
        self.client.force_authenticate(new_user)
        return new_user

    def test_user_posts_access(self):
        self.create_post()
        self.assertEqual(self.res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(
            self.post, msg="The post should have been created"
        )

        self.client.force_authenticate(user=None)

        res = self.client.post(
            POST_URL_LIST,
            {
                "title": "Non User Post.",
                "content": "Post of unauthorized user.",
            },
        )
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

        res = self.client.get(self.post_url_detail)
        self.assertEqual(
            res.status_code,
            status.HTTP_401_UNAUTHORIZED,
            msg="An unauthenticated user shouldn’t be able to retrieve",
        )

    def test_staff_can_delete_posts(self):
        self.create_post()
        staff_user = self.create_user("staffuser", is_staff=True)

        res = self.client.patch(
            self.post_url_detail,
            {"title": "Title edited"},
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="Only author can edit the post",
        )

        res = self.client.delete(self.post_url_detail)
        self.assertEqual(
            res.status_code,
            status.HTTP_204_NO_CONTENT,
            msg="Staff should be able to delete any post.",
        )

    def test_no_like_own_post(self):
        self.create_post()
        res = self.client.patch(
            reverse("social_media:post-like", kwargs={"pk": self.post.pk})
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="The author can’t like their own posts.",
        )

    def test_add_remove_likes(self):
        self.create_post()

        self.create_user("user1")
        self.client.patch(
            reverse("social_media:post-like", args=[self.post.pk])
        )

        self.create_user("user2")
        self.client.patch(
            reverse("social_media:post-like", args=[self.post.pk])
        )
        self.client.patch(
            reverse("social_media:post-unlike", args=[self.post.pk])
        )

        self.post.refresh_from_db()
        likes = self.post.liked.count()
        self.assertEqual(likes, 1)

    def test_add_remove_dislikes(self):
        self.create_post()

        self.create_user("user1")
        self.client.patch(
            reverse("social_media:post-dislike", args=[self.post.pk])
        )

        self.create_user("user2")
        self.client.patch(
            reverse("social_media:post-dislike", args=[self.post.pk])
        )
        self.client.patch(
            reverse("social_media:post-undislike", args=[self.post.pk])
        )

        self.post.refresh_from_db()
        dislikes = self.post.disliked.count()
        self.assertEqual(dislikes, 1)

    def test_dislike_like_mutually_exclusive(self):
        self.create_post()
        self.create_user("user")
        self.client.patch(
            reverse("social_media:post-like", args=[self.post.pk])
        )
        self.client.patch(
            reverse("social_media:post-dislike", args=[self.post.pk])
        )
        likes = self.post.liked.count()
        dislikes = self.post.disliked.count()
        self.assertEqual((likes, dislikes), (0, 1))
        self.client.patch(
            reverse("social_media:post-like", args=[self.post.pk])
        )
        self.post.refresh_from_db()
        likes = self.post.liked.count()
        dislikes = self.post.disliked.count()
        self.assertEqual((likes, dislikes), (1, 0))
