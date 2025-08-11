from channels.generic.websocket import AsyncWebsocketConsumer
import json

from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from core.serializers import EventSerializer


class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string'].decode('utf-8')  # получение токена
        token = None
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break

        if not token:
            await self.close()
            return

        auth = JWTAuthentication()
        try:
            validated_token = await sync_to_async(auth.get_validated_token)(token)
            user = await sync_to_async(auth.get_user)(validated_token)
            self.scope['user'] = user
        except (InvalidToken, TokenError):
            await self.close()
            return

        if not self.scope['user'].is_authenticated:
            await self.close()
            return

        await self.accept()

        try:
            await self.channel_layer.group_add('events_group', self.channel_name)
        except ConnectionError as e:
            print(f"Redis connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('events_group', self.channel_name)

    # обработка сообщений от клиента
    async def receive(self, text_data=None, bytes_data=None):
        pass

    # метод для отправки обновлений
    async def event_update(self, event: EventSerializer):
        await self.send(text_data=json.dumps({
            'type': 'event.update',
            'data': event
        }))