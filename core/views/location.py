from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

import json

from core.logic.location import LocationRepository, LocationService
from core.auth import async_permission_required, async_api_method


async def get_location_service():
    return LocationService(LocationRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_location(request):
    service = await get_location_service()
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            location = await service.create_location(data)
            return JsonResponse(location, status=201)
        else:  # GET
            locations = await service.get_location()
            return JsonResponse(locations, safe=False, status=200)

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def location_detail(request, location_id: int):
    service = await get_location_service()
    try:
        location = await service.get_location(location_id)
        return JsonResponse(location, status=200)

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def location_by_loa_id(request, loa_id: int):
    service = await get_location_service()
    try:
        location = await service.get_location_by_loa(loa_id)
        return JsonResponse(location, status=200, safe=False)

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def location_update(request, location_id: int):
    service = await get_location_service()
    try:
        data = json.loads(request.body)
        location = await service.update_location(location_id, data)
        return JsonResponse(location, status=200)

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def location_delete(request, location_id: int):
    service = await get_location_service()
    try:
        success = await service.delete_location(location_id)
        if not success:
            return JsonResponse({'error': 'Location not found'}, status=404)
        return HttpResponse(status=204)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)
