from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.ImageField(
        upload_to="post_images/%Y/%m/%d/", blank=True, null=True
    )
    views = models.IntegerField(editable=False, default=0)
    viewers = models.ManyToManyField(
        User, related_name="viewed_posts", blank=True
    )
    tags = models.ManyToManyField(Tag, blank=True)
    liked = models.ManyToManyField(User, blank=True, related_name="likes")
    disliked = models.ManyToManyField(
        User, blank=True, related_name="dislikes"
    )

    def __str__(self) -> str:
        return f"{self.title}/{self.author}"


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.post)
