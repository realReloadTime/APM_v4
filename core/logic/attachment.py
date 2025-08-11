import uuid
import os
import aiofiles

from asgiref.sync import sync_to_async
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Attachment
from core.serializers import AttachmentSerializer

from core.logic.event import EventRepository


class AttachmentRepository:
    @staticmethod
    async def create_attachment(data: dict) -> Attachment:
        event_id = data.get('event_id')
        if event_id:
            data['event'] = await EventRepository.get_event(event_id)
        data.pop('event_id', None)

        return await Attachment.objects.acreate(**data)

    @staticmethod
    async def get_attachment(pk: int | None) -> Attachment | list[Attachment]:
        if pk is None:
            return [attachment async for attachment in Attachment.objects.select_related('author', 'event').all()]
        try:
            return await Attachment.objects.select_related('author', 'event').aget(id=pk)
        except Attachment.DoesNotExist:
            raise ValueError(f"Attachment с ID {pk} не существует")


    async def update_attachment(self, pk: int, data: dict) -> Attachment | None:
        event_id = data.get('event_id')
        if event_id:
            data['event'] = await EventRepository.get_event(event_id)
        data.pop('event_id', None)

        updated = await Attachment.objects.filter(id=pk).aupdate(**data)

        if not updated:
            return None

        return await Attachment.objects.select_related('event').aget(id=pk)

    @staticmethod
    async def delete_attachment(pk: int) -> bool:
        try:
            attachment = await Attachment.objects.aget(id=pk)
            file_path = os.path.join('core', 'attachments', attachment.name)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Attachment.DoesNotExist:
            pass
        result = await Attachment.objects.filter(id=pk).adelete()
        return bool(result)


class AttachmentService:
    def __init__(self, repository: AttachmentRepository):
        self.repository = repository

    async def create_attachment(self, file, author):
        file_extension = os.path.splitext(file.name)[1]
        unique_name = f"{uuid.uuid4()}{file_extension}"  # file_extension = '.*' (dot included)
        file_path = os.path.join('core', 'attachments', unique_name)

        async with aiofiles.open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                await destination.write(chunk)

        data = {'name': unique_name, 'author': author}
        result = await self.repository.create_attachment(data)

        return await self.serialize_attachment(result)

    async def get_attachment(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_attachment(pk)
        return await self.serialize_attachment(result)

    async def update_attachment(self, attachment_id: int, data: dict) -> ReturnDict:
        if attachment_id is None or attachment_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_attachment(attachment_id, data)
        if result is None:
            raise ValueError("Attachment not found")
        return await self.serialize_attachment(result)

    async def delete_attachment(self, pk: int) -> bool:
        return await self.repository.delete_attachment(pk)

    @staticmethod
    async def serialize_attachment(result) -> ReturnDict:
        def serialize():
            if isinstance(result, list):
                serializer = AttachmentSerializer(result, many=True)
            else:
                serializer = AttachmentSerializer(result)
            return serializer.data

        return await sync_to_async(serialize)()