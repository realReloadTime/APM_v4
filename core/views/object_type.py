import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.object_type import ObjectTypeRepository, ObjectTypeService
from core.models import ObjectType
from core.auth import async_permission_required, async_api_method


async def get_object_type_service():
    return ObjectTypeService(ObjectTypeRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_object_type(request):
    service = await get_object_type_service()

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            object_type = await service.create_object_type(data)
            return JsonResponse(object_type, status=201)
        else:
            object_type = await service.get_object_type()
            return JsonResponse(object_type, status=200, safe=False)

    except ObjectType.DoesNotExist:
        return JsonResponse({'error': 'ObjectType not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_object_type_detail(request, object_type_id: int):
    service = await get_object_type_service()

    try:
        object_type = await service.get_object_type(object_type_id)
        return JsonResponse(object_type, status=200)

    except ObjectType.DoesNotExist:
        return JsonResponse({'error': 'ObjectType not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_object_type(request, object_type_id: int):
    service = await get_object_type_service()
    data = json.loads(request.body)
    try:
        object_type = await service.update_object_type(object_type_id, data)
        return JsonResponse(object_type, status=200)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_object_type(request, object_type_id: int):
    service = await get_object_type_service()

    try:
        assert await service.delete_object_type(object_type_id)
        return HttpResponse(status=204)

    except AssertionError:
        return JsonResponse(
        {'error': "Error on System deletion"},
        status=404
    )

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
