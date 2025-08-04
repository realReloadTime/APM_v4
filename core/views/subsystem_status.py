import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.subsystem_status import SubsystemStatusRepository, SubsystemStatusService
from core.models import SubsystemStatus
from core.auth import async_permission_required, async_api_method


async def get_subsystemstatus_service():
    return SubsystemStatusService(SubsystemStatusRepository())


@async_api_method(['GET', 'POST'])  # Разрешаем GET и POST
@async_permission_required([IsAuthenticated])
async def get_post_subsystem_status(request):
    service = await get_subsystemstatus_service()

    try:
        if request.method == 'POST':
            # обработка POST SubsystemStatus
            data = json.loads(request.body)
            ss_status = await service.create_subsystem_status(data)
            return JsonResponse(ss_status, status=201)
        else:  # GET
            ss_status = await service.get_subsystem_status()
            return JsonResponse(ss_status, status=200, safe=False)

    except SubsystemStatus.DoesNotExist:
        return JsonResponse({'error': 'SubsystemStatus not found'}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_subsystem_status_detail(request, ss_status_id: int):
    service = await get_subsystemstatus_service()

    try:
        ss_status = await service.get_subsystem_status(ss_status_id)
        return JsonResponse(ss_status, status=200)

    except SubsystemStatus.DoesNotExist:
        return JsonResponse({'error': 'SubsystemStatus not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_subsystem_status(request, ss_status_id: int):
    service = await get_subsystemstatus_service()
    data = json.loads(request.body)
    try:
        ss_status = await service.update_subsystem_status(ss_status_id, data)
        return JsonResponse(ss_status, status=200)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_subsystem_status(request, ss_status_id: int):
    service = await get_subsystemstatus_service()

    try:
        assert await service.delete_subsystem_status(ss_status_id)
        return HttpResponse(status=204)

    except SubsystemStatus.DoesNotExist:
        return JsonResponse(
        {'msg': 'SubsystemStatus not found'},
        status=404
    )

    except AssertionError:
        return JsonResponse(
        {'error': "Error on SubsystemStatus deletion"},
        status=404
    )
