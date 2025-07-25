from asgiref.sync import sync_to_async

from django.db.models import QuerySet
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response

from core.models import SubsystemStatus


class SubsystemStatusSerializer(ModelSerializer):  # ExampleSerializer(example) -> JSON response
    class Meta:
        model = SubsystemStatus
        fields = '__all__'


class SubsystemStatusRepository:  # CRUD логика чистой работы с БД
    @staticmethod
    async def create_subsystem_status(data: dict) -> SubsystemStatus:
        return await SubsystemStatus.objects.acreate(**data)

    @staticmethod
    async def get_subsystem_status(pk: int | None) -> SubsystemStatus | QuerySet[SubsystemStatus]:
        if pk is None:
            return await sync_to_async(SubsystemStatus.objects.all)()
        return await SubsystemStatus.objects.aget(id=pk)

    @staticmethod
    async def update_subsystem_status(data: dict) -> SubsystemStatus | None:
        updated = await SubsystemStatus.objects.filter(id=data['id']).aupdate(**data)
        if not updated:
            return None
        return await SubsystemStatus.objects.aget(id=data['id'])

    @staticmethod
    async def delete_subsystem_status(pk: int) -> True | False:
        result = await SubsystemStatus.objects.filter(id=pk).adelete()
        return bool(result)


class SubsystemStatusService:  # бизнес-логика (связь между View и PostgreSQL)
    def __init__(self, repository: SubsystemStatusRepository):
        self.repository = repository

    async def create_subsystem_status(self, data: dict) -> Response:
        result = await self.repository.create_subsystem_status(data)
        return await self.serialize_subsystem_status(result)

    async def get_subsystem_status(self, pk: int | None) -> Response:
        result = await self.repository.get_subsystem_status(pk)
        return await self.serialize_subsystem_status(result)

    async def update_subsystem_status(self, data: dict) -> Response:
        if 'id' not in data:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_subsystem_status(data)
        return await self.serialize_subsystem_status(result)

    async def delete_subsystem_status(self, pk: int) -> bool:
        return await self.repository.delete_subsystem_status(pk)

    @staticmethod
    async def serialize_subsystem_status(result) -> Response:
        from asgiref.sync import sync_to_async

        async def _serialize():
            if isinstance(result, list):
                serializer = SubsystemStatusSerializer(result, many=True)
            else:
                serializer = SubsystemStatusSerializer(result)
            return serializer.data

        data = await _serialize()
        return Response(data)