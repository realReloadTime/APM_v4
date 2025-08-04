from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Condition
from core.serializers import ConditionSerializer


class ConditionRepository:
    @staticmethod
    async def create_condition(data: dict) -> Condition:
        return await Condition.objects.acreate(**data)

    @staticmethod
    async def get_condition(pk: int | None) -> Condition | list[Condition]:
        if pk is None:
            return [condition async for condition in Condition.objects.all()]
        try:
            return await Condition.objects.aget(id=pk)
        except Condition.DoesNotExist:
            raise ValueError(f"Condition с ID {pk} не существует")

    @staticmethod
    async def update_condition(pk: int, data: dict) -> Condition | None:
        updated = await Condition.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await Condition.objects.aget(id=pk)

    @staticmethod
    async def delete_condition(pk: int) -> bool:
        result = await Condition.objects.filter(id=pk).adelete()
        return bool(result)


class ConditionService:
    def __init__(self, repository: ConditionRepository):
        self.repository = repository

    async def create_condition(self, data: dict) -> ReturnDict:
        result = await self.repository.create_condition(data)
        return await self.serialize_condition(result)

    async def get_condition(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_condition(pk)
        return await self.serialize_condition(result)

    async def update_condition(self, condition_id: int, data: dict) -> ReturnDict:
        if condition_id is None or condition_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_condition(condition_id, data)
        return await self.serialize_condition(result)

    async def delete_condition(self, pk: int) -> bool:
        return await self.repository.delete_condition(pk)

    @staticmethod
    async def serialize_condition(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = ConditionSerializer(result, many=True)
        else:
            serializer = ConditionSerializer(result)
        return serializer.data
