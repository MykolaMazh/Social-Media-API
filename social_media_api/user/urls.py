from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from user.views import (
    CreateUserView,
    LogoutView,
    RetrieveUpdateUserView,
    ListUserView,
    RetrieveUserView,
)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register_user"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/logout/", LogoutView.as_view(), name="invalidate_refresh"),
    path("me/", RetrieveUpdateUserView.as_view(), name="me"),
    path("users/", ListUserView.as_view(), name="users"),
    path("users/<int:pk>/", RetrieveUserView.as_view(), name="users"),
]

app_name = "user"
