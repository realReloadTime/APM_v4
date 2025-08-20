import json

from asgiref.sync import sync_to_async

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from django.http import JsonResponse


async def authenticate_request(request):
    auth = JWTAuthentication()
    try:
        user_auth_tuple = await sync_to_async(auth.authenticate)(request)
        if user_auth_tuple is not None:
            request.user, request.auth = user_auth_tuple
            return True
    except AuthenticationFailed:
        return False
    return False


def async_permission_required(permission_classes):
    def decorator(view_func):
        async def wrapped_view(request, *args, **kwargs):
            # пытаемся аутентифицировать через JWT
            if not await authenticate_request(request):
                return JsonResponse({'error': 'Authentication failed'}, status=401)

            # проверяем все разрешения
            for permission_class in permission_classes:
                permission = permission_class()
                if not await sync_to_async(permission.has_permission)(request, None):
                    return JsonResponse({'error': 'Permission denied'}, status=403)
            return await view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


# кастомный декоратор для обработки методов запросов (GET, POST, PUT и т.д.)
def async_api_method(methods):
    def decorator(view_func):
        async def wrapped_view(request, *args, **kwargs):
            if request.method not in methods:
                return JsonResponse({'error': 'Method not allowed'}, status=405)
            return await view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


class HasReadPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.read if request.user.profile else False


class HasEditPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.profile.edit if request.user.profile else False


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin


class HasLOAAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_admin:
            return True
        if not request.user.loa:
            return False
        # Для list(GET) — фильтрация в view, так что permission ок
        if request.method in ['POST', 'PUT']:
            data = json.loads(request.body) if request.body else {}
            loa_id = data.get('loa_id')
            return loa_id == request.user.loa.id
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        if not request.user.loa:
            return False
        # Проверяем, что объект (например, Event) связан с user.loa
        return obj.loa == request.user.loa  # Предполагаем, что obj имеет поле loa
