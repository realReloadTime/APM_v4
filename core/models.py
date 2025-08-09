from django.db.models import (Model, CASCADE, SET_NULL, Index, TextField, DateTimeField,
                              BooleanField, CharField, IntegerField, FloatField,
                              ForeignKey, ManyToManyField, OneToOneField, EmailField)
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = EmailField(unique=True)
    name = CharField(max_length=255, blank=True)

    is_active = BooleanField(default=True)  # поля для доступа к админке (обязательные для PermissionsMixin)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    read = BooleanField(default=True)
    edit = BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm: str, obj=None):
        if self.is_superuser:  # Если пользователь админ, даём все права
            return True
        if perm.endswith('_read') and self.read:
            return True
        if perm.endswith('_edit') and self.edit:
            return True
        return False


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


class Category(Model):
    name = CharField(max_length=255)
    table_name = CharField(max_length=255)

    def __str__(self):
        return self.name


class LocationType(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class Region(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class LOA(Model):
    name = CharField(max_length=255)
    region = ForeignKey(
        Region,
        on_delete=CASCADE,
        related_name='region_loas',
        null=True
    )

    def __str__(self):
        return self.name


class Location(Model):
    location_type = ForeignKey(
        LocationType,
        on_delete=CASCADE
    )
    name = CharField(max_length=255, blank=False)
    loa = ForeignKey(
        LOA,
        on_delete=CASCADE,
        related_name='loa_locations'
    )

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            Index(fields=['loa']),
            Index(fields=['location_type']),
            Index(fields=['name']),
        ]


class ObjectType(Model):
    name = CharField(max_length=255)

    def __str__(self):
        return self.name


class Object(Model):
    object_type = ForeignKey(
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

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            Index(fields=['loa']),
            Index(fields=['object_type']),
            Index(fields=['name']),
        ]


class Event(Model):
    begin = DateTimeField(auto_now_add=True, editable=False)
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
    organization_name = CharField(max_length=255, blank=True)
    note = TextField(blank=True)
    end = DateTimeField(blank=True, null=True)

    created_by = ForeignKey(
        CustomUser,
        on_delete=CASCADE,
        related_name='created_events',
        null=True
    )

    def __str__(self):
        return str(self.begin)

    class Meta:
        indexes = [
            Index(fields=['begin']),
            Index(fields=['loa', 'category']),
            Index(fields=['location']),
            Index(fields=['end']),
        ]


class Attachment(Model):
    event = ForeignKey(
        Event,
        on_delete=CASCADE,
        related_name='event_attachments',
        blank=True,
        null=True
    )
    name = CharField(max_length=255, unique=True)
    created_at = DateTimeField(auto_now_add=True)
    author = ForeignKey(
        'CustomUser',
        on_delete=CASCADE,
        related_name='attachments'
    )

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            Index(fields=['author']),
            Index(fields=['-created_at']),
        ]


class MeasuresTaken(Model):
    event = ForeignKey(   # many Measure : 1 Event
        Event,
        on_delete=CASCADE,
        related_name='event_measures',
        blank=True,
        null=True
    )
    adopted_at = DateTimeField()
    description = TextField()

    class Meta:
        indexes = [
            Index(fields=['adopted_at']),
        ]

    def __str__(self):
        return str(self.adopted_at)


class EquipmentFailure(Model):
    event = OneToOneField(
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
    event = OneToOneField(
        Event,
        on_delete=CASCADE
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
    temperature = FloatField(null=True, blank=True)
    wind = FloatField(null=True, blank=True)
    description = TextField(null=True, blank=True)

    class Meta:
        indexes = [
            Index(fields=['event']),
            Index(fields=['source']),
        ]


class FireDanger(Model):
    event = OneToOneField(
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
    event = OneToOneField(
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
    event = OneToOneField(
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
    event = OneToOneField(
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
    event = OneToOneField(
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
