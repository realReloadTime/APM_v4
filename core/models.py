from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models import (Model, CASCADE, SET_NULL, Index, TextField, DateTimeField,
                              BooleanField, CharField, IntegerField, FloatField,
                              ForeignKey, ManyToManyField, EmailField)


class CustomUserManager(BaseUserManager):
    async def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        await user.asave(using=self._db)
        return user

    async def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return await self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = EmailField(unique=True)
    first_name = CharField(max_length=30, blank=True)
    last_name = CharField(max_length=30, blank=True)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Token(Model):
    key = CharField(max_length=40, primary_key=True)
    user = ForeignKey(
        'CustomUser',
        related_name='auth_tokens',
        on_delete=CASCADE
    )
    created = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.key


class SubsystemStatus(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class System(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class Subsystem(Model):
    name = CharField(max_length=255)
    system = ForeignKey(
        System,
        on_delete=CASCADE,
        related_name='subsystems'
    )

    def __str__(self):
        return self.name


class Condition(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class Precipitation(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class Source(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class Attachment(Model):
    name = CharField(max_length=255)
    created_at = DateTimeField(auto_now_add=True)
    author = ForeignKey(
        'CustomUser',
        on_delete=CASCADE,
        related_name='attachments'
    )

    class Meta:
        indexes = [
            Index(fields=['author']),
            Index(fields=['-created_at']),
        ]


class Category(Model):
    name = CharField(max_length=255)
    table_name = CharField(max_length=255)


class LocationType(Model):
    name = CharField(max_length=255)


class Region(Model):
    name = CharField(max_length=255)


class LOA(Model):
    name = CharField(max_length=255)
    region = ForeignKey(
        Region,
        on_delete=CASCADE,
        related_name='region_loas',
        null=True
    )


class Location(Model):
    location_type = ForeignKey(
        LocationType,
        on_delete=CASCADE
    )
    name = CharField(max_length=255)
    loa = ForeignKey(
        LOA,
        on_delete=CASCADE,
        related_name='loa_locations'
    )

    class Meta:
        indexes = [
            Index(fields=['loa']),
            Index(fields=['location_type']),
        ]


class ObjectType(Model):
    name = CharField(max_length=255)


class Object(Model):
    type = ForeignKey(
        ObjectType,
        on_delete=CASCADE,
        related_name='type_objects'
    )
    name = CharField(max_length=255)
    loa = ForeignKey(
        LOA,
        on_delete=CASCADE,
        related_name='loa_objects'
    )

    class Meta:
        indexes = [
            Index(fields=['loa']),
            Index(fields=['type']),
        ]


class Event(Model):
    begin = DateTimeField(auto_now_add=True)
    loa = ForeignKey(
        LOA,
        on_delete=CASCADE,
        related_name='loa_events'
    )
    category = ForeignKey(
        Category,
        on_delete=CASCADE,
        related_name='category_events'
    )
    location = ForeignKey(
        Location,
        on_delete=CASCADE,
        related_name='location_events'
    )
    consequences = TextField()
    personnel_count = IntegerField(default=0)
    technic_count = IntegerField(default=0)
    organization_name = CharField(max_length=255)
    note = TextField()
    end = DateTimeField()
    attachments = ManyToManyField(
        'Attachment',
        related_name='attached_for_events',
        blank=True
    )

    class Meta:
        indexes = [
            Index(fields=['begin']),
            Index(fields=['loa', 'category']),
            Index(fields=['location']),
            Index(fields=['end']),
        ]


class MeasuresTaken(Model):
    event = ForeignKey(
        Event,
        on_delete=CASCADE,
        related_name='event_measures'
    )
    adopted_at = DateTimeField()
    description = TextField()

    class Meta:
        indexes = [
            Index(fields=['event']),
            Index(fields=['adopted_at']),
        ]


class EquipmentFailure(Model):
    event = ForeignKey(
        Event,
        on_delete=CASCADE,
    )
    object = ForeignKey(
        Object,
        on_delete=CASCADE,
    )
    influenced_objects = ManyToManyField(
        'Object',
        related_name='influenced_by_failures',
        blank=True
    )
    additional_info = TextField()
    subsystem = ForeignKey(
        Subsystem,
        on_delete=CASCADE
    )
    subsystem_info = TextField()
    subsystem_status = ForeignKey(
        SubsystemStatus,
        on_delete=SET_NULL,
        null=True
    )
    description = TextField()

    class Meta:
        indexes = [
            Index(fields=['object']),
            Index(fields=['event']),
            Index(fields=['subsystem_status']),
            Index(fields=['subsystem', 'subsystem_status']),
        ]


class AdverseWeather(Model):
    event = ForeignKey(
        Event,
        on_delete=CASCADE,
    )
    source = ForeignKey(
        Source,
        on_delete=SET_NULL,
        null=True
    )
    geography = TextField()
    condition = ForeignKey(
        Condition,
        on_delete=CASCADE
    )
    precipitation = ForeignKey(
        Precipitation,
        on_delete=CASCADE
    )
    temperature = FloatField()
    wind = FloatField()
    description = TextField()

    class Meta:
        indexes = [
            Index(fields=['event']),
            Index(fields=['source']),
        ]


class FireDanger(Model):
    event = ForeignKey(
        Event,
        on_delete=CASCADE,
    )
    source = ForeignKey(
        Source,
        on_delete=SET_NULL,
        null=True
    )
    area = FloatField()
    direction = CharField(max_length=255)
    description = TextField()

    class Meta:
        indexes = [
            Index(fields=['event']),
            Index(fields=['source']),
        ]


class GeologicalDanger(Model):
    event = ForeignKey(
        Event,
        on_delete=CASCADE
    )
    source = ForeignKey(
        Source,
        on_delete=SET_NULL,
        null=True
    )
    geography = TextField()
    epicenter = TextField()
    magnitude = IntegerField()
    description = TextField()

    class Meta:
        indexes = [
            Index(fields=['event']),
            Index(fields=['source']),
        ]


class HydrologicalDanger(Model):
    event = ForeignKey(
        Event,
        on_delete=CASCADE
    )
    source = ForeignKey(
        Source,
        on_delete=SET_NULL,
        null=True
    )
    water_name = CharField(max_length=255)
    height = FloatField()
    description = TextField()

    class Meta:
        indexes = [
            Index(fields=['event']),
            Index(fields=['source']),
        ]


class EmergencySituation(Model):
    event = ForeignKey(
        Event,
        on_delete=CASCADE
    )
    source = ForeignKey(
        Source,
        on_delete=SET_NULL,
        null=True
    )
    geography = TextField()
    description = TextField()

    class Meta:
        indexes = [
            Index(fields=['event']),
            Index(fields=['source']),
        ]


class OtherDanger(Model):
    event = ForeignKey(
        Event,
        on_delete=CASCADE
    )
    source = ForeignKey(
        Source,
        on_delete=SET_NULL,
        null=True
    )
    description = TextField()

    class Meta:
        indexes = [
            Index(fields=['event']),
            Index(fields=['source']),
        ]
