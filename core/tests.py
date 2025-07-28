import pytest
from django.contrib.auth import get_user_model
from core.drfutil.auth import AsyncAuthentication
from core.models import SubsystemStatus
from asgiref.sync import sync_to_async

User = get_user_model()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestSubsystemStatusCRUD:
    async def create_user_and_token(self):
        # Создаем пользователя асинхронно
        user = await sync_to_async(User.objects.create_user)(
            username="testuser",
            password="testpassword"
        )

        # Создаем токен через вашу асинхронную систему
        # Предполагая, что у вас есть модель Token в core.models
        from core.models import Token
        token = await sync_to_async(Token.objects.create)(user=user)

        return user, token.key

    async def get_authenticated_client(self):
        _, token = await self.create_user_and_token()

        # Создаем асинхронный клиент с авторизацией
        from django.test import AsyncClient
        client = AsyncClient()
        client.defaults["HTTP_AUTHORIZATION"] = f"Token {token}"
        return client

    async def test_create_and_retrieve(self):
        client = await self.get_authenticated_client()

        # Тест создания
        create_data = {"name": "Test Subsystem"}
        response = await client.post(
            "/api/subsystem_status/",
            data=create_data,
            content_type="application/json"
        )
        assert response.status_code == 201
        assert response.data["name"] == "Test Subsystem"
        created_id = response.data["id"]

        # Тест получения одного объекта
        response = await client.get(f"/api/subsystem_status/{created_id}/")
        assert response.status_code == 200
        assert response.data["name"] == "Test Subsystem"

        # Тест получения списка
        response = await client.get("/api/subsystem_status/")
        assert response.status_code == 200
        assert len(response.data) > 0
        assert any(item["name"] == "Test Subsystem" for item in response.data)

    async def test_update_and_delete(self):
        client = await self.get_authenticated_client()

        # Создаем объект для теста
        status = await sync_to_async(SubsystemStatus.objects.create)(name="Old Name")

        # Тест обновления
        update_data = {"name": "Updated Name"}
        response = await client.put(
            f"/api/subsystem_status/{status.id}/",
            data=update_data,
            content_type="application/json"
        )
        assert response.status_code == 200
        assert response.data["name"] == "Updated Name"

        # Тест удаления
        response = await client.delete(f"/api/subsystem_status/{status.id}/")
        assert response.status_code == 204

        # Проверяем что объект удален
        response = await client.get(f"/api/subsystem_status/{status.id}/")
        assert response.status_code == 404

    async def test_unauthenticated_access(self):
        # Проверка без авторизации
        from django.test import AsyncClient
        client = AsyncClient()

        response = await client.get("/api/subsystem_status/")
        assert response.status_code == 401  # Unauthorized

    async def test_invalid_token(self):
        from django.test import AsyncClient
        client = AsyncClient()
        client.defaults["HTTP_AUTHORIZATION"] = "Token invalidtoken123"

        response = await client.get("/api/subsystem_status/")
        assert response.status_code == 401