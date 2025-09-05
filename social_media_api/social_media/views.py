from django.db.models.aggregates import Count
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import F
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from social_media.models import Post, Tag, Comment
from social_media.tasks import post_publish
from social_media.serializers import (
    PostSerializer,
    TagSerializer,
    CommentSerializer,
    PostRetrieveSerializer,
)
from .permissions import (
    IsAuthorOrReadOnly,
    IsAdminOrReadOnly,
    IsAuthenticatedAndNotAuthor,
)

User = get_user_model()


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
    queryset = Post.objects.all()

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        if post.publish_at:
            post_publish.apply_async(eta=post.publish_at, args=[post.id])
        else:
            post.is_published = True
            post.save()

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

    def _handle_reaction(self, request, action_type: str, undo: bool = False):
        user = request.user
        post = self.get_object()
        if post.author == user:
            return Response(
                {"error": "You cannot react to your own post."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        like_exists = post.liked.filter(id=user.id).exists()
        dislike_exists = post.disliked.filter(id=user.id).exists()
        if action_type == "like":
            if undo and like_exists:
                post.liked.remove(user)
            else:
                if dislike_exists:
                    post.disliked.remove(user)
                post.liked.add(user)
        elif action_type == "dislike":
            if undo and dislike_exists:
                post.disliked.remove(user)
            else:
                if like_exists:
                    post.liked.remove(user)
                post.disliked.add(user)
        action_verb = action_type if not undo else f"do not {action_type}"
        return Response(
            {
                "message": (
                    f'You {action_verb} "{post.title}" by {post.author} '
                    f'from {post.created_at.strftime("%A %d %b %Y %H:%M:%S")}'
                )
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[IsAuthenticatedAndNotAuthor],
    )
    def like(self, request, pk):
        return self._handle_reaction(request, "like")

    @action(
        detail=True,
        methods=["patch"],
        url_name="unlike",
        permission_classes=[IsAuthenticatedAndNotAuthor],
    )
    def like_remove(self, request, pk):
        return self._handle_reaction(request, "like", undo=True)

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[IsAuthenticatedAndNotAuthor],
    )
    def dislike(self, request, pk):
        return self._handle_reaction(request, "dislike")

    @action(
        detail=True,
        methods=["patch"],
        permission_classes=[IsAuthenticatedAndNotAuthor],
        url_name="undislike",
    )
    def dislike_remove(self, request, pk):
        return self._handle_reaction(request, "dislike", undo=True)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
    )
    def liked(self, request):
        posts = self.get_queryset().filter(liked=request.user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        serializer_class=CommentSerializer,
    )
    def comment(self, request, pk):
        post = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        if user != instance.author and user not in instance.viewers.all():
            instance.views = F("views") + 1
            instance.viewers.add(user)
            instance.save()
            instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = (
            Post.objects.filter(is_published=True)
            .select_related("author")
            .prefetch_related("tags", "comments__author")
            .annotate(
                likes=Count("liked"),
                dislikes=Count("disliked"),
                comments_number=Count("comments"),
            )
        )
        tags = self.request.query_params.getlist("tag")

        author = self.request.query_params.get("author")
        if tags:
            queryset = queryset.filter(tags__title__in=tags).distinct()
        if author:
            queryset = queryset.filter(author__email__icontains=author)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostRetrieveSerializer
        return PostSerializer


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.select_related("author", "post", "post__author")
    serializer_class = CommentSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == "list":
            return [IsAdminUser()]
        return [IsAuthorOrReadOnly()]

    @extend_schema(
        summary="Only for admin users",
        description="Endpoint needs admin authorization.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
