from asgiref.sync import sync_to_async
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Event
from core.serializers import EventSerializer

from core.logic.loa import LOARepository
from core.logic.category import CategoryRepository
from core.logic.location import LocationRepository
from core.logic.measures_taken import MeasuresTakenRepository
from core.logic.attachment import AttachmentRepository
from core.logic.user import UserRepository

from django.db.models import aprefetch_related_objects


class EventRepository:
    @staticmethod
    async def create_event(data: dict) -> Event:
        loa_id = data.get('loa_id')
        category_id = data.get('category_id')
        location_id = data.get('location_id')
        measures_id = data.get('measures_id')
        attachments_id = data.get('attachments_id')
        created_by_id = data.get('created_by_id')

        if loa_id:
            loa = await LOARepository.get_loa(loa_id)
            data['loa'] = loa
        else:
            raise ValueError('loa_id обязательное поле для создания Event')

        data.pop('loa_id', None)

        if category_id:
            category = await CategoryRepository.get_category(category_id)
            data['category'] = category
        else:
            raise ValueError('category_id обязательное поле для создания Event')

        data.pop('category_id', None)

        if location_id:
            location = await LocationRepository.get_location(location_id)
            data['location'] = location
        else:
            raise ValueError('location_id обязательное поле для создания Event')

        data.pop('location_id', None)

        if measures_id:
            data['measures'] = list()
            for measure_pk in measures_id:
                measures = await MeasuresTakenRepository.get_measures_taken(measure_pk)
                data['measures'].append(measures)
            data.pop('measures_id', None)

        if attachments_id:
            data['attachments'] = list()
            for attachment_pk in attachments_id:
                attachments = await AttachmentRepository.get_attachment(attachment_pk)
                data['attachments'].append(attachments)
            data.pop('attachments_id', None)

        if created_by_id:
            current_user = await UserRepository.get_user(created_by_id)
            data['created_by'] = current_user
            data.pop('created_by_id')

        return await Event.objects.acreate(**data)

    @staticmethod
    async def get_event(pk: int | None) -> Event | list[Event]:
        if pk is None:
            events = [event async for event in Event.objects.select_related('loa', 'category', 'location', 'created_by').all()]

            # применяю aprefetch_related_objects для предварительной загрузки measures и attachments
            await aprefetch_related_objects(events, 'measures', 'attachments')
            return events
        try:
            event = await Event.objects.select_related('loa', 'category', 'location', 'created_by').aget(id=pk)
            await aprefetch_related_objects([event], 'measures', 'attachments')
            return event
        except Event.DoesNotExist:
            raise ValueError(f"Event с ID {pk} не существует")

    @staticmethod
    async def update_event(pk: int, data: dict) -> Event | None:
        loa_id = data.get('loa_id')
        category_id = data.get('category_id')
        location_id = data.get('location_id')
        measures_id = data.get('measures_id')
        attachments_id = data.get('attachments_id')
        created_by_id = data.get('created_by_id')

        if loa_id:
            loa = await LOARepository.get_loa(loa_id)
            data['loa'] = loa

        data.pop('loa_id', None)

        if category_id:
            category = await CategoryRepository.get_category(category_id)
            data['category'] = category

        data.pop('category_id', None)

        if location_id:
            location = await LocationRepository.get_location(location_id)
            data['location'] = location

        data.pop('location_id', None)

        if measures_id:
            data['measures'] = list()
            for measure_pk in measures_id:
                measures = await MeasuresTakenRepository.get_measures_taken(measure_pk)
                data['measures'].append(measures)
            data.pop('measures_id', None)

        if attachments_id:
            data['attachments'] = list()
            for attachment_pk in attachments_id:
                attachments = await AttachmentRepository.get_attachment(attachment_pk)
                data['attachments'].append(attachments)
            data.pop('attachments_id', None)

        if created_by_id:
            current_user = await UserRepository.get_user(created_by_id)
            data['created_by'] = current_user
            data.pop('created_by_id')

        updated = await Event.objects.filter(id=pk).aupdate(**data)

        if not updated:
            return None

        event = await Event.objects.select_related('loa', 'category', 'location', 'created_by').aget(id=pk)
        await aprefetch_related_objects([event], 'measures', 'attachments')
        return event

    @staticmethod
    async def delete_event(pk: int) -> bool:
        result = await Event.objects.filter(id=pk).adelete()
        return bool(result)


class EventService:
    def __init__(self, repository: EventRepository):
        self.repository = repository

    async def create_event(self, data: dict) -> ReturnDict:
        result = await self.repository.create_event(data)
        return await self.serialize_event(result)

    async def get_event(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_event(pk)
        return await self.serialize_event(result)

    async def update_event(self, event_id: int, data: dict) -> ReturnDict:
        if event_id is None or event_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_event(event_id, data)
        if result is None:
            raise ValueError("Event not found")
        return await self.serialize_event(result)

    async def delete_event(self, pk: int) -> bool:
        return await self.repository.delete_event(pk)

    @staticmethod
    async def serialize_event(result) -> ReturnDict:
        def serialize():
            if isinstance(result, list):
                serializer = EventSerializer(result, many=True)
            else:
                serializer = EventSerializer(result)
            return serializer.data

        return await sync_to_async(serialize)()
