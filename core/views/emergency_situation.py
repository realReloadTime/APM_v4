import json
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError

from core.auth import async_permission_required, async_api_method

from core.logic.emergency_situation import EmergencySituationRepository, EmergencySituationService
from core.models import EmergencySituation


async def get_emergency_situation_service():
    return EmergencySituationService(EmergencySituationRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_emergency_situation(request):
    service = await get_emergency_situation_service()
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            situation = await service.create_emergency_situation(data)
            return JsonResponse(situation, status=201)
        else:
            situation = await service.get_emergency_situation()
            return JsonResponse(situation, status=200, safe=False)

    except EmergencySituation.DoesNotExist:
        return JsonResponse({'error': 'EmergencySituation not found'}, status=404)
    except IntegrityError:
        return JsonResponse(
            {'error': 'Одному событию не может соответствовать несколько EmergencySituation. Проверьте event_id.'})
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_emergency_situation_detail(request, situation_id: int):
    service = await get_emergency_situation_service()
    try:
        situation = await service.get_emergency_situation(situation_id)
        return JsonResponse(situation, status=200)
    except EmergencySituation.DoesNotExist:
        return JsonResponse({'error': 'EmergencySituation not found'}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['GET', 'PUT'])
@async_permission_required([IsAuthenticated])
async def emergency_situation_by_event(request, event_id: int):
    service = await get_emergency_situation_service()
    try:
        if request.method == 'GET':
            result = await service.get_emergency_situation_by_event(event_id)
        else:
            data = json.loads(request.body)
            result = await service.update_emergency_situation(data=data, event_id=event_id)
        return JsonResponse(result, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_emergency_situation(request, situation_id: int):
    service = await get_emergency_situation_service()
    data = json.loads(request.body)
    try:
        situation = await service.update_emergency_situation(pk=situation_id, data=data)
        return JsonResponse(situation, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_emergency_situation(request, situation_id: int):
    service = await get_emergency_situation_service()
    try:
        assert await service.delete_emergency_situation(situation_id)
        return HttpResponse(status=204)
    except AssertionError:
        return JsonResponse({'error': "Error on EmergencySituation deletion"}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
