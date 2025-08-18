from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import F

from social_media.models import Post, Tag
from social_media.serializers import PostSerializer, TagSerializer
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiResponse,
    OpenApiExample,
)

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

    @extend_schema(
        summary="Post list",
        description="Get a list of posts, search by criteria.",
        parameters=[
            OpenApiParameter(
                name="tag",
                description="Search by tag name, cab be multiple search (?tag=movies&tag=celebrities)",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="author",
                description="Search by author email, case-insensitive",
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        request=PostSerializer(),
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if user != instance.author:
            instance.views = F("views") + 1
            instance.save()
            instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.getlist("tag")

        author = self.request.query_params.get("author")
        if tags:
            queryset = queryset.filter(tags__title__in=tags).distinct()
        if author:
            queryset = queryset.filter(author__email__icontains=author)
        return queryset


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
