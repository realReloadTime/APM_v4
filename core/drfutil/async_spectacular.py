from drf_spectacular.views import SpectacularAPIView
from core.drfutil.async_apiview import AsyncAPIView
from core.drfutil.requests import AsyncRequest
from rest_framework.permissions import AllowAny

class AsyncSpectacularAPIView(AsyncAPIView, SpectacularAPIView):
    authentication_classes = []  # Отключаем аутентификацию
    permission_classes = [AllowAny]  # Разрешаем доступ всем

    def initialize_request(self, request, *args, **kwargs) -> AsyncRequest:
        return AsyncRequest(
            request,
            parsers=self.get_parsers(),
            authenticators=self.get_authenticators(),
            negotiator=self.get_content_negotiator(),
            parser_context=self.get_parser_context(request),
        )

    async def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)