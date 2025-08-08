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
        required_fields = [('event',  EventRepository.get_event),
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


