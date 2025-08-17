from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from social_media.models import Post, Tag
from social_media.serializers import PostSerializer, TagSerializer
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly

User = get_user_model()


class PostViewSet(ModelViewSet):
    queryset = Post.objects.select_related("author").prefetch_related("tags")
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=["get"])
    def mine(self, request):
        posts = self.get_queryset().filter(author=self.request.user)
        serializer = self.get_serializer(posts, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def following(self, request):
        user = self.request.user
        following_users = user.following.all()
        posts = self.get_queryset().filter(author__in=following_users)
        serializer = self.get_serializer(posts, many=True)

        return Response(serializer.data)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
