from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Model
from rest_framework.permissions import DjangoModelPermissions  # noqa F401
from rest_framework.permissions import IsAuthenticated  # noqa F401
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.routers import APIRootView


class BanPermission(BasePermission):
    """Базовый класс разрешений с проверкой - забанен ли пользователь."""

    def has_permission(self, request: WSGIRequest, view: APIRootView) -> bool:
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
        )


class AdminOrReadOnly(BanPermission):
    """
    Разрешение на создание и изменение только для админов.
    Остальным только чтение объекта.
    """

    def has_object_permission(
        self, request: WSGIRequest, view: APIRootView
    ) -> bool:
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user.is_staff
        )


class IsAdminOrAuthorOrReadOnlyPermission(BasePermission):
    """
    Проверка пользователя на автора или админа
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
        )

class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS