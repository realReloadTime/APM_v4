from rest_framework import serializers
from core.models import CustomUser, SubsystemStatus, System, Subsystem, Condition, Precipitation, Source, Attachment, \
    Category, LocationType, Region, LOA, Location, ObjectType, Object, Event, MeasuresTaken, EquipmentFailure


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


class LOASerializer(serializers.ModelSerializer):
    region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        source='region',
        write_only=True
    )
    region = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = LOA
        fields = ['id', 'name', 'region_id', 'region']


class LocationSerializer(serializers.ModelSerializer):
    location_type_id = serializers.PrimaryKeyRelatedField(
        queryset=LocationType.objects.all(),
        source='location_type',
        write_only=True
    )

    loa_id = serializers.PrimaryKeyRelatedField(
        queryset=LOA.objects.all(),
        source='loa',
        write_only=True
    )

    location_type = serializers.StringRelatedField(read_only=True)
    loa = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Location
        fields = ['id', 'name', 'location_type', 'location_type_id', 'loa', 'loa_id']


class ObjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectType
        fields = '__all__'


class ObjectSerializer(serializers.ModelSerializer):
    object_type_id = serializers.PrimaryKeyRelatedField(
        queryset=ObjectType.objects.all(),
        source='object_type',
        write_only=True
    )

    loa_id = serializers.PrimaryKeyRelatedField(
        queryset=LOA.objects.all(),
        source='loa',
        write_only=True
    )

    object_type = serializers.StringRelatedField(read_only=True)
    loa = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Object
        fields = ['id', 'name', 'object_type', 'object_type_id', 'loa', 'loa_id']


class MeasuresTakenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasuresTaken
        field = '__all__'


class EventSerializer(serializers.ModelSerializer):
    loa_id = serializers.PrimaryKeyRelatedField(
        queryset=LOA.objects.all(),
        source='loa',
        write_only=True
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='location',
        write_only=True
    )
    measures_id = serializers.PrimaryKeyRelatedField(
        queryset=MeasuresTaken.objects.all(),
        source='measures',
        write_only=True,
        many=True,
        required=False
    )
    attachments_id = serializers.PrimaryKeyRelatedField(
        queryset=Attachment.objects.all(),
        source='attachments',
        write_only=True,
        many=True,
        required=False
    )
    created_by_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='created_by',
        write_only=True
    )

    loa = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    location = serializers.StringRelatedField(read_only=True)
    measures = serializers.StringRelatedField(read_only=True, many=True)
    attachments = serializers.StringRelatedField(read_only=True, many=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'begin', 'loa', 'loa_id', 'category', 'category_id', 'location', 'location_id', 'consequences',
                  'measures', 'measures_id', 'personnel_count', 'technic_count', 'organization_name', 'note',
                  'attachments', 'attachments_id', 'created_by', 'created_by_id', 'end']
        read_only_fields = ['id', 'begin', 'loa', 'category', 'location', 'measures', 'attachments', 'created_by',
                            'end']


class EquipmentFailureSerializer(serializers.ModelSerializer):
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(),
        source='event',
        write_only=True
    )
    object_id = serializers.PrimaryKeyRelatedField(
        queryset=Object.objects.all(),
        source='object',
        write_only=True
    )
    influenced_objects_id = serializers.PrimaryKeyRelatedField(
        queryset=Object.objects.all(),
        source='influenced_objects',
        write_only=True,
        many=True,
        required=False
    )
    subsystem_id = serializers.PrimaryKeyRelatedField(
        queryset=Subsystem.objects.all(),
        source='subsystem',
        write_only=True
    )
    subsystem_status_id = serializers.PrimaryKeyRelatedField(
        queryset=SubsystemStatus.objects.all(),
        source='subsystem_status',
        write_only=True
    )

    event = serializers.StringRelatedField(read_only=True)
    object = serializers.StringRelatedField(read_only=True)
    influenced_objects = serializers.StringRelatedField(read_only=True, many=True)
    subsystem = serializers.StringRelatedField(read_only=True)
    subsystem_status = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EquipmentFailure
        fields = ['id', 'event', 'event_id', 'object', 'object_id', 'influenced_objects', 'influenced_objects_id',
                  'additional_info', 'subsystem', 'subsystem_id', 'subsystem_status', 'subsystem_status_id',
                  'description']
        read_only_fields = ['id', 'event', 'object', 'influenced_objects', 'subsystem', 'subsystem_status']