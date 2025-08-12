import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.measures_taken import MeasuresTakenRepository, MeasuresTakenService
from core.models import MeasuresTaken
from core.auth import async_permission_required, async_api_method


async def get_measures_taken_service():
    return MeasuresTakenService(MeasuresTakenRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_measures_taken(request):
    service = await get_measures_taken_service()

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            measures_taken = await service.create_measures_taken(data)
            return JsonResponse(measures_taken, status=201)
        else:
            measures_taken = await service.get_measures_taken()
            return JsonResponse(measures_taken, status=200, safe=False)

    except MeasuresTaken.DoesNotExist:
        return JsonResponse({'error': 'MeasuresTaken not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_measures_taken_detail(request, measures_taken_id: int):
    service = await get_measures_taken_service()

    try:
        measures_taken = await service.get_measures_taken(measures_taken_id)
        return JsonResponse(measures_taken, status=200)

    except MeasuresTaken.DoesNotExist:
        return JsonResponse({'error': 'MeasuresTaken not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_measures_taken_by_event(request, event_id: int):
    service = await get_measures_taken_service()
    try:
        result = await service.get_measures_taken_by_event(event_id)
        return JsonResponse(result, status=200, safe=False)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_measures_taken(request, measures_taken_id: int):
    service = await get_measures_taken_service()
    data = json.loads(request.body)
    try:
        measures_taken = await service.update_measures_taken(measures_taken_id, data)
        return JsonResponse(measures_taken, status=200)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_measures_taken(request, measures_taken_id: int):
    service = await get_measures_taken_service()

    try:
        assert await service.delete_measures_taken(measures_taken_id)
        return HttpResponse(status=204)

    except AssertionError:
        return JsonResponse(
        {'error': "Error on System deletion"},
        status=404
    )

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
