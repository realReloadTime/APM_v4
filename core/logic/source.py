from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Source
from core.serializers import SourceSerializer


class SourceRepository:
    @staticmethod
    async def create_source(data: dict) -> Source:
        return await Source.objects.acreate(**data)

    @staticmethod
    async def get_source(pk: int | None) -> Source | list[Source]:
        if pk is None:
            return [source async for source in Source.objects.all()]
        try:
            return await Source.objects.aget(id=pk)
        except Source.DoesNotExist:
            raise ValueError(f"Source с ID {pk} не существует")

    @staticmethod
    async def update_source(pk: int, data: dict) -> Source | None:
        updated = await Source.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await Source.objects.aget(id=pk)

    @staticmethod
    async def delete_source(pk: int) -> bool:
        result = await Source.objects.filter(id=pk).adelete()
        return bool(result)


class SourceService:
    def __init__(self, repository: SourceRepository):
        self.repository = repository

    async def create_source(self, data: dict) -> ReturnDict:
        result = await self.repository.create_source(data)
        return await self.serialize_source(result)

    async def get_source(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_source(pk)
        return await self.serialize_source(result)

    async def update_source(self, source_id: int, data: dict) -> ReturnDict:
        if source_id is None or source_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_source(source_id, data)
        return await self.serialize_source(result)

    async def delete_source(self, pk: int) -> bool:
        return await self.repository.delete_source(pk)

    @staticmethod
    async def serialize_source(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = SourceSerializer(result, many=True)
        else:
            serializer = SourceSerializer(result)
        return serializer.data
