from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from rest_framework import generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from user.serializers import (
    UserUpdateSerializer,
    UserListSerializer,
    UserRetrieveSerializer,
    UserCreateSerializer,
)


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
        return get_user_model().objects.annotate(
            posts_written=Count("posts"),
            followers_count=Count("followers"),
            total_likes=Sum("posts__liked"),
            total_dislikes=Sum("posts__disliked"),
        )


class RetrieveUserView(generics.RetrieveAPIView):
    serializer_class = UserRetrieveSerializer
    queryset = (
        get_user_model()
        .objects.annotate(
            posts_written=Count("posts"),
            followers_count=Count("followers"),
            total_likes=Sum("posts__liked"),
            total_dislikes=Sum("posts__disliked"),
        )
        .prefetch_related("followers")
    )


class RetrieveUpdateUserView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return (
            get_user_model()
            .objects.annotate(
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
