from asgiref.sync import sync_to_async
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Event
from core.serializers import EventSerializer

from django.db.models import aprefetch_related_objects

from core.logic.loa import LOARepository
from core.logic.category import CategoryRepository
from core.logic.location import LocationRepository
from core.logic.user import UserRepository

from channels.layers import get_channel_layer

channel_layer = get_channel_layer()


class EventRepository:
    @staticmethod
    async def create_event(data: dict) -> Event:
        loa_id = data.get('loa_id')
        category_id = data.get('category_id')
        location_id = data.get('location_id')
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

        if created_by_id:
            current_user = await UserRepository.get_user(created_by_id)
            data['created_by'] = current_user
            data.pop('created_by_id')

        return await Event.objects.acreate(**data)

    @staticmethod
    async def get_event(
            pk: int | None = None,
            filters: dict | None = None,
            pagination: dict | None = None
    ) -> Event | dict:
        if pk is None:
            qs = Event.objects.order_by('-begin').select_related('loa', 'category', 'location', 'created_by').all()

            if filters:
                orm_filters = {}
                for key, value in filters.items():
                    # для полей с диапазоном дат (пока begin)
                    if key == 'start_date':
                        orm_filters['begin__gte'] = value
                    elif key == 'end_date':
                        orm_filters['begin__lte'] = value
                    else:
                        orm_filters[key] = value
                qs = qs.filter(**orm_filters)

            # применяем пагинацию
            if pagination:
                page = pagination.get('page', 1)
                page_size = pagination.get('page_size', 10)
                start = (page - 1) * page_size
                end = start + page_size
                total = await qs.acount()
                events = [event async for event in qs[start:end]]
            else:
                events = [event async for event in qs]
                total = len(events)

            if events:
                await aprefetch_related_objects(events, 'event_attachments', 'event_measures')

            return {
                'events': events,
                'total': total,
                'page': pagination.get('page', 1) if pagination else 1,
                'page_size': pagination.get('page_size', total) if pagination else total
            }
        try:
            event = await Event.objects.order_by('-begin').select_related('loa', 'category', 'location',
                                                                          'created_by').aget(id=pk)
            await aprefetch_related_objects([event], 'event_attachments', 'event_measures')

            return event
        except Event.DoesNotExist:
            raise ValueError(f"Event с ID {pk} не существует")

    @staticmethod
    async def update_event(pk: int, data: dict) -> Event | None:
        loa_id = data.get('loa_id')
        category_id = data.get('category_id')
        location_id = data.get('location_id')
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

        if created_by_id:
            current_user = await UserRepository.get_user(created_by_id)
            data['created_by'] = current_user
            data.pop('created_by_id')

        updated = await Event.objects.filter(id=pk).aupdate(**data)

        if not updated:
            return None

        event = await Event.objects.select_related('loa', 'category', 'location', 'created_by').aget(id=pk)
        await aprefetch_related_objects([event], 'event_attachments', 'event_measures')
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
        serialized_result = await self.serialize_event(result)

        await channel_layer.group_send('events_group', {  # группа для оповещения (consumers.py EventConsumer)
            'type': 'event_update',  # имя метода в consumer
            'event': serialized_result  # параметр метода
        })
        return serialized_result

    async def get_event(
            self,
            pk: int | None = None,
            filters: dict | None = None,
            pagination: dict | None = None
    ) -> ReturnDict | dict:
        result = await self.repository.get_event(pk, filters, pagination)

        # обработка пагинированного результата
        if isinstance(result, dict):
            events = result['events']
            serialized_data = await self.serialize_event(events)
            return {
                'results': serialized_data,
                'total': result['total'],
                'page': result['page'],
                'page_size': result['page_size']
            }

        return await self.serialize_event(result)

    async def update_event(self, event_id: int, data: dict) -> ReturnDict:
        if event_id is None or event_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_event(event_id, data)
        if result is None:
            raise ValueError("Event not found")

        serialized_result = await self.serialize_event(result)

        await channel_layer.group_send('events_group', {  # группа для оповещения (consumers.py EventConsumer)
            'type': 'event_update',  # имя метода в consumer
            'event': serialized_result  # параметр метода
        })
        return serialized_result

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
