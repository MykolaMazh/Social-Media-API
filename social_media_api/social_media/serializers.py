from rest_framework import serializers

# from django.contrib.auth import get_user_model

from social_media.models import Post, Tag
from user.serializers import UserShortSerializer

# User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "title"]


class PostSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "title", "author", "content", "photo", "tags"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if request and request.method in ["POST", "PUT", "PATCH"]:
            self.fields["tags"] = serializers.PrimaryKeyRelatedField(
                many=True, queryset=Tag.objects.all()
            )
        else:
            self.fields["tags"] = TagSerializer(many=True, read_only=True)
