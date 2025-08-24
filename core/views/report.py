import os
import json
import mimetypes
from django.http import JsonResponse, StreamingHttpResponse
from rest_framework.permissions import IsAuthenticated

from core.auth import async_permission_required, async_api_method
from core.logic.build_report import make_report
from core.logic.attachment import async_file_iterator


@async_api_method(['POST'])
@async_permission_required([IsAuthenticated])
async def download_report(request):
    try:
        body = json.loads(request.body)
        ids = body['event_id']
        label = body['label'] if 'label' in body else None

        if not isinstance(ids, list):  # если передан только один айдишник без списка
            ids = [ids]
        if await make_report(ids, label):
            file_path = os.path.join('core', 'attachments', 'report.xlsx')

            if not os.path.exists(file_path):
                return JsonResponse({'error': 'Файл не найден на сервере'}, status=404)

            mime_type, _ = mimetypes.guess_type(file_path)
            response = StreamingHttpResponse(
                async_file_iterator(file_path),
                content_type=mime_type or 'application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="report.xlsx"'
            response['Content-Length'] = os.path.getsize(file_path)

            return response

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)
