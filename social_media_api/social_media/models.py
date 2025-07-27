from django.db import models
from django.conf import settings


class Tag(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to="photoes/%Y/%m/%d/", blank=True, null=True)
    views = models.IntegerField(editable=False, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    liked = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="posts_liked"
    )

    def __str__(self) -> str:
        return f"{self.title}/{self.author}"


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    commented_date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")

    def __str__(self) -> str:
        return self.author
