from asgiref.sync import sync_to_async

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django.http import JsonResponse

from core.models import CustomUser


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
            print(f"User authenticated: {request.user.is_authenticated}")  # ДЛЯ ОТЛАДКИ, УДАЛИТЬ!!
            print(request.user)
            if request.method not in methods:
                return JsonResponse({'error': 'Method not allowed'}, status=405)
            return await view_func(request, *args, **kwargs)

        return wrapped_view

    return decorator


@sync_to_async
def check_user_permisssion(user: CustomUser, permission: str = 'read'):  # проверка доступа пользователя к функционалу
    return user.has_perm(permission)
