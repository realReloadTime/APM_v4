import json
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError

from core.auth import async_permission_required, async_api_method

from core.logic.fire_danger import FireDangerRepository, FireDangerService
from core.models import FireDanger


async def get_fire_danger_service():
    return FireDangerService(FireDangerRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_fire_danger(request):
    service = await get_fire_danger_service()
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            fire = await service.create_fire_danger(data)
            return JsonResponse(fire, status=201)
        else:
            fire = await service.get_fire_danger()
            return JsonResponse(fire, status=200, safe=False)

    except FireDanger.DoesNotExist:
        return JsonResponse({'error': 'FireDanger not found'}, status=404)
    except IntegrityError:
        return JsonResponse(
            {'error': 'Одному событию не может соответствовать несколько FireDanger. Проверьте event_id.'})
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_fire_danger_detail(request, fire_id: int):
    service = await get_fire_danger_service()
    try:
        fire = await service.get_fire_danger(fire_id)
        return JsonResponse(fire, status=200)
    except FireDanger.DoesNotExist:
        return JsonResponse({'error': 'FireDanger not found'}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['GET', 'PUT'])
@async_permission_required([IsAuthenticated])
async def fire_danger_by_event(request, event_id: int):
    service = await get_fire_danger_service()
    try:
        if request.method == 'GET':
            result = await service.get_fire_danger_by_event(event_id)
        else:
            data = json.loads(request.body)
            result = await service.update_fire_danger(data=data, event_id=event_id)
        return JsonResponse(result, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_fire_danger(request, fire_id: int):
    service = await get_fire_danger_service()
    data = json.loads(request.body)
    try:
        fire = await service.update_fire_danger(fire_id, data)
        return JsonResponse(fire, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_fire_danger(request, fire_id: int):
    service = await get_fire_danger_service()
    try:
        assert await service.delete_fire_danger(fire_id)
        return HttpResponse(status=204)
    except AssertionError:
        return JsonResponse({'error': "Error on FireDanger deletion"}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
