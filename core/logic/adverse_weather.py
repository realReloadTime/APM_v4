from asgiref.sync import sync_to_async
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import AdverseWeather
from core.serializers import AdverseWeatherSerializer
from core.logic.event import EventRepository
from core.logic.source import SourceRepository
from core.logic.condition import ConditionRepository
from core.logic.precipitation import PrecipitationRepository


class AdverseWeatherRepository:
    @staticmethod
    async def create_adverse_weather(data: dict) -> AdverseWeather:
        required_fields = [('event', EventRepository.get_event),
                           ('source', SourceRepository.get_source),
                           ('condition', ConditionRepository.get_condition),
                           ('precipitation', PrecipitationRepository.get_precipitation)]

        for field, repo in required_fields:
            oid = data.get(field + '_id')
            if oid:
                field_object = await repo(oid)
                data[field] = field_object
            else:
                raise ValueError(f'{field + "_id"} обязательное поле для создания AdverseWeather')
            data.pop(field + '_id', None)

        return await AdverseWeather.objects.acreate(**data)

    @staticmethod
    async def get_adverse_weather(pk: int | None) -> AdverseWeather | list[AdverseWeather]:
        if pk is None:
            weathers = [weather async for weather in AdverseWeather.objects.all()]
            return weathers
        try:
            weather = await AdverseWeather.objects.aget(id=pk)
            return weather
        except AdverseWeather.DoesNotExist:
            raise ValueError(f'AdverseWeather с ID {pk} не существует')

    @staticmethod
    async def get_adverse_weather_by_event(event_id: int) -> AdverseWeather:
        weather = await AdverseWeather.objects.filter(event_id=event_id).aget()
        return weather

    @staticmethod
    async def update_adverse_weather(pk: int, data: dict) -> AdverseWeather | None:
        fields = [('event', EventRepository.get_event),
                  ('source', SourceRepository.get_source),
                  ('condition', ConditionRepository.get_condition),
                  ('precipitation', PrecipitationRepository.get_precipitation)]

        for field, repo in fields:
            oid = data.get(field + '_id')
            if oid:
                field_object = await repo(oid)
                data[field] = field_object
            data.pop(field + '_id', None)

        updated = await AdverseWeather.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await AdverseWeather.objects.aget(id=pk)

    @staticmethod
    async def delete_adverse_weather(pk: int) -> bool:
        result = await AdverseWeather.objects.filter(id=pk).adelete()
        return bool(result)


class AdverseWeatherService:
    def __init__(self, repository: AdverseWeatherRepository):
        self.repository = repository

    async def create_adverse_weather(self, data: dict) -> ReturnDict:
        result = await self.repository.create_adverse_weather(data)
        return await self.serialize_adverse_weather(result)

    async def get_adverse_weather(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_adverse_weather(pk)
        return await self.serialize_adverse_weather(result)

    async def get_adverse_weather_by_event(self, event_id: int) -> ReturnDict:
        if event_id > 0:
            result = await self.repository.get_adverse_weather_by_event(event_id)
            return await self.serialize_adverse_weather(result)
        else:
            raise ValueError('event_id должен быть больше 0')

    async def update_adverse_weather(self, pk: int, data: dict) -> ReturnDict:
        if pk < 1:
            raise ValueError('ID не может быть меньше 1')
        result = await self.repository.update_adverse_weather(pk, data)
        if result is None:
            raise ValueError('AdverseWeather с этим ID не найден')
        return await self.serialize_adverse_weather(result)

    async def delete_adverse_weather(self, pk: int):
        return await self.repository.delete_adverse_weather(pk)

    @staticmethod
    async def serialize_adverse_weather(result) -> ReturnDict:
        def serialize():
            if isinstance(result, list):
                serializer = AdverseWeatherSerializer(result, many=True)
            else:
                serializer = AdverseWeatherSerializer(result)
            return serializer.data

        return await sync_to_async(serialize)()
