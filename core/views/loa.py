from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

import json

from core.logic.loa import LOARepository, LOAService
from core.auth import async_permission_required, async_api_method


async def get_loa_service():
    return LOAService(LOARepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_loa(request):
    service = await get_loa_service()
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            loa = await service.create_loa(data)
            return JsonResponse(loa, status=201)
        else:  # GET
            loas = await service.get_loa()
            return JsonResponse(loas, safe=False, status=200)

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def loa_detail(request, loa_id: int):
    service = await get_loa_service()
    try:
        loa = await service.get_loa(loa_id)
        return JsonResponse(loa, status=200)

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def loas_by_region(request, region_id: int):
    service = await get_loa_service()
    try:
        loas = await service.get_loas_by_region(region_id)
        return JsonResponse(loas, safe=False, status=200)
    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def loa_update(request, loa_id: int):
    service = await get_loa_service()
    try:
        data = json.loads(request.body)
        loa = await service.update_loa(loa_id, data)
        return JsonResponse(loa, status=200)

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def loa_delete(request, loa_id: int):
    service = await get_loa_service()
    try:
        success = await service.delete_loa(loa_id)
        if not success:
            return JsonResponse({'error': 'LOA not found'}, status=404)
        return HttpResponse(status=204)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)
