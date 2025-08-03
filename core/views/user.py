from rest_framework import status
from rest_framework.response import Response
from core.drfutil.async_apiview import AsyncAPIView
from core.drfutil.auth import AsyncAuthentication, AsyncIsAuthenticated
from core.models import CustomUser, Token
from rest_framework.serializers import Serializer, EmailField, CharField
import uuid
from drf_spectacular.utils import extend_schema, OpenApiParameter
from core.logic.user import UserService, UserRepository
from asgiref.sync import sync_to_async

class RegisterSerializer(Serializer):
    email = EmailField()
    password = CharField(write_only=True)
    first_name = CharField(max_length=30, allow_blank=True)
    last_name = CharField(max_length=30, allow_blank=True)

class UserSerializer(Serializer):
    id = CharField(read_only=True)
    email = EmailField()
    first_name = CharField(max_length=30, allow_blank=True)
    last_name = CharField(max_length=30, allow_blank=True)
    is_active = CharField(read_only=True)
    is_staff = CharField(read_only=True)

class RegisterView(AsyncAPIView):
    @extend_schema(
        summary="Register a new user",
        description="Creates a new user and returns a token.",
        responses={201: UserSerializer}
    )
    async def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                user = await CustomUser.objects.create_user(
                    email=data['email'],
                    password=data['password'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                )
                token = await Token.objects.acreate(key=str(uuid.uuid4()), user=user)
                return Response({
                    'token': token.key,
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(AsyncAPIView):
    @extend_schema(
        summary="Login a user",
        description="Authenticates a user and returns a token.",
        responses={200: UserSerializer}
    )
    async def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = await CustomUser.objects.aget(email=email)
            if await sync_to_async(user.check_password)(password):
                token, _ = await Token.objects.aget_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user': UserSerializer(user).data
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserCRUD(AsyncAPIView):
    authentication_classes = [AsyncAuthentication]
    permission_classes = [AsyncIsAuthenticated]
    serializer_class = UserSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserService(UserRepository())

    @extend_schema(
        summary="Retrieve user",
        description="Fetches a single user by ID or all users if no ID is provided.",
        parameters=[OpenApiParameter(name='pk', type=int, location='path', required=False, description='User ID')],
        responses={200: UserSerializer, 404: None}
    )
    async def get(self, request, pk=None):
        try:
            response = await self.service.get_user(pk)
            return Response(response.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Create user",
        description="Creates a new user.",
        responses={201: UserSerializer}
    )
    async def post(self, request):
        try:
            response = await self.service.create_user(request.data)
            return Response(response.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update user",
        description="Updates an existing user.",
        parameters=[OpenApiParameter(name='pk', type=int, location='path', required=True, description='User ID')],
        responses={200: UserSerializer, 404: None}
    )
    async def put(self, request, pk):
        try:
            data = request.data.copy()
            data['id'] = pk
            response = await self.service.update_user(data)
            if response is None:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response(response.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete user",
        description="Deletes a user.",
        parameters=[OpenApiParameter(name='pk', type=int, location='path', required=True, description='User ID')],
        responses={204: None, 404: None}
    )
    async def delete(self, request, pk):
        try:
            success = await self.service.delete_user(pk)
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)