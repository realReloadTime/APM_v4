import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.system import SystemRepository, SystemService
from core.models import System
from core.auth import async_permission_required, async_api_method


async def get_system_service():
    return SystemService(SystemRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_system(request):
    service = await get_system_service()

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            system = await service.create_system(data)
            return JsonResponse(system, status=201)
        else:
            system = await service.get_system()
            return JsonResponse(system, status=200, safe=False)

    except System.DoesNotExist:
        return JsonResponse({'error': 'System not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_system_detail(request, system_id: int):
    service = await get_system_service()

    try:
        system = await service.get_system(system_id)
        return JsonResponse(system, status=200)

    except System.DoesNotExist:
        return JsonResponse({'error': 'System not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': other_err}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_system(request, system_id: int):
    service = await get_system_service()
    data = json.loads(request.body)
    try:
        system = await service.update_system(system_id, data)
        return JsonResponse(system, status=200)

    except Exception as other_err:
        return JsonResponse({'error': other_err}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_system(request, system_id: int):
    service = await get_system_service()

    try:
        assert await service.delete_system(system_id)
        return HttpResponse(status=204)

    except System.DoesNotExist:
        return JsonResponse(
        {'msg': 'System not found'},
        status=404
    )

    except AssertionError:
        return JsonResponse(
        {'error': "Error on System deletion"},
        status=404
    )
