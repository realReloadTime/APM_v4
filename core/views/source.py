import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.source import SourceRepository, SourceService
from core.models import Source
from core.auth import async_permission_required, async_api_method


async def get_source_service():
    return SourceService(SourceRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_source(request):
    service = await get_source_service()

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            source = await service.create_source(data)
            return JsonResponse(source, status=201)
        else:
            source = await service.get_source()
            return JsonResponse(source, status=200, safe=False)

    except Source.DoesNotExist:
        return JsonResponse({'error': 'Source not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_source_detail(request, source_id: int):
    service = await get_source_service()

    try:
        source = await service.get_source(source_id)
        return JsonResponse(source, status=200)

    except Source.DoesNotExist:
        return JsonResponse({'error': 'Source not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_source(request, source_id: int):
    service = await get_source_service()
    data = json.loads(request.body)
    try:
        source = await service.update_source(source_id, data)
        return JsonResponse(source, status=200)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_source(request, source_id: int):
    service = await get_source_service()

    try:
        assert await service.delete_source(source_id)
        return HttpResponse(status=204)

    except AssertionError:
        return JsonResponse(
        {'error': "Error on System deletion"},
        status=404
    )

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
