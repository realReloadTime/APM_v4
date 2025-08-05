import uuid
import os

from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Attachment
from core.serializers import AttachmentSerializer


class AttachmentRepository:
    @staticmethod
    async def create_attachment(data: dict) -> Attachment:
        return await Attachment.objects.acreate(**data)

    @staticmethod
    async def get_attachment(pk: int | None) -> Attachment | list[Attachment]:
        if pk is None:
            return [attachment async for attachment in Attachment.objects.select_related('author').all()]
        try:
            return await Attachment.objects.select_related('author').aget(id=pk)
        except Attachment.DoesNotExist:
            raise ValueError(f"Attachment с ID {pk} не существует")

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
        unique_name = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join('core', 'attachments', unique_name)

        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        data = {'name': unique_name, 'author': author}
        result = await self.repository.create_attachment(data)

        return await self.serialize_attachment(result)

    async def get_attachment(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_attachment(pk)
        return await self.serialize_attachment(result)

    async def delete_attachment(self, pk: int) -> bool:
        return await self.repository.delete_attachment(pk)

    @staticmethod
    async def serialize_attachment(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = AttachmentSerializer(result, many=True)
        else:
            serializer = AttachmentSerializer(result)
        return serializer.data