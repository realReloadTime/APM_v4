from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework_simplejwt.utils import aware_utcnow

from core.models import CustomUser
from core.serializers import UserSerializer


class UserRepository:
    @staticmethod
    async def create_user(data: dict) -> CustomUser:
        return await CustomUser.objects.create_user(**data)

    @staticmethod
    async def get_user(pk: int | None = None) -> CustomUser | list[CustomUser] | None:
        if pk is None:
            return [user async for user in CustomUser.objects.all()]
        return await CustomUser.objects.aget(id=pk)

    @staticmethod
    async def update_user(pk: int, data: dict) -> CustomUser | None:
        updated = await CustomUser.objects.filter(id=pk).aupdate(**data)
        if not updated:
            return None
        return await CustomUser.objects.aget(id=pk)

    @staticmethod
    async def delete_user(pk: int) -> bool:
        result = await CustomUser.objects.filter(id=pk).adelete()
        return bool(result)


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: dict):
        result = await self.repository.create_user(data)
        return await self.serialize_user(result)

    async def get_me_as_user(self, user: CustomUser):
        return await self.serialize_user(user)

    async def get_user(self, pk: int | None = None):
        result = await self.repository.get_user(pk)
        return await self.serialize_user(result)

    async def update_user(self, user_id: int, data: dict):
        if user_id is None or user_id < 1:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_user(user_id, data)
        return await self.serialize_user(result)


    async def delete_user(self, pk: int) -> bool:
        return await self.repository.delete_user(pk)

    @staticmethod
    async def serialize_user(result) -> ReturnDict:
        if isinstance(result, list):
            serializer = UserSerializer(result, many=True)
        else:
            serializer = UserSerializer(result)
        return serializer.data
