from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS 


class IsAuthor(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAuthorOrSafeMethodOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user
                or request.method in SAFE_METHODS
                or request.user.is_staff)


class IsYourShopCart(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return (obj.author == request.user)
