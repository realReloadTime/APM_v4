import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.event import EventRepository, EventService
from core.models import Event
from core.auth import async_permission_required, async_api_method


async def get_event_service():
    return EventService(EventRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_event(request):
    service = await get_event_service()

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            data['created_by'] = request.user

            event = await service.create_event(data)
            return JsonResponse(event, status=201)
        else:
            event = await service.get_event()
            return JsonResponse(event, status=200, safe=False)

    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_event_detail(request, event_id: int):
    service = await get_event_service()

    try:
        event = await service.get_event(event_id)
        return JsonResponse(event, status=200)

    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_event(request, event_id: int):
    service = await get_event_service()
    data = json.loads(request.body)
    try:
        event = await service.update_event(event_id, data)
        return JsonResponse(event, status=200)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_event(request, event_id: int):
    service = await get_event_service()

    try:
        assert await service.delete_event(event_id)
        return HttpResponse(status=204)

    except AssertionError:
        return JsonResponse(
        {'error': "Error on System deletion"},
        status=404
    )

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
