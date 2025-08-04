from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import SubsystemStatus
from core.serializers import SubsystemStatusSerializer


class SubsystemStatusRepository:  # CRUD логика чистой работы с БД
    @staticmethod
    async def create_subsystem_status(data: dict) -> SubsystemStatus:
        return await SubsystemStatus.objects.acreate(**data)

    @staticmethod
    async def get_subsystem_status(pk: int | None) -> SubsystemStatus | list[SubsystemStatus]:
        if pk is None:
            return [ss_status async for ss_status in SubsystemStatus.objects.all()]
        return await SubsystemStatus.objects.aget(id=pk)

    @staticmethod
    async def update_subsystem_status(pk: int, data: dict) -> SubsystemStatus | None:
        updated = await SubsystemStatus.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await SubsystemStatus.objects.aget(id=pk)

    @staticmethod
    async def delete_subsystem_status(pk: int) -> bool:
        result = await SubsystemStatus.objects.filter(id=pk).adelete()
        return bool(result)


class SubsystemStatusService:  # бизнес-логика (связь между View и PostgreSQL)
    def __init__(self, repository: SubsystemStatusRepository):
        self.repository = repository

    async def create_subsystem_status(self, data: dict) -> ReturnDict:
        result = await self.repository.create_subsystem_status(data)
        return await self.serialize_subsystem_status(result)

    async def get_subsystem_status(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_subsystem_status(pk)
        return await self.serialize_subsystem_status(result)

    async def update_subsystem_status(self, status_id: int, data: dict) -> ReturnDict:
        if status_id is None or status_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_subsystem_status(status_id, data)
        return await self.serialize_subsystem_status(result)

    async def delete_subsystem_status(self, pk: int) -> bool:
        return await self.repository.delete_subsystem_status(pk)

    @staticmethod
    async def serialize_subsystem_status(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = SubsystemStatusSerializer(result, many=True)
        else:
            serializer = SubsystemStatusSerializer(result)
        return serializer.data