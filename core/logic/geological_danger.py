from asgiref.sync import sync_to_async
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import GeologicalDanger
from core.serializers import GeologicalDangerSerializer
from core.logic.event import EventRepository
from core.logic.source import SourceRepository


class GeologicalDangerRepository:
    @staticmethod
    async def create_geological_danger(data: dict) -> GeologicalDanger:
        required_fields = [('event', EventRepository.get_event),
                           ('source', SourceRepository.get_source)]

        for field, repo in required_fields:
            oid = data.get(field + '_id')
            if oid:
                field_object = await repo(oid)
                data[field] = field_object
            else:
                raise ValueError(f'{field + "_id"} обязательное поле для создания GeologicalDanger')
            data.pop(field + '_id', None)

        return await GeologicalDanger.objects.acreate(**data)

    @staticmethod
    async def get_geological_danger(pk: int | None) -> GeologicalDanger | list[GeologicalDanger]:
        if pk is None:
            geos = [geo async for geo in GeologicalDanger.objects.all()]
            return geos
        try:
            geo = await GeologicalDanger.objects.aget(id=pk)
            return geo
        except GeologicalDanger.DoesNotExist:
            raise ValueError(f'GeologicalDanger с ID {pk} не существует')

    @staticmethod
    async def get_geological_danger_by_event(event_id: int) -> GeologicalDanger:
        geo = await GeologicalDanger.objects.filter(event_id=event_id).aget()
        return geo

    @staticmethod
    async def update_geological_danger(pk: int | None, data: dict, event_pk: int | None) -> GeologicalDanger | None:
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
            updated = await GeologicalDanger.objects.filter(event=event_pk).aupdate(**data)
        else:
            updated = await GeologicalDanger.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None

        if event_pk is not None:
            return await GeologicalDanger.objects.aget(event=event_pk)
        return await GeologicalDanger.objects.aget(id=pk)

    @staticmethod
    async def delete_geological_danger(pk: int) -> bool:
        result = await GeologicalDanger.objects.filter(id=pk).adelete()
        return bool(result)


class GeologicalDangerService:
    def __init__(self, repository: GeologicalDangerRepository):
        self.repository = repository

    async def create_geological_danger(self, data: dict) -> ReturnDict:
        result = await self.repository.create_geological_danger(data)
        return await self.serialize_geological_danger(result)

    async def get_geological_danger(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_geological_danger(pk)
        return await self.serialize_geological_danger(result)

    async def get_geological_danger_by_event(self, event_id: int) -> ReturnDict:
        if event_id > 0:
            result = await self.repository.get_geological_danger_by_event(event_id)
            return await self.serialize_geological_danger(result)
        else:
            raise ValueError('event_id должен быть больше 0')

    async def update_geological_danger(self, data: dict, pk: int = None, event_id: int = None) -> ReturnDict:
        if pk is None and event_id is None:
            raise ValueError("Can't update without any ID key.")
        result = await self.repository.update_geological_danger(pk, data, event_id)
        if result is None:
            raise ValueError('GeologicalDanger с этим ID не найден')
        return await self.serialize_geological_danger(result)

    async def delete_geological_danger(self, pk: int):
        return await self.repository.delete_geological_danger(pk)

    @staticmethod
    async def serialize_geological_danger(result) -> ReturnDict:
        def serialize():
            if isinstance(result, list):
                serializer = GeologicalDangerSerializer(result, many=True)
            else:
                serializer = GeologicalDangerSerializer(result)
            return serializer.data

        return await sync_to_async(serialize)()
