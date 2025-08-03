from django.utils.translation import gettext_lazy as _
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission
from core.drfutil.requests import AsyncRequest
from rest_framework.throttling import BaseThrottle
import asyncio
from core.models import Token, CustomUser


async def get_token(model, key):
    try:
        return await model.objects.select_related('user').aget(key=key)
    except model.DoesNotExist:
        return None


def get_authorization_header(request):
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, str):
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class AsyncAuthentication(BaseAuthentication):
    keyword = 'Token'
    model = Token

    async def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(_('Invalid token header. No credentials provided.'))
        elif len(auth) > 2:
            raise exceptions.AuthenticationFailed(_('Invalid token header. Token string should not contain spaces.'))
        try:
            token = auth[1].decode()
        except UnicodeError:
            raise exceptions.AuthenticationFailed(
                _('Invalid token header. Token string should not contain invalid characters.'))
        return await self.authenticate_credentials(token)

    async def authenticate_credentials(self, key):
        token = await get_token(self.model, key)
        if not token:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
        return token.user, token

    async def authenticate_header(self, request):
        return self.keyword


class AsyncPermission(BasePermission):
    async def has_permission(self, request: AsyncRequest, view) -> bool:
        await asyncio.sleep(0.01)
        return True


class AsyncThrottle(BaseThrottle):
    async def allow_request(self, request: AsyncRequest, view) -> bool:
        await asyncio.sleep(0.01)
        return True


class AsyncIsAuthenticated(BasePermission):
    async def has_permission(self, request: AsyncRequest, view):
        return bool(request.user and request.user.is_authenticated)
