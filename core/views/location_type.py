import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.location_type import LocationTypeRepository, LocationTypeService
from core.models import LocationType
from core.auth import async_permission_required, async_api_method


async def get_location_type_service():
    return LocationTypeService(LocationTypeRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_location_type(request):
    service = await get_location_type_service()

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            location_type = await service.create_location_type(data)
            return JsonResponse(location_type, status=201)
        else:
            location_type = await service.get_location_type()
            return JsonResponse(location_type, status=200, safe=False)

    except LocationType.DoesNotExist:
        return JsonResponse({'error': 'LocationType not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_location_type_detail(request, location_type_id: int):
    service = await get_location_type_service()

    try:
        location_type = await service.get_location_type(location_type_id)
        return JsonResponse(location_type, status=200)

    except LocationType.DoesNotExist:
        return JsonResponse({'error': 'LocationType not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_location_type(request, location_type_id: int):
    service = await get_location_type_service()
    data = json.loads(request.body)
    try:
        location_type = await service.update_location_type(location_type_id, data)
        return JsonResponse(location_type, status=200)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_location_type(request, location_type_id: int):
    service = await get_location_type_service()

    try:
        assert await service.delete_location_type(location_type_id)
        return HttpResponse(status=204)

    except AssertionError:
        return JsonResponse(
        {'error': "Error on System deletion"},
        status=404
    )

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
