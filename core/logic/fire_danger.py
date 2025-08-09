from asgiref.sync import sync_to_async
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import FireDanger
from core.serializers import FireDangerSerializer
from core.logic.event import EventRepository
from core.logic.source import SourceRepository


class FireDangerRepository:
    @staticmethod
    async def create_fire_danger(data: dict) -> FireDanger:
        required_fields = [('event', EventRepository.get_event),
                           ('source', SourceRepository.get_source)]

        for field, repo in required_fields:
            oid = data.get(field + '_id')
            if oid:
                field_object = await repo(oid)
                data[field] = field_object
            else:
                raise ValueError(f'{field + "_id"} обязательное поле для создания FireDanger')
            data.pop(field + '_id', None)

        return await FireDanger.objects.acreate(**data)

    @staticmethod
    async def get_fire_danger(pk: int | None) -> FireDanger | list[FireDanger]:
        if pk is None:
            fires = [fire async for fire in FireDanger.objects.all()]
            return fires
        try:
            fire = await FireDanger.objects.aget(id=pk)
            return fire
        except FireDanger.DoesNotExist:
            raise ValueError(f'FireDanger с ID {pk} не существует')

    @staticmethod
    async def get_fire_danger_by_event(event_id: int) -> FireDanger:
        fire = await FireDanger.objects.filter(event_id=event_id).aget()
        return fire

    @staticmethod
    async def update_fire_danger(pk: int, data: dict) -> FireDanger | None:
        fields = [('event', EventRepository.get_event),
                  ('source', SourceRepository.get_source)]

        for field, repo in fields:
            oid = data.get(field + '_id')
            if oid:
                field_object = await repo(oid)
                data[field] = field_object
            data.pop(field + '_id', None)

        updated = await FireDanger.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await FireDanger.objects.aget(id=pk)

    @staticmethod
    async def delete_fire_danger(pk: int) -> bool:
        result = await FireDanger.objects.filter(id=pk).adelete()
        return bool(result)


class FireDangerService:
    def __init__(self, repository: FireDangerRepository):
        self.repository = repository

    async def create_fire_danger(self, data: dict) -> ReturnDict:
        result = await self.repository.create_fire_danger(data)
        return await self.serialize_fire_danger(result)

    async def get_fire_danger(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_fire_danger(pk)
        return await self.serialize_fire_danger(result)

    async def get_fire_danger_by_event(self, event_id: int) -> ReturnDict:
        if event_id > 0:
            result = await self.repository.get_fire_danger_by_event(event_id)
            return await self.serialize_fire_danger(result)
        else:
            raise ValueError('event_id должен быть больше 0')

    async def update_fire_danger(self, pk: int, data: dict) -> ReturnDict:
        if pk < 1:
            raise ValueError('ID не может быть меньше 1')
        result = await self.repository.update_fire_danger(pk, data)
        if result is None:
            raise ValueError('FireDanger с этим ID не найден')
        return await self.serialize_fire_danger(result)

    async def delete_fire_danger(self, pk: int):
        return await self.repository.delete_fire_danger(pk)

    @staticmethod
    async def serialize_fire_danger(result) -> ReturnDict:
        def serialize():
            if isinstance(result, list):
                serializer = FireDangerSerializer(result, many=True)
            else:
                serializer = FireDangerSerializer(result)
            return serializer.data

        return await sync_to_async(serialize)()
