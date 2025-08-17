from rest_framework import serializers

# from django.contrib.auth import get_user_model

from social_media.models import Post
from user.serializers import UserShortSerializer

# User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    author = UserShortSerializer()

    class Meta:
        model = Post
        fields = ["id", "title", "author", "content", "photo", "tags"]
