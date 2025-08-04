from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Precipitation
from core.serializers import PrecipitationSerializer


class PrecipitationRepository:
    @staticmethod
    async def create_precipitation(data: dict) -> Precipitation:
        return await Precipitation.objects.acreate(**data)

    @staticmethod
    async def get_precipitation(pk: int | None) -> Precipitation | list[Precipitation]:
        if pk is None:
            return [precipitation async for precipitation in Precipitation.objects.all()]
        try:
            return await Precipitation.objects.aget(id=pk)
        except Precipitation.DoesNotExist:
            raise ValueError(f"Precipitation с ID {pk} не существует")

    @staticmethod
    async def update_precipitation(pk: int, data: dict) -> Precipitation | None:
        updated = await Precipitation.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await Precipitation.objects.aget(id=pk)

    @staticmethod
    async def delete_precipitation(pk: int) -> bool:
        result = await Precipitation.objects.filter(id=pk).adelete()
        return bool(result)


class PrecipitationService:
    def __init__(self, repository: PrecipitationRepository):
        self.repository = repository

    async def create_precipitation(self, data: dict) -> ReturnDict:
        result = await self.repository.create_precipitation(data)
        return await self.serialize_precipitation(result)

    async def get_precipitation(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_precipitation(pk)
        return await self.serialize_precipitation(result)

    async def update_precipitation(self, precipitation_id: int, data: dict) -> ReturnDict:
        if precipitation_id is None or precipitation_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_precipitation(precipitation_id, data)
        return await self.serialize_precipitation(result)

    async def delete_precipitation(self, pk: int) -> bool:
        return await self.repository.delete_precipitation(pk)

    @staticmethod
    async def serialize_precipitation(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = PrecipitationSerializer(result, many=True)
        else:
            serializer = PrecipitationSerializer(result)
        return serializer.data
