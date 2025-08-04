from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import System
from core.serializers import SystemSerializer


class SystemRepository:
    @staticmethod
    async def create_system(data: dict) -> System:
        return await System.objects.acreate(**data)

    @staticmethod
    async def get_system(pk: int | None) -> System | list[System]:
        if pk is None:
            return [system async for system in System.objects.all()]
        try:
            return await System.objects.aget(id=pk)
        except System.DoesNotExist:
            raise ValueError(f"System с ID {pk} не существует")

    @staticmethod
    async def update_system(pk: int, data: dict) -> System | None:
        updated = await System.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await System.objects.aget(id=pk)

    @staticmethod
    async def delete_system(pk: int) -> bool:
        result = await System.objects.filter(id=pk).adelete()
        return bool(result)


class SystemService:
    def __init__(self, repository: SystemRepository):
        self.repository = repository

    async def create_system(self, data: dict) -> ReturnDict:
        result = await self.repository.create_system(data)
        return await self.serialize_system(result)

    async def get_system(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_system(pk)
        return await self.serialize_system(result)

    async def update_system(self, system_id: int, data: dict) -> ReturnDict:
        if system_id is None or system_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_system(system_id, data)
        return await self.serialize_system(result)

    async def delete_system(self, pk: int) -> bool:
        return await self.repository.delete_system(pk)

    @staticmethod
    async def serialize_system(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = SystemSerializer(result, many=True)
        else:
            serializer = SystemSerializer(result)
        return serializer.data
