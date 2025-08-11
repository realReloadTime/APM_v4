from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Object
from core.serializers import ObjectSerializer
from core.logic.object_type import ObjectTypeRepository
from core.logic.loa import LOARepository


class ObjectRepository:
    @staticmethod
    async def create_object(data: dict) -> Object:
        name = data.get('name')
        object_type_id = data.get('object_type_id')
        loa_id = data.get('loa_id')

        if not name:
            raise ValueError("name обязательное поле для создания Object")

        if object_type_id:
            object_type = await ObjectTypeRepository.get_object_type(object_type_id)
            data['object_type'] = object_type
        else:
            raise ValueError("object_type_id обязательное поле для создания Object")

        if loa_id:
            loa = await LOARepository.get_loa(loa_id)
            data['loa'] = loa
        else:
            raise ValueError("loa_id обязательное поле для создания Object")

        data.pop('object_type_id', None)
        data.pop('loa_id', None)

        return await Object.objects.acreate(**data)

    @staticmethod
    async def get_object(pk: int | None, filters: dict | None = None) -> Object | list[Object]:
        if pk is None:
            if filters:
                return [objecT async for objecT in
                    Object.objects.select_related('object_type').select_related('loa').all().filter(**filters)]
            else:
                return [objecT async for objecT in
                        Object.objects.select_related('object_type').select_related('loa').all()]
        try:
            return await Object.objects.select_related('object_type').select_related('loa').aget(id=pk)
        except Object.DoesNotExist:
            raise ValueError(f"Object с ID {pk} не существует")

    @staticmethod
    async def update_object(pk: int, data: dict) -> Object | None:
        object_type_id = data.get('object_type_id')
        loa_id = data.get('loa_id')

        if object_type_id:
            object_type = await ObjectTypeRepository.get_object_type(object_type_id)
            data['object_type'] = object_type
        data.pop('object_type_id', None)

        if loa_id:
            loa = await LOARepository.get_loa(loa_id)
            data['loa'] = loa
        data.pop('loa_id', None)

        updated = await Object.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await Object.objects.select_related('object_type').select_related('loa').aget(id=pk)

    @staticmethod
    async def delete_object(pk: int) -> bool:
        result = await Object.objects.filter(id=pk).adelete()
        return bool(result)


class ObjectService:
    def __init__(self, repository: ObjectRepository):
        self.repository = repository

    async def create_object(self, data: dict) -> ReturnDict:
        result = await self.repository.create_object(data)
        return await self.serialize_object(result)

    async def get_object(
            self, pk: int | None = None,
            filters: dict | None = None,
    ) -> ReturnDict:
        result = await self.repository.get_object(pk, filters)
        return await self.serialize_object(result)

    async def update_object(self, object_id: int, data: dict) -> ReturnDict:
        if object_id is None or object_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_object(object_id, data)
        if result is None:
            raise ValueError("Object not found")
        return await self.serialize_object(result)

    async def delete_object(self, pk: int) -> bool:
        return await self.repository.delete_object(pk)

    @staticmethod
    async def serialize_object(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = ObjectSerializer(result, many=True)
        else:
            serializer = ObjectSerializer(result)
        return serializer.data
