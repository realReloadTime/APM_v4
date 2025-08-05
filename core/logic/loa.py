from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import LOA
from core.serializers import LOASerializer
from core.logic.region import RegionRepository


class LOARepository:
    @staticmethod
    async def create_loa(data: dict) -> LOA:
        region_id = data.get('region_id')
        if region_id:
            region = await RegionRepository.get_region(region_id)
            data['region'] = region
        else:
            raise ValueError("region_id обязательное поле для создания LOA")

        data.pop('region_id', None)
        return await LOA.objects.acreate(**data)

    @staticmethod
    async def get_loa(pk: int | None) -> LOA | list[LOA]:
        if pk is None:
            return [loa async for loa in LOA.objects.select_related('region').all()]
        try:
            return await LOA.objects.select_related('region').aget(id=pk)
        except LOA.DoesNotExist:
            raise ValueError(f"LOA с ID {pk} не существует")

    @staticmethod
    async def get_loas_by_region(region_id: int) -> list[LOA]:
        await RegionRepository.get_region(region_id)  # проверка существования системы
        # возврат подсистем, связанных с системой
        return [loa async for loa in
                LOA.objects.select_related('region').filter(region_id=region_id)]

    @staticmethod
    async def update_loa(pk: int, data: dict) -> LOA | None:
        # region_id необязательное поле - если не указано, связь не меняется
        region_id = data.get('region_id')
        if region_id:
            region = await RegionRepository.get_region(region_id)
            data['region'] = region
        data.pop('region_id', None)
        updated = await LOA.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await LOA.objects.select_related('region').aget(id=pk)

    @staticmethod
    async def delete_loa(pk: int) -> bool:
        result = await LOA.objects.filter(id=pk).adelete()
        return bool(result)


class LOAService:
    def __init__(self, repository: LOARepository):
        self.repository = repository

    async def create_loa(self, data: dict) -> ReturnDict:
        result = await self.repository.create_loa(data)
        return await self.serialize_loa(result)

    async def get_loa(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_loa(pk)
        return await self.serialize_loa(result)

    async def get_loas_by_region(self, region_id: int) -> ReturnDict:
        result = await self.repository.get_loas_by_region(region_id)
        return await self.serialize_loa(result)

    async def update_loa(self, loa_id: int, data: dict) -> ReturnDict:
        if loa_id is None or loa_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_loa(loa_id, data)
        if result is None:
            raise ValueError("LOA not found")
        return await self.serialize_loa(result)

    async def delete_loa(self, pk: int) -> bool:
        return await self.repository.delete_loa(pk)

    @staticmethod
    async def serialize_loa(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = LOASerializer(result, many=True)
        else:
            serializer = LOASerializer(result)
        return serializer.data
