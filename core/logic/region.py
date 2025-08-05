from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Region
from core.serializers import RegionSerializer


class RegionRepository:
    @staticmethod
    async def create_region(data: dict) -> Region:
        return await Region.objects.acreate(**data)

    @staticmethod
    async def get_region(pk: int | None) -> Region | list[Region]:
        if pk is None:
            return [region async for region in Region.objects.all()]
        try:
            return await Region.objects.aget(id=pk)
        except Region.DoesNotExist:
            raise ValueError(f"Region с ID {pk} не существует")

    @staticmethod
    async def update_region(pk: int, data: dict) -> Region | None:
        updated = await Region.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await Region.objects.aget(id=pk)

    @staticmethod
    async def delete_region(pk: int) -> bool:
        result = await Region.objects.filter(id=pk).adelete()
        return bool(result)


class RegionService:
    def __init__(self, repository: RegionRepository):
        self.repository = repository

    async def create_region(self, data: dict) -> ReturnDict:
        result = await self.repository.create_region(data)
        return await self.serialize_region(result)

    async def get_region(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_region(pk)
        return await self.serialize_region(result)

    async def update_region(self, region_id: int, data: dict) -> ReturnDict:
        if region_id is None or region_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_region(region_id, data)
        return await self.serialize_region(result)

    async def delete_region(self, pk: int) -> bool:
        return await self.repository.delete_region(pk)

    @staticmethod
    async def serialize_region(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = RegionSerializer(result, many=True)
        else:
            serializer = RegionSerializer(result)
        return serializer.data
