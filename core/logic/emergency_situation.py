from asgiref.sync import sync_to_async
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import EmergencySituation
from core.serializers import EmergencySituationSerializer
from core.logic.event import EventRepository
from core.logic.source import SourceRepository


class EmergencySituationRepository:
    @staticmethod
    async def create_emergency_situation(data: dict) -> EmergencySituation:
        required_fields = [('event', EventRepository.get_event),
                           ('source', SourceRepository.get_source)]

        for field, repo in required_fields:
            oid = data.get(field + '_id')
            if oid:
                field_object = await repo(oid)
                data[field] = field_object
            else:
                raise ValueError(f'{field + "_id"} обязательное поле для создания EmergencySituation')
            data.pop(field + '_id', None)

        return await EmergencySituation.objects.acreate(**data)

    @staticmethod
    async def get_emergency_situation(pk: int | None) -> EmergencySituation | list[EmergencySituation]:
        if pk is None:
            situations = [situation async for situation in EmergencySituation.objects.all()]
            return situations
        try:
            situation = await EmergencySituation.objects.aget(id=pk)
            return situation
        except EmergencySituation.DoesNotExist:
            raise ValueError(f'EmergencySituation с ID {pk} не существует')

    @staticmethod
    async def get_emergency_situation_by_event(event_id: int) -> EmergencySituation:
        situation = await EmergencySituation.objects.filter(event_id=event_id).aget()
        return situation

    @staticmethod
    async def update_emergency_situation(pk: int | None, data: dict, event_pk: int | None) -> EmergencySituation | None:
        fields = [('event', EventRepository.get_event),
                  ('source', SourceRepository.get_source)]

        for field, repo in fields:
            oid = data.get(field + '_id')
            data.pop(field + '_id', None)
            if event_pk is not None and field == 'event':  # защита от перезаписи event_id при получении данных по event_id
                continue
            if oid:
                field_object = await repo(oid)
                data[field] = field_object

        if event_pk is not None:
            updated = await EmergencySituation.objects.filter(event=event_pk).aupdate(**data)
        else:
            updated = await EmergencySituation.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None

        if event_pk is not None:
            return await EmergencySituation.objects.aget(event=event_pk)
        return await EmergencySituation.objects.aget(id=pk)

    @staticmethod
    async def delete_emergency_situation(pk: int) -> bool:
        result = await EmergencySituation.objects.filter(id=pk).adelete()
        return bool(result)


class EmergencySituationService:
    def __init__(self, repository: EmergencySituationRepository):
        self.repository = repository

    async def create_emergency_situation(self, data: dict) -> ReturnDict:
        result = await self.repository.create_emergency_situation(data)
        return await self.serialize_emergency_situation(result)

    async def get_emergency_situation(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_emergency_situation(pk)
        return await self.serialize_emergency_situation(result)

    async def get_emergency_situation_by_event(self, event_id: int) -> ReturnDict:
        if event_id > 0:
            result = await self.repository.get_emergency_situation_by_event(event_id)
            return await self.serialize_emergency_situation(result)
        else:
            raise ValueError('event_id должен быть больше 0')

    async def update_emergency_situation(self, data: dict, pk: int = None, event_id: int = None) -> ReturnDict:
        if pk is None and event_id is None:
            raise ValueError("Can't update without any ID key.")
        result = await self.repository.update_emergency_situation(pk, data, event_id)
        if result is None:
            raise ValueError('EmergencySituation с этим ID не найден')
        return await self.serialize_emergency_situation(result)

    async def delete_emergency_situation(self, pk: int):
        return await self.repository.delete_emergency_situation(pk)

    @staticmethod
    async def serialize_emergency_situation(result) -> ReturnDict:
        def serialize():
            if isinstance(result, list):
                serializer = EmergencySituationSerializer(result, many=True)
            else:
                serializer = EmergencySituationSerializer(result)
            return serializer.data

        return await sync_to_async(serialize)()
