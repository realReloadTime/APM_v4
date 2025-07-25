from rest_framework import status
from rest_framework.response import Response

from core.logic.subsystem_status import (SubsystemStatusService,
                                         SubsystemStatusRepository,
                                         SubsystemStatusSerializer)
from core.models import SubsystemStatus
from core.drfutil.auth import AsyncIsAuthenticated, AsyncAuthentication
from core.drfutil.async_apiview import AsyncAPIView


class SubsystemStatusCRUD(AsyncAPIView):
    authentication_classes = [AsyncAuthentication, ]
    permission_classes = [AsyncIsAuthenticated, ]
    serializer_class = SubsystemStatusSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = SubsystemStatusService(SubsystemStatusRepository())

    async def get(self, request, pk=None):
        try:
            if pk:
                response = await self.service.get_subsystem_status(pk)
                return Response(response.data, status=status.HTTP_200_OK)
            else:
                response = await self.service.get_subsystem_status(None)
                return Response(response.data, status=status.HTTP_200_OK)
        except SubsystemStatus.DoesNotExist:
            return Response(
                {"error": "SubsystemStatus not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    async def post(self, request):
        try:
            response = await self.service.create_subsystem_status(request.data)
            return Response(response.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    async def put(self, request, pk):
        try:
            data = request.data.copy()
            data['id'] = pk
            response = await self.service.update_subsystem_status(data)

            if response is None:
                return Response(
                    {"error": "SubsystemStatus not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(response.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    async def delete(self, request, pk):
        try:
            success = await self.service.delete_subsystem_status(pk)
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"error": "SubsystemStatus not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
