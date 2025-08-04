import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.condition import ConditionRepository, ConditionService
from core.models import Condition
from core.auth import async_permission_required, async_api_method


async def get_condition_service():
    return ConditionService(ConditionRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_condition(request):
    service = await get_condition_service()

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            condition = await service.create_condition(data)
            return JsonResponse(condition, status=201)
        else:
            condition = await service.get_condition()
            return JsonResponse(condition, status=200, safe=False)

    except Condition.DoesNotExist:
        return JsonResponse({'error': 'Condition not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_condition_detail(request, condition_id: int):
    service = await get_condition_service()

    try:
        condition = await service.get_condition(condition_id)
        return JsonResponse(condition, status=200)

    except Condition.DoesNotExist:
        return JsonResponse({'error': 'Condition not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_condition(request, condition_id: int):
    service = await get_condition_service()
    data = json.loads(request.body)
    try:
        condition = await service.update_condition(condition_id, data)
        return JsonResponse(condition, status=200)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_condition(request, condition_id: int):
    service = await get_condition_service()

    try:
        assert await service.delete_condition(condition_id)
        return HttpResponse(status=204)

    except AssertionError:
        return JsonResponse(
        {'error': "Error on System deletion"},
        status=404
    )

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
