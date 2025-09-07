from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from social_media.models import Post, Comment

User = get_user_model()


REGISTER = "user:register_user"
ME = "user:me"
USERS = "user:users"
POST_LIST = "social_media:post-list"
POST_DETAIL = "social_media:post-detail"
POST_LIKE = "social_media:post-like"
POST_DISLIKE = "social_media:post-dislike"
POST_COMMENT = "social_media:post-comment"
FOLLOW = "user:follow"
FOLLOWERS = "user:followers_list"
FOLLOWING = "user:following_list"
COMMENT_LIST = "social_media:comment-list"
COMMENT_DETAIL = "social_media:comment-detail"


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
        res = self.client.post(reverse(REGISTER), payload)
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
        res = self.client.patch(reverse(ME), payload)
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
        self.client.patch(reverse(ME), payload)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.email, payload["email"])

    def test_follow_user(self):
        user1 = User.objects.create_user(
            email="test1@example.com",
            password="testpass123",
        )
        user2 = User.objects.create_user(
            email="test2@example.com",
            password="testpass123",
        )

        self.client.force_authenticate(user1)
        self.client.patch(reverse(FOLLOW, args=[self.user.id]))
        self.client.patch(reverse(FOLLOW, args=[user2.id]))
        res = self.client.get(reverse(FOLLOWING))
        self.assertEqual(
            len(res.data),
            2,
            msg="The length of the list of following users should be equal "
            "to number of times the user follow another users.",
        )

        self.client.delete(reverse(FOLLOW, args=[user2.id]))
        res = self.client.get(reverse(FOLLOWING))
        self.assertEqual(
            len(res.data),
            1,
            msg="delete request should unfollow an user",
        )

        self.client.force_authenticate(user2)
        self.client.patch(reverse(FOLLOW, args=[self.user.id]))

        self.client.force_authenticate(self.user)
        res = self.client.get(reverse(FOLLOWERS))
        self.assertEqual(
            len(res.data),
            2,
            msg="The length of the list of followers should be equal to the "
            "number of times the user has been followed by other users.",
        )


class PostApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.create_user("user0")

    def create_post(self):
        payload = {
            "title": "Test post.",
            "content": "This is my test post.",
        }

        self.res = self.client.post(reverse(POST_LIST), payload)
        self.post = Post.objects.order_by("id").last()
        self.post_url_detail = reverse(POST_DETAIL, args=[self.post.id])
        self.post.refresh_from_db()
        return self.post

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
            reverse(POST_LIST),
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

        res = self.client.get(reverse(POST_LIST))
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
        self.create_user("staffuser", is_staff=True)
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
            reverse(POST_LIKE, kwargs={"pk": self.post.pk})
        )
        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
            msg="The author can’t like their own posts.",
        )

    def test_add_remove_likes(self):
        self.create_post()

        self.create_user("user1")
        self.client.patch(reverse(POST_LIKE, args=[self.post.pk]))

        self.create_user("user2")
        self.client.patch(reverse(POST_LIKE, args=[self.post.pk]))
        self.client.patch(
            reverse("social_media:post-unlike", args=[self.post.pk])
        )

        self.post.refresh_from_db()
        likes = self.post.liked.count()
        self.assertEqual(likes, 1)

    def test_add_remove_dislikes(self):
        self.create_post()

        self.create_user("user1")
        self.client.patch(reverse(POST_DISLIKE, args=[self.post.pk]))

        self.create_user("user2")
        self.client.patch(reverse(POST_DISLIKE, args=[self.post.pk]))
        self.client.patch(
            reverse("social_media:post-undislike", args=[self.post.pk])
        )

        self.post.refresh_from_db()
        dislikes = self.post.disliked.count()
        self.assertEqual(dislikes, 1)

    def test_dislike_like_mutually_exclusive(self):
        self.create_post()
        self.create_user("user1")
        self.client.patch(reverse(POST_LIKE, args=[self.post.pk]))
        self.client.patch(reverse(POST_DISLIKE, args=[self.post.pk]))
        likes = self.post.liked.count()
        dislikes = self.post.disliked.count()
        self.assertEqual((likes, dislikes), (0, 1))
        self.client.patch(reverse(POST_LIKE, args=[self.post.pk]))
        self.post.refresh_from_db()
        likes = self.post.liked.count()
        dislikes = self.post.disliked.count()
        self.assertEqual((likes, dislikes), (1, 0))

    def test_liked_post_list(self):
        self.create_post()
        post1 = self.create_post()
        post3 = self.create_post()
        self.create_user("user1")
        self.client.patch(reverse(POST_LIKE, args=[post1.pk]))
        self.client.patch(reverse(POST_LIKE, args=[post3.pk]))
        res = self.client.get(reverse("social_media:post-liked"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)


class CommentApiTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email="user1@gmail.com", password="user1password"
        )
        self.user2 = User.objects.create_user(
            email="user2@gmail.com", password="user2password"
        )
        payload = {
            "title": "test post",
            "content": "Test post content.",
        }
        self.client.force_authenticate(self.user1)
        self.client.post(reverse(POST_LIST), data=payload)
        self.post = Post.objects.first()

    def test_only_own_comment_access(self):

        self.client.force_authenticate(self.user2)
        res = self.client.post(
            reverse(COMMENT_LIST),
            data={"content": "I fully agree.", "post": self.post.id},
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        edited_content = "Awful post."
        self.client.patch(
            reverse(COMMENT_DETAIL, kwargs={"pk": self.post.id}),
            data={"content": edited_content},
        )
        comment = Comment.objects.first()
        self.assertEqual(comment.content, edited_content)

        self.client.force_authenticate(self.user1)
        edited_content_2 = "Great!!!"
        res = self.client.patch(
            reverse(COMMENT_DETAIL, kwargs={"pk": self.post.id}),
            data={"content": edited_content_2},
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, edited_content_2)

    def test_can_comment_with_action(self):
        self.client.force_authenticate(self.user2)
        comment_content = "New comment"
        res = self.client.post(
            reverse(POST_COMMENT, args=[self.post.id]),
            data={"content": comment_content, "post": self.post.id},
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, comment_content)
