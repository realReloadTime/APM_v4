from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

import json

from core.logic.subsystem import SubsystemRepository, SubsystemService
from core.auth import async_permission_required, async_api_method


async def get_subsystem_service():
    return SubsystemService(SubsystemRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_subsystem(request):
    service = await get_subsystem_service()
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            subsystem = await service.create_subsystem(data)
            return JsonResponse(subsystem, status=201)
        else:  # GET
            subsystems = await service.get_subsystem()
            return JsonResponse(subsystems, safe=False, status=200)

    except ValueError as ve:
        return JsonResponse({'error': ve}, status=400)

    except Exception as other_err:
        return JsonResponse({'error': other_err}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def subsystem_detail(request, subsystem_id: int):
    service = await get_subsystem_service()
    try:
        subsystem = await service.get_subsystem(subsystem_id)
        return JsonResponse(subsystem, status=200)

    except ValueError as ve:
        return JsonResponse({'error': ve}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': other_err}, status=400)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def subsystem_update(request, subsystem_id: int):
    service = await get_subsystem_service()
    try:
        data = json.loads(request.body)
        subsystem = await service.update_subsystem(subsystem_id, data)
        return JsonResponse(subsystem, status=200)
    
    except ValueError as ve:
        return JsonResponse({'error': ve}, status=400)
    
    except Exception as other_err:
        return JsonResponse({'error': other_err}, status=400)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def subsystem_delete(request, subsystem_id: int):
    service = await get_subsystem_service()
    try:
        success = await service.delete_subsystem(subsystem_id)
        if not success:
            return JsonResponse({'error': 'Subsystem not found'}, status=404)
        return HttpResponse(status=204)
    
    except Exception as other_err:
        return JsonResponse({'error': other_err}, status=400)
