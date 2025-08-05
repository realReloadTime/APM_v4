import mimetypes
import os

from django.http import JsonResponse, HttpResponse, FileResponse

from rest_framework.permissions import IsAuthenticated

from core.logic.attachment import AttachmentRepository, AttachmentService
from core.auth import async_permission_required, async_api_method


async def get_attachment_service():
    return AttachmentService(AttachmentRepository())


@async_api_method(['GET', 'POST'])
@async_permission_required([IsAuthenticated])
async def get_post_attachment(request):
    service = await get_attachment_service()

    try:
        if request.method == 'POST':
            file = request.FILES.get('file')

            if not file:
                return JsonResponse({'error': 'Файл обязателен'}, status=400)

            attachment = await service.create_attachment(file, request.user)
            return JsonResponse(attachment, status=201)
        else:  # GET
            attachments = await service.get_attachment()
            return JsonResponse(attachments, safe=False, status=200)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def attachment_detail(request, attachment_id: int):
    service = await get_attachment_service()

    try:
        attachment = await service.get_attachment(attachment_id)
        return JsonResponse(attachment, status=200)

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['GET'])
@async_permission_required([IsAuthenticated])
async def attachment_download(request, attachment_id: int):
    service = await get_attachment_service()

    try:
        attachment = await service.get_attachment(attachment_id)
        file_path = os.path.join('core', 'attachments', attachment['name'])

        if not os.path.exists(file_path):
            return JsonResponse({'error': 'Файл не найден на сервере'}, status=404)

        file = open(file_path, 'rb')
        mime_type, _ = mimetypes.guess_type(file_path)
        response = FileResponse(file, content_type=mime_type or 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{attachment["name"]}"'

        return response

    except ValueError as ve:
        return JsonResponse({'error': str(ve)}, status=404)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)


@async_api_method(['DELETE'])
@async_permission_required([IsAuthenticated])
async def attachment_delete(request, attachment_id: int):
    service = await get_attachment_service()

    try:
        success = await service.delete_attachment(attachment_id)

        if not success:
            return JsonResponse({'error': 'Attachment not found'}, status=404)
        return HttpResponse(status=204)

    except Exception as other_err:
        return JsonResponse({'error': str(other_err)}, status=400)
