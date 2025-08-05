from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Category
from core.serializers import CategorySerializer


class CategoryRepository:
    @staticmethod
    async def create_category(data: dict) -> Category:
        return await Category.objects.acreate(**data)

    @staticmethod
    async def get_category(pk: int | None) -> Category | list[Category]:
        if pk is None:
            return [category async for category in Category.objects.all()]
        try:
            return await Category.objects.aget(id=pk)
        except Category.DoesNotExist:
            raise ValueError(f"Category с ID {pk} не существует")

    @staticmethod
    async def update_category(pk: int, data: dict) -> Category | None:
        updated = await Category.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await Category.objects.aget(id=pk)

    @staticmethod
    async def delete_category(pk: int) -> bool:
        result = await Category.objects.filter(id=pk).adelete()
        return bool(result)


class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    async def create_category(self, data: dict) -> ReturnDict:
        result = await self.repository.create_category(data)
        return await self.serialize_category(result)

    async def get_category(self, pk: int | None = None) -> ReturnDict:
        result = await self.repository.get_category(pk)
        return await self.serialize_category(result)

    async def update_category(self, category_id: int, data: dict) -> ReturnDict:
        if category_id is None or category_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_category(category_id, data)
        return await self.serialize_category(result)

    async def delete_category(self, pk: int) -> bool:
        return await self.repository.delete_category(pk)

    @staticmethod
    async def serialize_category(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = CategorySerializer(result, many=True)
        else:
            serializer = CategorySerializer(result)
        return serializer.data
