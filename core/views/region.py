import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.region import RegionRepository, RegionService
from core.models import Region
from core.auth import async_permission_required, async_api_method


async def get_region_service():
    return RegionService(RegionRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_region(request):
    service = await get_region_service()

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            region = await service.create_region(data)
            return JsonResponse(region, status=201)
        else:
            region = await service.get_region()
            return JsonResponse(region, status=200, safe=False)

    except Region.DoesNotExist:
        return JsonResponse({'error': 'Region not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_region_detail(request, region_id: int):
    service = await get_region_service()

    try:
        region = await service.get_region(region_id)
        return JsonResponse(region, status=200)

    except Region.DoesNotExist:
        return JsonResponse({'error': 'Region not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_region(request, region_id: int):
    service = await get_region_service()
    data = json.loads(request.body)
    try:
        region = await service.update_region(region_id, data)
        return JsonResponse(region, status=200)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_region(request, region_id: int):
    service = await get_region_service()

    try:
        assert await service.delete_region(region_id)
        return HttpResponse(status=204)

    except AssertionError:
        return JsonResponse(
        {'error': "Error on System deletion"},
        status=404
    )

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
