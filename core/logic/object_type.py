from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import ObjectType
from core.serializers import ObjectTypeSerializer


class ObjectTypeRepository:
    @staticmethod
    async def create_object_type(data: dict) -> ObjectType:
        return await ObjectType.objects.acreate(**data)

    @staticmethod
    async def get_object_type(pk: int | None) -> ObjectType | list[ObjectType]:
        if pk is None:
            return [object_type async for object_type in ObjectType.objects.all()]
        try:
            return await ObjectType.objects.aget(id=pk)
        except ObjectType.DoesNotExist:
            raise ValueError(f"ObjectType с ID {pk} не существует")

    @staticmethod
    async def update_object_type(pk: int, data: dict) -> ObjectType | None:
        updated = await ObjectType.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await ObjectType.objects.aget(id=pk)

    @staticmethod
    async def delete_object_type(pk: int) -> bool:
        result = await ObjectType.objects.filter(id=pk).adelete()
        return bool(result)


class ObjectTypeService:
    def __init__(self, repository: ObjectTypeRepository):
        self.repository = repository

    async def create_object_type(self, data: dict) -> ReturnDict:
        result = await self.repository.create_object_type(data)
        return await self.serialize_object_type(result)

    async def get_object_type(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_object_type(pk)
        return await self.serialize_object_type(result)

    async def update_object_type(self, object_type_id: int, data: dict) -> ReturnDict:
        if object_type_id is None or object_type_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_object_type(object_type_id, data)
        return await self.serialize_object_type(result)

    async def delete_object_type(self, pk: int) -> bool:
        return await self.repository.delete_object_type(pk)

    @staticmethod
    async def serialize_object_type(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = ObjectTypeSerializer(result, many=True)
        else:
            serializer = ObjectTypeSerializer(result)
        return serializer.data
