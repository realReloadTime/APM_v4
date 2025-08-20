from core.logic.report import *

import json
from django.http import JsonResponse, HttpResponse

from rest_framework.permissions import IsAuthenticated
from core.auth import async_permission_required, async_api_method

from asgiref.sync import sync_to_async
from core.logic.report import generate_report_data

import json
from django.http import JsonResponse


@async_api_method(['POST'])
# @async_permission_required([IsAuthenticated])
async def test(request):
    body = json.loads(request.body)
    ids = body['event_id']
    # Ensure ids is a list (handle case where it might be a single int)
    if not isinstance(ids, list):
        ids = [ids]
    data = await sync_to_async(generate_report_data)(ids)
    return JsonResponse(data)