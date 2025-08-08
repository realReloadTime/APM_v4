from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import MeasuresTaken
from core.serializers import MeasuresTakenSerializer

from core.logic.event import EventRepository


class MeasuresTakenRepository:
    @staticmethod
    async def create_measures_taken(data: dict) -> MeasuresTaken:
        event_id = data.get('event_id')
        if event_id:
            data['event'] = await EventRepository.get_event(event_id)
        else:
            raise ValueError('event_id обязательное поле для создания MeasuresTaken')
        data.pop('event_id', None)
        return await MeasuresTaken.objects.acreate(**data)

    @staticmethod
    async def get_measures_taken(pk: int | None) -> MeasuresTaken | list[MeasuresTaken]:
        if pk is None:
            return [measures_taken async for measures_taken in MeasuresTaken.objects.select_related('event').all()]
        try:
            return await MeasuresTaken.objects.select_related('event').aget(id=pk)
        except MeasuresTaken.DoesNotExist:
            raise ValueError(f"MeasuresTaken с ID {pk} не существует")

    @staticmethod
    async def update_measures_taken(pk: int, data: dict) -> MeasuresTaken | None:
        event_id = data.get('event_id')
        if event_id:
            data['event'] = await EventRepository.get_event(event_id)
            data.pop('event_id', None)

        updated = await MeasuresTaken.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await MeasuresTaken.objects.aget(id=pk)

    @staticmethod
    async def delete_measures_taken(pk: int) -> bool:
        result = await MeasuresTaken.objects.filter(id=pk).adelete()
        return bool(result)


class MeasuresTakenService:
    def __init__(self, repository: MeasuresTakenRepository):
        self.repository = repository

    async def create_measures_taken(self, data: dict) -> ReturnDict:
        result = await self.repository.create_measures_taken(data)
        return await self.serialize_measures_taken(result)

    async def get_measures_taken(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_measures_taken(pk)
        return await self.serialize_measures_taken(result)

    async def update_measures_taken(self, measures_taken_id: int, data: dict) -> ReturnDict:
        if measures_taken_id is None or measures_taken_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_measures_taken(measures_taken_id, data)
        return await self.serialize_measures_taken(result)

    async def delete_measures_taken(self, pk: int) -> bool:
        return await self.repository.delete_measures_taken(pk)

    @staticmethod
    async def serialize_measures_taken(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = MeasuresTakenSerializer(result, many=True)
        else:
            serializer = MeasuresTakenSerializer(result)
        return serializer.data
