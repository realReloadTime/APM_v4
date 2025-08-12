import json
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError

from core.auth import async_permission_required, async_api_method

from core.logic.other_danger import OtherDangerRepository, OtherDangerService
from core.models import OtherDanger


async def get_other_danger_service():
    return OtherDangerService(OtherDangerRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_other_danger(request):
    service = await get_other_danger_service()
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            danger = await service.create_other_danger(data)
            return JsonResponse(danger, status=201)
        else:
            danger = await service.get_other_danger()
            return JsonResponse(danger, status=200, safe=False)

    except OtherDanger.DoesNotExist:
        return JsonResponse({'error': 'OtherDanger not found'}, status=404)
    except IntegrityError:
        return JsonResponse(
            {'error': 'Одному событию не может соответствовать несколько OtherDanger. Проверьте event_id.'})
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_other_danger_detail(request, danger_id: int):
    service = await get_other_danger_service()
    try:
        danger = await service.get_other_danger(danger_id)
        return JsonResponse(danger, status=200)
    except OtherDanger.DoesNotExist:
        return JsonResponse({'error': 'OtherDanger not found'}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['GET', 'PUT'])
@async_permission_required([IsAuthenticated])
async def other_danger_by_event(request, event_id: int):
    service = await get_other_danger_service()
    try:
        if request.method == 'GET':
            result = await service.get_other_danger_by_event(event_id)
        else:
            data = json.loads(request.body)
            result = await service.update_other_danger(data=data, event_id=event_id)
        return JsonResponse(result, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_other_danger(request, danger_id: int):
    service = await get_other_danger_service()
    data = json.loads(request.body)
    try:
        danger = await service.update_other_danger(pk=danger_id, data=data)
        return JsonResponse(danger, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_other_danger(request, danger_id: int):
    service = await get_other_danger_service()
    try:
        assert await service.delete_other_danger(danger_id)
        return HttpResponse(status=204)
    except AssertionError:
        return JsonResponse({'error': "Error on OtherDanger deletion"}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
