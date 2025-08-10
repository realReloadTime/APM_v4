from asgiref.sync import sync_to_async
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import HydrologicalDanger
from core.serializers import HydrologicalDangerSerializer
from core.logic.event import EventRepository
from core.logic.source import SourceRepository


class HydrologicalDangerRepository:
    @staticmethod
    async def create_hydrological_danger(data: dict) -> HydrologicalDanger:
        required_fields = [('event', EventRepository.get_event),
                           ('source', SourceRepository.get_source)]

        for field, repo in required_fields:
            oid = data.get(field + '_id')
            if oid:
                field_object = await repo(oid)
                data[field] = field_object
            else:
                raise ValueError(f'{field + "_id"} обязательное поле для создания HydrologicalDanger')
            data.pop(field + '_id', None)

        return await HydrologicalDanger.objects.acreate(**data)

    @staticmethod
    async def get_hydrological_danger(pk: int | None) -> HydrologicalDanger | list[HydrologicalDanger]:
        if pk is None:
            hydros = [hydro async for hydro in HydrologicalDanger.objects.all()]
            return hydros
        try:
            hydro = await HydrologicalDanger.objects.aget(id=pk)
            return hydro
        except HydrologicalDanger.DoesNotExist:
            raise ValueError(f'HydrologicalDanger с ID {pk} не существует')

    @staticmethod
    async def get_hydrological_danger_by_event(event_id: int) -> HydrologicalDanger:
        hydro = await HydrologicalDanger.objects.filter(event_id=event_id).aget()
        return hydro

    @staticmethod
    async def update_hydrological_danger(pk: int, data: dict) -> HydrologicalDanger | None:
        fields = [('event', EventRepository.get_event),
                  ('source', SourceRepository.get_source)]

        for field, repo in fields:
            oid = data.get(field + '_id')
            if oid:
                field_object = await repo(oid)
                data[field] = field_object
            data.pop(field + '_id', None)

        updated = await HydrologicalDanger.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await HydrologicalDanger.objects.aget(id=pk)

    @staticmethod
    async def delete_hydrological_danger(pk: int) -> bool:
        result = await HydrologicalDanger.objects.filter(id=pk).adelete()
        return bool(result)


class HydrologicalDangerService:
    def __init__(self, repository: HydrologicalDangerRepository):
        self.repository = repository

    async def create_hydrological_danger(self, data: dict) -> ReturnDict:
        result = await self.repository.create_hydrological_danger(data)
        return await self.serialize_hydrological_danger(result)

    async def get_hydrological_danger(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_hydrological_danger(pk)
        return await self.serialize_hydrological_danger(result)

    async def get_hydrological_danger_by_event(self, event_id: int) -> ReturnDict:
        if event_id > 0:
            result = await self.repository.get_hydrological_danger_by_event(event_id)
            return await self.serialize_hydrological_danger(result)
        else:
            raise ValueError('event_id должен быть больше 0')

    async def update_hydrological_danger(self, pk: int, data: dict) -> ReturnDict:
        if pk < 1:
            raise ValueError('ID не может быть меньше 1')
        result = await self.repository.update_hydrological_danger(pk, data)
        if result is None:
            raise ValueError('HydrologicalDanger с этим ID не найден')
        return await self.serialize_hydrological_danger(result)

    async def delete_hydrological_danger(self, pk: int):
        return await self.repository.delete_hydrological_danger(pk)

    @staticmethod
    async def serialize_hydrological_danger(result) -> ReturnDict:
        def serialize():
            if isinstance(result, list):
                serializer = HydrologicalDangerSerializer(result, many=True)
            else:
                serializer = HydrologicalDangerSerializer(result)
            return serializer.data

        return await sync_to_async(serialize)()
