from rest_framework import serializers

# from django.contrib.auth import get_user_model

from social_media.models import Post, Tag, Comment
from user.serializers import UserShortSerializer

# User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "title"]


class PostSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    likes = serializers.IntegerField(read_only=True)
    dislikes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "author",
            "content",
            "photo",
            "tags",
            "views",
            "likes",
            "dislikes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method in ["POST", "PUT", "PATCH"]:
            self.fields["tags"] = serializers.PrimaryKeyRelatedField(
                many=True, queryset=Tag.objects.all(), required=False
            )
        else:
            self.fields["tags"] = TagSerializer(many=True, read_only=True)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    post = serializers.SlugRelatedField(slug_field="title", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "author",
            "content",
            "post",
            "created_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method == "POST":
            self.fields["post"] = serializers.PrimaryKeyRelatedField(
                queryset=Post.objects.all()
            )
