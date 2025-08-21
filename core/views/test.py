import json
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated

from core.auth import async_permission_required, async_api_method
from core.logic.data_for_report import generate_report_data


@async_api_method(['POST'])
@async_permission_required([IsAuthenticated])
async def test(request):
    body = json.loads(request.body)
    ids = body['event_id']
    if not isinstance(ids, list):  # если передан только один айдишник без списка
        ids = [ids]
    data = await generate_report_data(ids)
    return JsonResponse(data)
