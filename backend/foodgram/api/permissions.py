from rest_framework import permissions


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user)


class IsAuthorOrSafeMethodOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.method in ("GET", "HEAD", "OPTIONS")
                or request.user.is_staff)


class IsYourShopCart(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user)
