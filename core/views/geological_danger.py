import json
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError

from core.auth import async_permission_required, async_api_method

from core.logic.geological_danger import GeologicalDangerRepository, GeologicalDangerService
from core.models import GeologicalDanger


async def get_geological_danger_service():
    return GeologicalDangerService(GeologicalDangerRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_geological_danger(request):
    service = await get_geological_danger_service()
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            geo = await service.create_geological_danger(data)
            return JsonResponse(geo, status=201)
        else:
            geo = await service.get_geological_danger()
            return JsonResponse(geo, status=200, safe=False)

    except GeologicalDanger.DoesNotExist:
        return JsonResponse({'error': 'GeologicalDanger not found'}, status=404)
    except IntegrityError:
        return JsonResponse(
            {'error': 'Одному событию не может соответствовать несколько GeologicalDanger. Проверьте event_id.'})
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_geological_danger_detail(request, geo_id: int):
    service = await get_geological_danger_service()
    try:
        geo = await service.get_geological_danger(geo_id)
        return JsonResponse(geo, status=200)
    except GeologicalDanger.DoesNotExist:
        return JsonResponse({'error': 'GeologicalDanger not found'}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['GET', 'PUT'])
@async_permission_required([IsAuthenticated])
async def geological_danger_by_event(request, event_id: int):
    service = await get_geological_danger_service()
    try:
        if request.method == 'GET':
            result = await service.get_geological_danger_by_event(event_id)
        else:
            data = json.loads(request.body)
            result = await service.update_geological_danger(data=data, event_id=event_id)
        return JsonResponse(result, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_geological_danger(request, geo_id: int):
    service = await get_geological_danger_service()
    data = json.loads(request.body)
    try:
        geo = await service.update_geological_danger(pk=geo_id, data=data)
        return JsonResponse(geo, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_geological_danger(request, geo_id: int):
    service = await get_geological_danger_service()
    try:
        assert await service.delete_geological_danger(geo_id)
        return HttpResponse(status=204)
    except AssertionError:
        return JsonResponse({'error': "Error on GeologicalDanger deletion"}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
