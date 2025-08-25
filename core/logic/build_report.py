import os

import xlsxwriter
from django.db.models import Prefetch

from core.models import (
    Event, EquipmentFailure, AdverseWeather, FireDanger, GeologicalDanger,
    HydrologicalDanger, EmergencySituation, OtherDanger, MeasuresTaken
)


async def generate_report_data(event_ids: list[int]) -> tuple[dict, int]:
    """
    Функция для генерации структурированных данных отчета на основе списка ID событий.
    События группируются по категориям, нумеруются и форматируются в список словарей.

    :param event_ids: Список ID событий для обработки.
    :return: Словарь с ключами - названиями категорий, значениями - списками словарей с данными событий.
    """
    if not event_ids:
        return {}, 0

    events = Event.objects.filter(id__in=event_ids).select_related(
        'loa', 'category', 'location', 'created_by'
    ).prefetch_related(
        Prefetch('event_measures', queryset=MeasuresTaken.objects.order_by('adopted_at')),
        'event_attachments'
    )

    grouped_data = {
        'EquipmentFailure': list(),
        'AdverseWeather': list(),
        'FireDanger': list(),
        'GeologicalDanger': list(),
        'HydrologicalDanger': list(),
        'EmergencySituation': list(),
        'OtherDanger': list()
    }

    async for event in events:
        category_table = event.category.table_name.lower() if event.category else None

        if category_table == 'equipment_failure':
            zero_dict = {'№ п/п': len(grouped_data['EquipmentFailure']) + 1}
            zero_dict.update(await _collect_common_data(event))

            failure = await EquipmentFailure.objects.select_related(
                'object', 'subsystem', 'subsystem_status'
            ).prefetch_related('influenced_objects').aget(event=event)
            zero_dict.update(await _collect_equipment_failure_data(failure))

            grouped_data['EquipmentFailure'].append(zero_dict)

        elif category_table == 'adverse_weather':
            zero_dict = {'№ п/п': len(grouped_data['AdverseWeather']) + 1}
            zero_dict.update(await _collect_common_data(event))

            weather = await AdverseWeather.objects.select_related('source', 'condition', 'precipitation').aget(
                event=event)
            zero_dict.update(await _collect_weather_danger_data(weather, event))

            grouped_data['AdverseWeather'].append(zero_dict)

        elif category_table == 'fire_danger':
            zero_dict = {'№ п/п': len(grouped_data['FireDanger']) + 1}
            zero_dict.update(await _collect_common_data(event))

            fire = await FireDanger.objects.select_related('source').aget(event=event)
            zero_dict.update(await _collect_fire_danger_data(fire, event))

            grouped_data['FireDanger'].append(zero_dict)

        elif category_table == 'geological_danger':
            zero_dict = {'№ п/п': len(grouped_data['GeologicalDanger']) + 1}
            zero_dict.update(await _collect_common_data(event))

            geo = await GeologicalDanger.objects.select_related('source').aget(event=event)
            zero_dict.update(await _collect_geological_danger_data(geo, event))

            grouped_data['GeologicalDanger'].append(zero_dict)

        elif category_table == 'hydrological_danger':
            zero_dict = {'№ п/п': len(grouped_data['HydrologicalDanger']) + 1}
            zero_dict.update(await _collect_common_data(event))

            hydro = await HydrologicalDanger.objects.select_related('source').aget(event=event)
            zero_dict.update(await _collect_hydrological_danger_data(hydro, event))

            grouped_data['HydrologicalDanger'].append(zero_dict)

        elif category_table == 'emergency_situation':
            zero_dict = {'№ п/п': len(grouped_data['EmergencySituation']) + 1}
            zero_dict.update(await _collect_common_data(event))

            emergency = await EmergencySituation.objects.select_related('source').aget(event=event)
            zero_dict.update(await _collect_emergency_situation_data(emergency, event))

            grouped_data['EmergencySituation'].append(zero_dict)

        elif category_table == 'other_danger':
            zero_dict = {'№ п/п': len(grouped_data['OtherDanger']) + 1}
            zero_dict.update(await _collect_common_data(event))

            other = await OtherDanger.objects.select_related('source').aget(event=event)
            zero_dict.update(await _collect_other_danger_data(other, event))
            grouped_data['OtherDanger'].append(zero_dict)

    max_range_columns = 0
    for category, items in grouped_data.items():
        max_range_columns = len(items[0].items()) if items[0] and max_range_columns < len(
            items[0].items()) else max_range_columns

    return grouped_data, max_range_columns


async def _collect_common_data(event: Event) -> dict:
    """Собирает общие данные из модели Event."""
    measures = '\n\n'.join([
        f"{m.adopted_at.strftime('%d.%m.%Y %H:%M:%S')}: {m.description}"
        async for m in event.event_measures.all()]) or ''

    attachments = '\n'.join([a.name async for a in event.event_attachments.all()]) or ''

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


