from collections import defaultdict
from django.db.models import Prefetch
from core.models import (
    Event, EquipmentFailure, AdverseWeather, FireDanger, GeologicalDanger,
    HydrologicalDanger, EmergencySituation, OtherDanger, MeasuresTaken
)


def generate_report_data(event_ids: list[int]) -> dict:
    """
    Функция для генерации структурированных данных отчета на основе списка ID событий.
    События группируются по категориям, нумеруются и форматируются в список словарей с полями на русском языке.

    :param event_ids: Список ID событий для обработки.
    :return: Словарь с ключами - названиями категорий, значениями - списками словарей с данными событий.
    """
    if not event_ids:
        return {}

    # Получаем все события с предзагрузкой связанных данных
    events = Event.objects.filter(id__in=event_ids).select_related(
        'loa', 'category', 'location', 'created_by'
    ).prefetch_related(
        Prefetch('event_measures', queryset=MeasuresTaken.objects.order_by('adopted_at')),
        'event_attachments'
    )

    # Создаем словарь для группировки
    grouped_data = {
        'EquipmentFailure': list(),
        'AdverseWeather': list(),
        'FireDanger': list(),
        'GeologicalDanger': list(),
        'HydrologicalDanger': list(),
        'EmergencySituation': list(),
        'OtherDanger': list()
    }

    for event in events:
        category_table = event.category.table_name.lower() if event.category else None
        data = _collect_common_data(event)
        print(category_table)
        if category_table == 'equipment_failure':
            failure = EquipmentFailure.objects.select_related(
                'object', 'subsystem', 'subsystem_status'
            ).prefetch_related('influenced_objects').get(event=event)
            data.update(_collect_equipment_failure_data(failure, event))
            grouped_data['EquipmentFailure'].append(data)

        elif category_table == 'adverse_weather':
            weather = AdverseWeather.objects.select_related('source', 'condition', 'precipitation').get(event=event)
            data.update(_collect_weather_danger_data(weather, event))
            grouped_data['AdverseWeather'].append(data)

        elif category_table == 'fire_danger':
            fire = FireDanger.objects.select_related('source').get(event=event)
            data.update(_collect_fire_danger_data(fire, event))
            grouped_data['FireDanger'].append(data)

        elif category_table == 'geological_danger':
            geo = GeologicalDanger.objects.select_related('source').get(event=event)
            data.update(_collect_geological_danger_data(geo, event))
            grouped_data['GeologicalDanger'].append(data)

        elif category_table == 'hydrological_danger':
            hydro = HydrologicalDanger.objects.select_related('source').get(event=event)
            data.update(_collect_hydrological_danger_data(hydro, event))
            grouped_data['HydrologicalDanger'].append(data)

        elif category_table == 'emergency_situation':
            emergency = EmergencySituation.objects.select_related('source').get(event=event)
            data.update(_collect_emergency_situation_data(emergency, event))
            grouped_data['EmergencySituation'].append(data)

        elif category_table == 'other_danger':
            other = OtherDanger.objects.select_related('source').get(event=event)
            data.update(_collect_other_danger_data(other, event))
            grouped_data['OtherDanger'].append(data)

        print(grouped_data, data)

    # Нумеруем события в каждой группе
    for category, items in grouped_data.items():
        for idx, item in enumerate(items, start=1):
            item['№ п/п'] = idx
    return dict(grouped_data)


def _collect_common_data(event: Event) -> dict:
    """Собирает общие данные из модели Event."""
    measures = '\n'.join(
        f"{m.adopted_at.strftime('%d.%m.%Y %H:%M:%S')}: {m.description}"
        for m in event.event_measures.all()
    ) or ''

    attachments = '\n'.join(a.name for a in event.event_attachments.all()) or ''

    return {
        'Дата, время начала': event.begin.strftime('%d.%m.%Y %H:%M:%S') if event.begin else '',
        'Дата, время окончания': event.end.strftime('%d.%m.%Y %H:%M:%S') if event.end else '',
        'ЛПУ': event.loa.name if event.loa else '',
        'Место возникновения/ Наименование объекта': event.location.name if event.location else '',
        'Возможные последствия, степень угрозы': event.consequences,
        'Принятые меры': measures,
        'Примечание': f"{event.note}\nПриложения: {attachments}" if attachments else event.note,
        'ФИО диспетчера, дата/время внесения информации': (
            f"{event.created_by.name} {event.begin.strftime('%d.%m.%Y %H:%M:%S')}"
            if event.created_by else ''
        ),
        'Персонал': event.personnel_count,
        'Техника': event.technic_count,
        'Организация': event.organization_name,
    }


