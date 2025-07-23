from django.db.models import (Model, CASCADE, SET_NULL, Index,
                              TextField, DateTimeField, BooleanField, CharField, IntegerField, FloatField,
                              ForeignKey, ManyToManyField)


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
        on_delete=CASCADE,  # удаление устройств при удалении всей компании
        related_name='subsystems'  # system.subsystems.all()
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


class User(Model):
    name = CharField(max_length=255)

    read = BooleanField(default=True)

    edit = BooleanField(default=False)

    admin = BooleanField(default=False)

    created_at = DateTimeField(auto_now_add=True)

    updated_at = DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            # Ускорение авторизации/поиска по имени
            Index(fields=['name']),

            # Быстрая фильтрация по уровню доступа
            Index(fields=['admin', 'edit']),
        ]


class Attachment(Model):
    name = CharField(max_length=255)

    created_at = DateTimeField(auto_now_add=True)

    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='attachments'
    )

    class Meta:
        indexes = [
            # Поиск вложений по автору
            Index(fields=['author']),

            # Сортировка по дате создания
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
        related_name='region_loas'
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
            # Поиск мест по LOA
            Index(fields=['loa']),

            # Ускорение JOIN-запросов
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
            # Фильтрация объектов по LOA
            Index(fields=['loa']),

            # Поиск по типу объекта
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
            # Для быстрого поиска событий по времени
            Index(fields=['begin']),

            # Для фильтрации по LOA + категории
            Index(fields=['loa', 'category']),

            # Для выборки по месту события
            Index(fields=['location']),

            # Для отчетов по временным диапазонам
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
            # Фильтрация мер по событию
            Index(fields=['event']),

            # Аналитика по времени принятия мер
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
        blank=True  # необязательно будут
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
        null=True  # статус будет просто не определен
    )

    description = TextField()

    class Meta:
        indexes = [
            # Частый поиск по связанному объекту
            Index(fields=['object']),

            Index(fields=['event']),

            # Фильтрация по статусу подсистемы
            Index(fields=['subsystem_status']),

            # Комбинированный индекс для аналитики
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
