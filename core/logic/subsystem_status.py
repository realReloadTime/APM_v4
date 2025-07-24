from asgiref.sync import sync_to_async
from django.db.models import QuerySet

from ..models import SubsystemStatus

from rest_framework.serializers import ModelSerializer


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
        else:
            return await SubsystemStatus.objects.aget(id=pk)

    @staticmethod
    async def update_subsystem_status(data: dict) -> SubsystemStatus | None:
        if 'id' not in data:
            raise ValueError("Can't update without ID key.")
        updated = await SubsystemStatus.objects.filter(id=data['id']).aupdate(**data)
        if not updated:
            return None
        return await SubsystemStatus.objects.aget(id=data['id'])


    @staticmethod
    async def delete_subsystem_status(pk: int) -> True | False:
        result = await SubsystemStatus.objects.filter(id=pk).adelete()
        return bool(result[0])


class SubsystemStatusService:  # бизнес-логика (связь между View и PostgreSQL)
    def __init__(self, repository: SubsystemStatusRepository):
        self.repository = repository