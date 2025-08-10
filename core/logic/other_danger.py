from asgiref.sync import sync_to_async
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import OtherDanger
from core.serializers import OtherDangerSerializer
from core.logic.event import EventRepository
from core.logic.source import SourceRepository


class OtherDangerRepository:
    @staticmethod
    async def create_other_danger(data: dict) -> OtherDanger:
        required_fields = [('event', EventRepository.get_event),
                           ('source', SourceRepository.get_source)]

        for field, repo in required_fields:
            oid = data.get(field + '_id')
            if oid:
                field_object = await repo(oid)
                data[field] = field_object
            else:
                raise ValueError(f'{field + "_id"} обязательное поле для создания OtherDanger')
            data.pop(field + '_id', None)

        return await OtherDanger.objects.acreate(**data)

    @staticmethod
    async def get_other_danger(pk: int | None) -> OtherDanger | list[OtherDanger]:
        if pk is None:
            dangers = [danger async for danger in OtherDanger.objects.all()]
            return dangers
        try:
            danger = await OtherDanger.objects.aget(id=pk)
            return danger
        except OtherDanger.DoesNotExist:
            raise ValueError(f'OtherDanger с ID {pk} не существует')

    @staticmethod
    async def get_other_danger_by_event(event_id: int) -> OtherDanger:
        danger = await OtherDanger.objects.filter(event_id=event_id).aget()
        return danger

    @staticmethod
    async def update_other_danger(pk: int, data: dict) -> OtherDanger | None:
        fields = [('event', EventRepository.get_event),
                  ('source', SourceRepository.get_source)]

        for field, repo in fields:
            oid = data.get(field + '_id')
            if oid:
                field_object = await repo(oid)
                data[field] = field_object
            data.pop(field + '_id', None)

        updated = await OtherDanger.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await OtherDanger.objects.aget(id=pk)

    @staticmethod
    async def delete_other_danger(pk: int) -> bool:
        result = await OtherDanger.objects.filter(id=pk).adelete()
        return bool(result)


class OtherDangerService:
    def __init__(self, repository: OtherDangerRepository):
        self.repository = repository

    async def create_other_danger(self, data: dict) -> ReturnDict:
        result = await self.repository.create_other_danger(data)
        return await self.serialize_other_danger(result)

    async def get_other_danger(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_other_danger(pk)
        return await self.serialize_other_danger(result)

    async def get_other_danger_by_event(self, event_id: int) -> ReturnDict:
        if event_id > 0:
            result = await self.repository.get_other_danger_by_event(event_id)
            return await self.serialize_other_danger(result)
        else:
            raise ValueError('event_id должен быть больше 0')

    async def update_other_danger(self, pk: int, data: dict) -> ReturnDict:
        if pk < 1:
            raise ValueError('ID не может быть меньше 1')
        result = await self.repository.update_other_danger(pk, data)
        if result is None:
            raise ValueError('OtherDanger с этим ID не найден')
        return await self.serialize_other_danger(result)

    async def delete_other_danger(self, pk: int):
        return await self.repository.delete_other_danger(pk)

    @staticmethod
    async def serialize_other_danger(result) -> ReturnDict:
        def serialize():
            if isinstance(result, list):
                serializer = OtherDangerSerializer(result, many=True)
            else:
                serializer = OtherDangerSerializer(result)
            return serializer.data

        return await sync_to_async(serialize)()
