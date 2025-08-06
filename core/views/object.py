from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

import json

from core.logic.object import ObjectRepository, ObjectService
from core.auth import async_permission_required, async_api_method


async def get_object_service():
    return ObjectService(ObjectRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_object(request):
    service = await get_object_service()
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            obj = await service.create_object(data)
            return JsonResponse(obj, status=201)
        else:  # GET
            objects = await service.get_object()
            return JsonResponse(objects, safe=False, status=200)

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def object_detail(request, object_id: int):
    service = await get_object_service()
    try:
        obj = await service.get_object(object_id)
        return JsonResponse(obj, status=200)

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def object_update(request, object_id: int):
    service = await get_object_service()
    try:
        data = json.loads(request.body)
        obj = await service.update_object(object_id, data)
        return JsonResponse(obj, status=200)

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=400)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def object_delete(request, object_id: int):
    service = await get_object_service()
    try:
        success = await service.delete_object(object_id)
        if not success:
            return JsonResponse({'error': 'Object not found'}, status=404)
        return HttpResponse(status=204)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)
