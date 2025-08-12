from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    extend_schema,
    OpenApiExample,
    OpenApiResponse,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes
from typing import List

from user.serializers import (
    UserUpdateSerializer,
    UserListSerializer,
    UserRetrieveSerializer,
    UserCreateSerializer,
)

User = get_user_model()


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({"message": "Successfully logged out"}, status=200)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=400)


class ListUserView(generics.ListAPIView):
    serializer_class = UserListSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        search_email = self.request.query_params.get("email")
        posts = self.request.query_params.get("posts")
        followers = self.request.query_params.get("followers")
        reacted = self.request.query_params.get("reacted")
        if search_email:
            queryset = queryset.filter(email__icontains=search_email)
        queryset = queryset.annotate(
            posts_written=Count("posts"),
            followers_count=Count("followers"),
            total_likes=Sum("posts__liked"),
            total_dislikes=Sum("posts__disliked"),
            reactions=F("total_likes") + F("total_dislikes"),
        )
        if posts:
            queryset = queryset.filter(posts_written__gte=posts)
        if followers:
            queryset = queryset.filter(followers_count__gte=followers)
        if reacted:
            queryset = queryset.filter(reactions__gte=reacted)
        return queryset


class RetrieveUserView(generics.RetrieveAPIView):
    serializer_class = UserRetrieveSerializer
    queryset = User.objects.annotate(
        posts_written=Count("posts"),
        followers_count=Count("followers"),
        total_likes=Sum("posts__liked"),
        total_dislikes=Sum("posts__disliked"),
    ).prefetch_related("followers")


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return (
            User.objects.annotate(
                posts_written=Count("posts"),
                followers_count=Count("followers"),
                total_likes=Sum("posts__liked"),
                total_dislikes=Sum("posts__disliked"),
            )
            .prefetch_related("followers")
            .get(pk=self.request.user.pk)
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserRetrieveSerializer
        return UserUpdateSerializer


class FollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Follow the user",
        description="Follow the user with no request body",
        parameters=[
            OpenApiParameter(
                name="id",
                description="The ID of the user to follow",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.JSON_PTR,
                description="Following the user",
                examples=[
                    OpenApiExample(
                        name="Successfull followed",
                        value={
                            "message": "You are now following 'user2@gmail.com'."
                        },
                    ),
                    OpenApiExample(
                        name="Already followed",
                        value={
                            "message": "You already follow 'user2@gmail.com'."
                        },
                    ),
                ],
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.JSON_PTR,
                description="Following yourself",
                examples=[
                    OpenApiExample(
                        name="Can't follow",
                        value={"error": "You cannot follow yourself."},
                        description="trying to follow yourself",
                    ),
                ],
            ),
        },
    )
    def patch(self, request, pk):
        user = request.user
        user_to_follow = get_object_or_404(User, pk=pk)
        if user == user_to_follow:
            return Response(
                {"error": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user_to_follow in user.following.all():
            return Response(
                {"message": f"You already follow '{user_to_follow.email}'."},
                status=status.HTTP_200_OK,
            )

        user.following.add(user_to_follow)
        return Response(
            {"message": f"You are now following '{user_to_follow.email}'."},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Unfollow the user",
        description="Unfollow the user with no request body",
        parameters=[
            OpenApiParameter(
                name="id",
                description="The ID of the user to unfollow",
                required=True,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
            )
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.JSON_PTR,
                description="Unfollowing the user",
                examples=[
                    OpenApiExample(
                        name="Successfull",
                        value={
                            "message": "You are now not follow 'user2@gmail.com'."
                        },
                    )
                ],
            )
        },
    )
    def delete(self, request, pk):
        user = request.user
        user_to_follow = get_object_or_404(User, pk=pk)

        user.following.remove(user_to_follow)
        return Response(
            {"message": f"You are now not follow '{user_to_follow.email}'."},
            status=status.HTTP_200_OK,
        )
