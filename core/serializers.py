from rest_framework import serializers
from core.models import CustomUser, SubsystemStatus, System, Subsystem


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'name']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data.get('name', '')
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'name', 'is_active', 'is_staff', 'read', 'edit']


class SubsystemStatusSerializer(serializers.ModelSerializer):  # ExampleSerializer(example) -> JSON response
    class Meta:
        model = SubsystemStatus
        fields = '__all__'


class SystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = System
        fields = '__all__'


class SubsystemSerializer(serializers.ModelSerializer):
    system_id = serializers.PrimaryKeyRelatedField(
        queryset=System.objects.all(),
        source='system',
        write_only=True
    )
    system = serializers.StringRelatedField(read_only=True)  # Для вывода имени системы

    class Meta:
        model = Subsystem
        fields = ['id', 'name', 'system_id', 'system']