from django.contrib.auth.middleware import get_user
from django.utils.functional import SimpleLazyObject
from asgiref.sync import sync_to_async

class AsyncAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        scope['user'] = SimpleLazyObject(lambda: sync_to_async(get_user)(scope))
        return await self.inner(scope, receive, send)