import json
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse
from django.db.utils import IntegrityError

from core.auth import async_permission_required, async_api_method

from core.logic.adverse_weather import AdverseWeatherRepository, AdverseWeatherService
from core.models import AdverseWeather


async def get_adverse_weather_service():
    return AdverseWeatherService(AdverseWeatherRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_adverse_weather(request):
    service = await get_adverse_weather_service()
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            weather = await service.create_adverse_weather(data)
            return JsonResponse(weather, status=201)
        else:
            weather = await service.get_adverse_weather()
            return JsonResponse(weather, status=200, safe=False)

    except AdverseWeather.DoesNotExist:
        return JsonResponse({'error': 'AdverseWeather not found'}, status=404)
    except IntegrityError:
        return JsonResponse(
            {'error': 'Одному событию не может соответствовать несколько AdverseWeather. Проверьте event_id.'})
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_adverse_weather_detail(request, weather_id: int):
    service = await get_adverse_weather_service()
    try:
        weather = await service.get_adverse_weather(weather_id)
        return JsonResponse(weather, status=200)
    except AdverseWeather.DoesNotExist:
        return JsonResponse({'error': 'AdverseWeather not found'}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def get_adverse_weather_by_event(request, event_id: int):
    service = await get_adverse_weather_service()
    try:
        weather = await service.get_adverse_weather_by_event(event_id)
        return JsonResponse(weather, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['PUT'])
@async_permission_required([IsAuthenticated])
async def update_adverse_weather(request, weather_id: int):
    service = await get_adverse_weather_service()
    data = json.loads(request.body)
    try:
        weather = await service.update_adverse_weather(weather_id, data)
        return JsonResponse(weather, status=200)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def delete_adverse_weather(request, weather_id: int):
    service = await get_adverse_weather_service()
    try:
        assert await service.delete_adverse_weather(weather_id)
        return HttpResponse(status=204)
    except AssertionError:
        return JsonResponse({'error': "Error on AdverseWeather deletion"}, status=404)
    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=404)
