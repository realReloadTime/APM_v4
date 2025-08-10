from asgiref.sync import sync_to_async
from asyncpg import InternalServerError

from django.http import JsonResponse, HttpResponse

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

import json

from core.logic.user import UserService, UserRepository
from core.models import CustomUser
from core.serializers import RegisterSerializer
from core.auth import async_permission_required, async_api_method


async def get_user_service():
    return UserService(UserRepository())


# регистрация (email, password)
@async_api_method(['POST'])
async def register(request):
    data = json.loads(request.body)
    serializer = RegisterSerializer(data=data)

    if await sync_to_async(serializer.is_valid)():
        user = await sync_to_async(serializer.save)()
        refresh = await sync_to_async(RefreshToken.for_user)(user)
        return JsonResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=201)

    return JsonResponse(serializer.errors, status=400)


# авторизация (email, password)
@async_api_method(['POST'])
async def login(request):
    data = json.loads(request.body)
    email = data.get('email')
    password = data.get('password')

    try:
        user = await CustomUser.objects.aget(email=email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)

    if await sync_to_async(user.check_password)(password):
        refresh = await sync_to_async(RefreshToken.for_user)(user)
        return JsonResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    return JsonResponse({'error': 'Invalid credentials'}, status=401)


@async_api_method(['POST'])
async def refresh_auth_token(request=None):
    try:
        refresh_token = json.loads(request.body)['refresh']
        new_access = await sync_to_async(RefreshToken)(refresh_token)
        return JsonResponse({"access": str(new_access.access_token)}, status=205)

    except ValueError or InternalServerError:
        JsonResponse({'error': 'Invalid key name or body.'}, status=400)
    except Exception as other_ex:
        JsonResponse({'error': str(other_ex), 'error_type': str(other_ex.__class__)}, status=404)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_user_self(request):
    service = await get_user_service()

    try:
        return JsonResponse(await service.get_me_as_user(request.user))
    except Exception as err:
        return JsonResponse({'error': str(err)}, status=400)

# получение пользователя по ID
@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def user_detail(request, user_id):
    service = await get_user_service()
    try:
        user = await service.get_user(user_id)
        return JsonResponse(user)

    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


# cписок всех пользователей
@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def user_list(request):
    service = await get_user_service()

    try:
        users = await service.get_user()
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)

    return JsonResponse(users, safe=False)


# обновление пользователя
@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def user_update(request, user_id: int):
    service = await get_user_service()
    data = json.loads(request.body)
    try:
        user = await service.update_user(user_id, data)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)

    return JsonResponse(user)


# удаление пользователя
@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def user_delete(request, user_id):
    service = await get_user_service()
    try:
        assert await service.delete_user(user_id)
        return HttpResponse(status=204)
    except CustomUser.DoesNotExist:
        return JsonResponse(
            {'msg': 'User not found'},
            status=404
        )

    except AssertionError:
        return JsonResponse(
            {'error': "Error on user deletion"},
            status=404
        )
