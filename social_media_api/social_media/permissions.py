from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.method == "POST" and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            and request.user.is_authenticated
            or obj.author == request.user
            or (request.method == "DELETE" and request.user.is_staff)
            or (request.method == "POST" and request.user.is_authenticated)
        )


class IsAuthenticatedAndNotAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.author != request.user


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS) or (
            request.user and request.user.is_staff
        )
