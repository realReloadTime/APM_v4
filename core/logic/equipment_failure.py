from asgiref.sync import sync_to_async
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import EquipmentFailure
from core.serializers import EquipmentFailureSerializer
from core.logic.event import EventRepository
from core.logic.object import ObjectRepository
from core.logic.subsystem import SubsystemRepository
from core.logic.subsystem_status import SubsystemStatusRepository


class EquipmentFailureRepository:
    @staticmethod
    async def create_equipment_failure(data: dict) -> EquipmentFailure:
        event_id = data.get('event_id')
        object_id = data.get('object_id')
        influenced_objects_id = data.get('influenced_objects_id', [])
        subsystem_id = data.get('subsystem_id')
        subsystem_status_id = data.get('subsystem_status_id')

        if event_id:
            event = await EventRepository.get_event(event_id)
            data['event'] = event
        else:
            raise ValueError('event_id обязательное поле для создания EquipmentFailure')
        data.pop('event_id', None)

        if object_id:
            obj = await ObjectRepository.get_object(object_id)
            data['object'] = obj
        else:
            raise ValueError('object_id обязательное поле для создания EquipmentFailure')
        data.pop('object_id', None)

        if influenced_objects_id:
            data['influenced_objects'] = []
            for obj_id in influenced_objects_id:
                obj = await ObjectRepository.get_object(obj_id)
                data['influenced_objects'].append(obj)
            data.pop('influenced_objects_id', None)

        if subsystem_id:
            subsystem = await SubsystemRepository.get_subsystem(subsystem_id)
            data['subsystem'] = subsystem
        else:
            raise ValueError('subsystem_id обязательное поле для создания EquipmentFailure')
        data.pop('subsystem_id', None)

        if subsystem_status_id:
            status = await SubsystemStatusRepository.get_subsystem_status(subsystem_status_id)
            data['subsystem_status'] = status
        data.pop('subsystem_status_id', None)

        return await EquipmentFailure.objects.acreate(**data)

    @staticmethod
    async def get_equipment_failure(pk: int | None) -> EquipmentFailure | list[EquipmentFailure]:
        if pk is None:
            failures = [failure async for failure in EquipmentFailure.objects.all()]
            return failures
        try:
            failure = await EquipmentFailure.objects.aget(id=pk)
            return failure
        except EquipmentFailure.DoesNotExist:
            raise ValueError(f"EquipmentFailure с ID {pk} не существует")

    @staticmethod
    async def update_equipment_failure(pk: int, data: dict) -> EquipmentFailure | None:
        event_id = data.get('event_id')
        object_id = data.get('object_id')
        influenced_objects_id = data.get('influenced_objects_id', [])
        subsystem_id = data.get('subsystem_id')
        subsystem_status_id = data.get('subsystem_status_id')

        if event_id:
            event = await EventRepository.get_event(event_id)
            data['event'] = event
        data.pop('event_id', None)

        if object_id:
            obj = await ObjectRepository.get_object(object_id)
            data['object'] = obj
        data.pop('object_id', None)

        if influenced_objects_id:
            data['influenced_objects'] = []
            for obj_id in influenced_objects_id:
                obj = await ObjectRepository.get_object(obj_id)
                data['influenced_objects'].append(obj)
            data.pop('influenced_objects_id', None)

        if subsystem_id:
            subsystem = await SubsystemRepository.get_subsystem(subsystem_id)
            data['subsystem'] = subsystem
        data.pop('subsystem_id', None)

        if subsystem_status_id:
            status = await SubsystemStatusRepository.get_subsystem_status(subsystem_status_id)
            data['subsystem_status'] = status
        data.pop('subsystem_status_id', None)

        updated = await EquipmentFailure.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None

        return await EquipmentFailure.objects.aget(id=pk)

    @staticmethod
    async def delete_equipment_failure(pk: int) -> bool:
        result = await EquipmentFailure.objects.filter(id=pk).adelete()
        return bool(result)


class EquipmentFailureService:
    def __init__(self, repository: EquipmentFailureRepository):
        self.repository = repository

    async def create_equipment_failure(self, data: dict) -> ReturnDict:
        result = await self.repository.create_equipment_failure(data)
        return await self.serialize_equipment_failure(result)

    async def get_equipment_failure(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_equipment_failure(pk)
        return await self.serialize_equipment_failure(result)

    async def update_equipment_failure(self, failure_id: int, data: dict) -> ReturnDict:
        if failure_id is None or failure_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_equipment_failure(failure_id, data)
        if result is None:
            raise ValueError("EquipmentFailure not found")
        return await self.serialize_equipment_failure(result)

    async def delete_equipment_failure(self, pk: int) -> bool:
        return await self.repository.delete_equipment_failure(pk)

    @staticmethod
    async def serialize_equipment_failure(result) -> ReturnDict:
        def serialize():
            if isinstance(result, list):
                serializer = EquipmentFailureSerializer(result, many=True)
            else:
                serializer = EquipmentFailureSerializer(result)
            return serializer.data

        return await sync_to_async(serialize)()
