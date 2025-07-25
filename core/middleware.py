from django.contrib.auth import get_user
from channels.db import database_sync_to_async

class AsyncAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        scope['user'] = self.get_user
        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_user(self, scope):
        return get_user(scope)