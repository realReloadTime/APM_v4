from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse
import json
from core.auth import async_permission_required, async_api_method

from core.logic.equipment_failure import EquipmentFailureRepository, EquipmentFailureService
from core.models import EquipmentFailure

async def get_equipment_failure_service():
    return EquipmentFailureService(EquipmentFailureRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_equipment_failure(request):
    service = await get_equipment_failure_service()
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            failure = await service.create_equipment_failure(data)
            return JsonResponse(failure, status=201)
        else:
            failure = await service.get_equipment_failure()
            return JsonResponse(failure, status=200, safe=False)

    except EquipmentFailure.DoesNotExist:
        return JsonResponse({'error': 'EquipmentFailure not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_equipment_failure_detail(request, failure_id: int):
    service = await get_equipment_failure_service()
    try:
        failure = await service.get_equipment_failure(failure_id)
        return JsonResponse(failure, status=200)
    except EquipmentFailure.DoesNotExist:
        return JsonResponse({'error': 'EquipmentFailure not found'}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_equipment_failure(request, failure_id: int):
    service = await get_equipment_failure_service()
    data = json.loads(request.body)
    try:
        failure = await service.update_equipment_failure(failure_id, data)
        return JsonResponse(failure, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_equipment_failure(request, failure_id: int):
    service = await get_equipment_failure_service()
    try:
        assert await service.delete_equipment_failure(failure_id)
        return HttpResponse(status=204)
    except AssertionError:
        return JsonResponse({'error': "Error on EquipmentFailure deletion"}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)