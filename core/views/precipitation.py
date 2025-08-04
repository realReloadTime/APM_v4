import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.precipitation import PrecipitationRepository, PrecipitationService
from core.models import Precipitation
from core.auth import async_permission_required, async_api_method


async def get_precipitation_service():
    return PrecipitationService(PrecipitationRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_precipitation(request):
    service = await get_precipitation_service()

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            precipitation = await service.create_precipitation(data)
            return JsonResponse(precipitation, status=201)
        else:
            precipitation = await service.get_precipitation()
            return JsonResponse(precipitation, status=200, safe=False)

    except Precipitation.DoesNotExist:
        return JsonResponse({'error': 'Precipitation not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_precipitation_detail(request, precipitation_id: int):
    service = await get_precipitation_service()

    try:
        precipitation = await service.get_precipitation(precipitation_id)
        return JsonResponse(precipitation, status=200)

    except Precipitation.DoesNotExist:
        return JsonResponse({'error': 'Precipitation not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_precipitation(request, precipitation_id: int):
    service = await get_precipitation_service()
    data = json.loads(request.body)
    try:
        precipitation = await service.update_precipitation(precipitation_id, data)
        return JsonResponse(precipitation, status=200)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_precipitation(request, precipitation_id: int):
    service = await get_precipitation_service()

    try:
        assert await service.delete_precipitation(precipitation_id)
        return HttpResponse(status=204)

    except AssertionError:
        return JsonResponse(
        {'error': "Error on System deletion"},
        status=404
    )

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