async def _collect_equipment_failure_data(failure: EquipmentFailure) -> dict:
    """Собирает данные для EquipmentFailure в формате отчета об отказах."""
    influenced = ', '.join([o.name async for o in failure.influenced_objects.all()]) or ''

    return {
        'Наименование отказа': f"{failure.subsystem.name}",
        'Место возникновения/ Наименование объекта': (
            f"{failure.object.name} (влияние на: {influenced})" if influenced else failure.object.name
        ),
        'Описание события': f"{failure.subsystem_info}\n{failure.description}",
        'Статус подсистемы': failure.subsystem_status.name if failure.subsystem_status else '',
        'Резервный источник питания': 'Укажите, если применимо',  # Если есть специфическое поле, добавить
    }


async def _collect_weather_danger_data(weather: AdverseWeather, event: Event) -> dict:
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


async def _collect_fire_danger_data(fire: FireDanger, event: Event) -> dict:
    """Собирает данные для FireDanger."""
    return {
        'Вид информации, источник получения': fire.source.name if fire.source else '',
        'Объект МГ Общества, вблизи которого возникла ЧС': event.location.name if event.location else '',
        'Территория воздействия': f"Площадь: {fire.area}, направление: {fire.direction}",
        'Метеоусловия, температура, ветер, осадки': 'Пожарная опасность',
        'Описание события': fire.description,
    }


async def _collect_geological_danger_data(geo: GeologicalDanger, event: Event) -> dict:
    """Собирает данные для GeologicalDanger."""
    return {
        'Вид информации, источник получения': geo.source.name if geo.source else '',
        'Объект МГ Общества, вблизи которого возникла ЧС': event.location.name if event.location else '',
        'Территория воздействия': f"{geo.geography}, эпицентр: {geo.epicenter}",
        'Метеоусловия, температура, ветер, осадки': f"Геологическая опасность, магнитуда: {geo.magnitude}",
        'Описание события': geo.description,
    }


async def _collect_hydrological_danger_data(hydro: HydrologicalDanger, event: Event) -> dict:
    """Собирает данные для HydrologicalDanger."""
    return {
        'Вид информации, источник получения': hydro.source.name if hydro.source else '',
        'Объект МГ Общества, вблизи которого возникла ЧС': event.location.name if event.location else '',
        'Территория воздействия': hydro.water_name,
        'Метеоусловия, температура, ветер, осадки': f"Гидрологическая опасность, высота: {hydro.height}",
        'Описание события': hydro.description,
    }


async def _collect_emergency_situation_data(emergency: EmergencySituation, event: Event) -> dict:
    """Собирает данные для EmergencySituation."""
    return {
        'Вид информации, источник получения': emergency.source.name if emergency.source else '',
        'Объект МГ Общества, вблизи которого возникла ЧС': event.location.name if event.location else '',
        'Территория воздействия': emergency.geography,
        'Метеоусловия, температура, ветер, осадки': 'Чрезвычайная ситуация',
        'Описание события': emergency.description,
    }


async def _collect_other_danger_data(other: OtherDanger, event: Event) -> dict:
    """Собирает данные для OtherDanger."""
    return {
        'Вид информации, источник получения': other.source.name if other.source else '',
        'Объект МГ Общества, вблизи которого возникла ЧС': event.location.name if event.location else '',
        'Территория воздействия': 'N/A',
        'Метеоусловия, температура, ветер, осадки': 'Другая опасность',
        'Описание события': other.description,
    }


async def make_report(event_ids: list[int], label: str | None) -> bool:
    data, max_range_size = await generate_report_data(event_ids)
    file_path = os.path.join('core', 'attachments', 'report.xlsx')
    workbook = xlsxwriter.Workbook(file_path)

    title_format = workbook.add_format(
        {
            'bold': True,
            'align': 'center',
            'valign': 'top',
            'font_size': 12,
            'font_name': 'Arial',
            'text_wrap': True
        }
    )

    category_format = workbook.add_format(
        {
            'bold': True,
            'align': 'center',
            'valign': 'bottom',
            'font_size': 14,
            'font_name': 'Arial',
            'text_wrap': True
        }
    )

    header_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#00AEEF',
        'border': 1,
        'text_wrap': True,
        'font_size': 10,
        'font_name': 'Arial',
    })

    cell_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top',
        'border': 1,
        'font_size': 10,
        'font_name': 'Arial',
    })

    worksheet = workbook.add_worksheet()
    worksheet.hide_gridlines()
    row = 0

    if label:
        worksheet.merge_range(row, 0, row, 0 + max_range_size, label, title_format)
        row += 2

    for category, records in data.items():
        col = 0
        worksheet.merge_range(row, col, row, col + max_range_size, category, category_format)
        row += 1
        if not records:
            continue

        headers = list(records[0].keys())
        for header in headers:
            worksheet.write(row, col, header, header_format)
            col += 1
        worksheet.set_column(0, len(headers) - 1, 20)

        row += 1

        for record in records:
            col = 0
            for header in headers:
                value = record.get(header, '')
                if isinstance(value, (int, float)):
                    worksheet.write_number(row, col, value, cell_format)
                else:
                    worksheet.write(row, col, value, cell_format)
                col += 1
            row += 1
        row += 1

    workbook.close()
    return True
