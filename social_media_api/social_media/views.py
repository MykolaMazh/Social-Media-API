from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model

from social_media.models import Post
from social_media.serializers import PostSerializer

User = get_user_model()


class PostViewSet(ModelViewSet):
    queryset = Post.objects.select_related("author").all()
    serializer_class = PostSerializer
