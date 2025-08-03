from asgiref.sync import sync_to_async
from rest_framework.response import Response
from core.models import CustomUser
from core.views.user import UserSerializer

class UserRepository:
    @staticmethod
    async def create_user(data: dict) -> CustomUser:
        return await CustomUser.objects.create_user(**data)

    @staticmethod
    async def get_user(pk: int | None) -> CustomUser:
        if pk is None:
            return await sync_to_async(CustomUser.objects.all)()
        return await CustomUser.objects.aget(id=pk)

    @staticmethod
    async def update_user(data: dict) -> CustomUser | None:
        updated = await CustomUser.objects.filter(id=data['id']).aupdate(**data)
        if not updated:
            return None
        return await CustomUser.objects.aget(id=data['id'])

    @staticmethod
    async def delete_user(pk: int) -> bool:
        result = await CustomUser.objects.filter(id=pk).adelete()
        return bool(result)

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: dict) -> Response:
        result = await self.repository.create_user(data)
        return await self.serialize_user(result)

    async def get_user(self, pk: int | None) -> Response:
        result = await self.repository.get_user(pk)
        return await self.serialize_user(result)

    async def update_user(self, data: dict) -> Response:
        if 'id' not in data:
            raise ValueError("Can't update without ID key.")
        result = await self.repository.update_user(data)
        return await self.serialize_user(result)

    async def delete_user(self, pk: int) -> bool:
        return await self.repository.delete_user(pk)

    @staticmethod
    async def serialize_user(result) -> Response:
        async def _serialize():
            if isinstance(result, list):
                serializer = UserSerializer(result, many=True)
            else:
                serializer = UserSerializer(result)
            return serializer.data
        data = await _serialize()
        return Response(data)