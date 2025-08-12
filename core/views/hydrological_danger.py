import json
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError

from core.auth import async_permission_required, async_api_method

from core.logic.hydrological_danger import HydrologicalDangerRepository, HydrologicalDangerService
from core.models import HydrologicalDanger


async def get_hydrological_danger_service():
    return HydrologicalDangerService(HydrologicalDangerRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_hydrological_danger(request):
    service = await get_hydrological_danger_service()
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            hydro = await service.create_hydrological_danger(data)
            return JsonResponse(hydro, status=201)
        else:
            hydro = await service.get_hydrological_danger()
            return JsonResponse(hydro, status=200, safe=False)

    except HydrologicalDanger.DoesNotExist:
        return JsonResponse({'error': 'HydrologicalDanger not found'}, status=404)
    except IntegrityError:
        return JsonResponse(
            {'error': 'Одному событию не может соответствовать несколько HydrologicalDanger. Проверьте event_id.'})
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_hydrological_danger_detail(request, hydro_id: int):
    service = await get_hydrological_danger_service()
    try:
        hydro = await service.get_hydrological_danger(hydro_id)
        return JsonResponse(hydro, status=200)
    except HydrologicalDanger.DoesNotExist:
        return JsonResponse({'error': 'HydrologicalDanger not found'}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['GET', 'PUT'])
@async_permission_required([IsAuthenticated])
async def hydrological_danger_by_event(request, event_id: int):
    service = await get_hydrological_danger_service()
    try:
        if request.method == 'GET':
            result = await service.get_hydrological_danger_by_event(event_id)
        else:
            data = json.loads(request.body)
            result = await service.update_hydrological_danger(data=data, event_id=event_id)
        return JsonResponse(result, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_hydrological_danger(request, hydro_id: int):
    service = await get_hydrological_danger_service()
    data = json.loads(request.body)
    try:
        hydro = await service.update_hydrological_danger(pk=hydro_id, data=data)
        return JsonResponse(hydro, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_hydrological_danger(request, hydro_id: int):
    service = await get_hydrological_danger_service()
    try:
        assert await service.delete_hydrological_danger(hydro_id)
        return HttpResponse(status=204)
    except AssertionError:
        return JsonResponse({'error': "Error on HydrologicalDanger deletion"}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
