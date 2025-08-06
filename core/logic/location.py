from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Location
from core.serializers import LocationSerializer
from core.logic.location_type import LocationTypeRepository
from core.logic.loa import LOARepository


class LocationRepository:
    @staticmethod
    async def create_location(data: dict) -> Location:
        name = data.get('name')
        location_type_id = data.get('location_type_id')
        loa_id = data.get('loa_id')

        if not name:
            raise ValueError("name обязательное поле для создания Location")

        if location_type_id:
            location_type = await LocationTypeRepository.get_location_type(location_type_id)
            data['location_type'] = location_type
        else:
            raise ValueError("location_type_id обязательное поле для создания Location")

        if loa_id:
            loa = await LOARepository.get_loa(loa_id)
            data['loa'] = loa
        else:
            raise ValueError("loa_id обязательное поле для создания Location")

        data.pop('location_type_id', None)
        data.pop('loa_id', None)

        return await Location.objects.acreate(**data)

    @staticmethod
    async def get_location(pk: int | None) -> Location | list[Location]:
        if pk is None:
            return [location async for location in Location.objects.select_related('location_type').select_related('loa').all()]
        try:
            return await Location.objects.select_related('location_type').select_related('loa').aget(id=pk)
        except Location.DoesNotExist:
            raise ValueError(f"Location с ID {pk} не существует")

    @staticmethod
    async def update_location(pk: int, data: dict) -> Location | None:
        location_type_id = data.get('location_type_id')
        loa_id = data.get('loa_id')
        
        if location_type_id:
            location_type = await LocationTypeRepository.get_location_type(location_type_id)
            data['location_type'] = location_type
        data.pop('location_type_id', None)
        
        if loa_id:
            loa = await LOARepository.get_loa(loa_id)
            data['loa'] = loa
        data.pop('loa_id', None)
        
        updated = await Location.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await Location.objects.select_related('location_type').select_related('loa').aget(id=pk)

    @staticmethod
    async def delete_location(pk: int) -> bool:
        result = await Location.objects.filter(id=pk).adelete()
        return bool(result)


class LocationService:
    def __init__(self, repository: LocationRepository):
        self.repository = repository

    async def create_location(self, data: dict) -> ReturnDict:
        result = await self.repository.create_location(data)
        return await self.serialize_location(result)

    async def get_location(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_location(pk)
        return await self.serialize_location(result)

    async def update_location(self, location_id: int, data: dict) -> ReturnDict:
        if location_id is None or location_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_location(location_id, data)
        if result is None:
            raise ValueError("Location not found")
        return await self.serialize_location(result)

    async def delete_location(self, pk: int) -> bool:
        return await self.repository.delete_location(pk)

    @staticmethod
    async def serialize_location(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = LocationSerializer(result, many=True)
        else:
            serializer = LocationSerializer(result)
        return serializer.data