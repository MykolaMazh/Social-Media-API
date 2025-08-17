from django.db import models
from django.conf import settings


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
    tags = models.ManyToManyField(Tag, blank=True)
    liked = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="likes"
    )
    disliked = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="dislikes"
    )

    def like(self, user):
        """Add user to liked, remove from disliked."""
        self.disliked.remove(user)
        self.liked.add(user)

    def dislike(self, user):
        """Add user to disliked, remove from liked."""
        self.liked.remove(user)
        self.disliked.add(user)

    def __str__(self) -> str:
        return f"{self.title}/{self.author}"


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    commented_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.author)
