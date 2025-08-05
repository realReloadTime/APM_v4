from rest_framework import serializers
from core.models import CustomUser, SubsystemStatus, System, Subsystem, Condition, Precipitation, Source, Attachment, \
    Category, LocationType, Region


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


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = '__all__'


class PrecipitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precipitation
        fields = '__all__'


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'


class AttachmentSerializer(serializers.ModelSerializer):
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='author',
        write_only=True
    )
    author = serializers.StringRelatedField(read_only=True)
    file = serializers.FileField(write_only=True)  # поле для загрузки файла

    class Meta:
        model = Attachment
        fields = ['id', 'name', 'created_at', 'author_id', 'author', 'file']
        read_only_fields = ['name', 'created_at', 'author']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class LocationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationType
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'
