from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Subsystem
from core.serializers import SubsystemSerializer
from core.logic.system import SystemRepository


class SubsystemRepository:
    @staticmethod
    async def create_subsystem(data: dict) -> Subsystem:
        system_id = data.get('system_id')

        if system_id:
            system = await SystemRepository.get_system(system_id)
            data['system'] = system
        else:
            raise ValueError("system_id обязательное поле для создания Subsystem")

        data.pop('system_id', None)
        return await Subsystem.objects.acreate(**data)

    @staticmethod
    async def get_subsystem(pk: int | None) -> Subsystem | list[Subsystem]:
        if pk is None:
            return [subsystem async for subsystem in Subsystem.objects.select_related('system').all()]
        try:
            return await Subsystem.objects.select_related('system').aget(id=pk)
        except Subsystem.DoesNotExist:
            raise ValueError(f"Subsystem с ID {pk} не существует")

    @staticmethod
    async def get_subsystems_by_system(system_id: int) -> list[Subsystem]:
        await SystemRepository.get_system(system_id)  # проверка существования системы
        # возврат подсистем, связанных с системой
        return [subsystem async for subsystem in
                Subsystem.objects.select_related('system').filter(system_id=system_id)]

    @staticmethod
    async def update_subsystem(pk: int, data: dict) -> Subsystem | None:
        # system_id необязательное поле - если не указано, связь не меняется
        system_id = data.get('system_id')
        if system_id:
            system = await SystemRepository.get_system(system_id)
            data['system'] = system

        data.pop('system_id', None)
        updated = await Subsystem.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await Subsystem.objects.select_related('system').aget(id=pk)

    @staticmethod
    async def delete_subsystem(pk: int) -> bool:
        result = await Subsystem.objects.filter(id=pk).adelete()
        return bool(result)


class SubsystemService:
    def __init__(self, repository: SubsystemRepository):
        self.repository = repository

    async def create_subsystem(self, data: dict) -> ReturnDict:
        result = await self.repository.create_subsystem(data)
        return await self.serialize_subsystem(result)

    async def get_subsystem(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_subsystem(pk)
        return await self.serialize_subsystem(result)

    async def get_subsystems_by_system(self, system_id: int) -> ReturnDict:
        result = await self.repository.get_subsystems_by_system(system_id)
        return await self.serialize_subsystem(result)

    async def update_subsystem(self, subsystem_id: int, data: dict) -> ReturnDict:
        if subsystem_id is None or subsystem_id < 1:
            raise ValueError("Can't update without ID key.")

        result = await self.repository.update_subsystem(subsystem_id, data)
        if result is None:
            raise ValueError("Subsystem not found")
        return await self.serialize_subsystem(result)

    async def delete_subsystem(self, pk: int) -> bool:
        return await self.repository.delete_subsystem(pk)

    @staticmethod
    async def serialize_subsystem(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = SubsystemSerializer(result, many=True)
        else:
            serializer = SubsystemSerializer(result)
        return serializer.data
