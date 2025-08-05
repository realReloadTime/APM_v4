from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import LocationType
from core.serializers import LocationTypeSerializer


class LocationTypeRepository:
    @staticmethod
    async def create_location_type(data: dict) -> LocationType:
        return await LocationType.objects.acreate(**data)

    @staticmethod
    async def get_location_type(pk: int | None) -> LocationType | list[LocationType]:
        if pk is None:
            return [location_type async for location_type in LocationType.objects.all()]
        try:
            return await LocationType.objects.aget(id=pk)
        except LocationType.DoesNotExist:
            raise ValueError(f"LocationType с ID {pk} не существует")

    @staticmethod
    async def update_location_type(pk: int, data: dict) -> LocationType | None:
        updated = await LocationType.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await LocationType.objects.aget(id=pk)

    @staticmethod
    async def delete_location_type(pk: int) -> bool:
        result = await LocationType.objects.filter(id=pk).adelete()
        return bool(result)


class LocationTypeService:
    def __init__(self, repository: LocationTypeRepository):
        self.repository = repository

    async def create_location_type(self, data: dict) -> ReturnDict:
        result = await self.repository.create_location_type(data)
        return await self.serialize_location_type(result)

    async def get_location_type(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_location_type(pk)
        return await self.serialize_location_type(result)

    async def update_location_type(self, location_type_id: int, data: dict) -> ReturnDict:
        if location_type_id is None or location_type_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_location_type(location_type_id, data)
        return await self.serialize_location_type(result)

    async def delete_location_type(self, pk: int) -> bool:
        return await self.repository.delete_location_type(pk)

    @staticmethod
    async def serialize_location_type(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = LocationTypeSerializer(result, many=True)
        else:
            serializer = LocationTypeSerializer(result)
        return serializer.data