def _collect_equipment_failure_data(failure: EquipmentFailure, event: Event) -> dict:
    """Собирает данные для EquipmentFailure в формате отчета об отказах."""
    influenced = ', '.join(o.name for o in failure.influenced_objects.all()) or ''

    return {
        'Наименование отказа': f"{failure.subsystem.system.name if failure.subsystem.system else ''} - {failure.subsystem.name}",
        'Место возникновения/ Наименование объекта': (
            f"{failure.object.name} (влияние на: {influenced})" if influenced else failure.object.name
        ),
        'Описание события': f"{failure.subsystem_info}\n{failure.description}",
        'Статус подсистемы': failure.subsystem_status.name if failure.subsystem_status else '',
        'Резервный источник питания': 'Укажите, если применимо',  # Если есть специфическое поле, добавить
    }


def _collect_weather_danger_data(weather: AdverseWeather, event: Event) -> dict:
    """Собирает данные для AdverseWeather в формате отчета о погодных условиях."""
    return {
        'Вид информации, источник получения': weather.source.name if weather.source else '',
        'Объект МГ Общества, вблизи которого возникла ЧС': event.location.name if event.location else '',
        'Территория воздействия': weather.geography,
        'Метеоусловия, температура, ветер, осадки': (
            f"Метеоусловия: {weather.condition.name}, температура: {weather.temperature if weather.temperature is not None else 'N/A'}, "
            f"ветер: {weather.wind if weather.wind is not None else 'N/A'}, осадки: {weather.precipitation.name}"
        ),
        'Описание события': weather.description,
    }


def _collect_fire_danger_data(fire: FireDanger, event: Event) -> dict:
    """Собирает данные для FireDanger."""
    return {
        'Вид информации, источник получения': fire.source.name if fire.source else '',
        'Объект МГ Общества, вблизи которого возникла ЧС': event.location.name if event.location else '',
        'Территория воздействия': f"Площадь: {fire.area}, направление: {fire.direction}",
        'Метеоусловия, температура, ветер, осадки': 'Пожарная опасность',
        'Описание события': fire.description,
    }


def _collect_geological_danger_data(geo: GeologicalDanger, event: Event) -> dict:
    """Собирает данные для GeologicalDanger."""
    return {
        'Вид информации, источник получения': geo.source.name if geo.source else '',
        'Объект МГ Общества, вблизи которого возникла ЧС': event.location.name if event.location else '',
        'Территория воздействия': f"{geo.geography}, эпицентр: {geo.epicenter}",
        'Метеоусловия, температура, ветер, осадки': f"Геологическая опасность, магнитуда: {geo.magnitude}",
        'Описание события': geo.description,
    }


def _collect_hydrological_danger_data(hydro: HydrologicalDanger, event: Event) -> dict:
    """Собирает данные для HydrologicalDanger."""
    return {
        'Вид информации, источник получения': hydro.source.name if hydro.source else '',
        'Объект МГ Общества, вблизи которого возникла ЧС': event.location.name if event.location else '',
        'Территория воздействия': hydro.water_name,
        'Метеоусловия, температура, ветер, осадки': f"Гидрологическая опасность, высота: {hydro.height}",
        'Описание события': hydro.description,
    }


def _collect_emergency_situation_data(emergency: EmergencySituation, event: Event) -> dict:
    """Собирает данные для EmergencySituation."""
    return {
        'Вид информации, источник получения': emergency.source.name if emergency.source else '',
        'Объект МГ Общества, вблизи которого возникла ЧС': event.location.name if event.location else '',
        'Территория воздействия': emergency.geography,
        'Метеоусловия, температура, ветер, осадки': 'Чрезвычайная ситуация',
        'Описание события': emergency.description,
    }


def _collect_other_danger_data(other: OtherDanger, event: Event) -> dict:
    """Собирает данные для OtherDanger."""
    return {
        'Вид информации, источник получения': other.source.name if other.source else '',
        'Объект МГ Общества, вблизи которого возникла ЧС': event.location.name if event.location else '',
        'Территория воздействия': 'N/A',
        'Метеоусловия, температура, ветер, осадки': 'Другая опасность',
        'Описание события': other.description,
    }