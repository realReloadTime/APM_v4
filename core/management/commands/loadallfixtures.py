# your_app/management/commands/loadallfixtures.py
import os
import sys
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Load all project fixtures excluding venv and installed packages'

    def handle(self, *args, **options):
        # Определяем пути для исключения
        exclude_paths = [
            os.path.normpath('venv'),
            os.path.normpath('.venv'),
            os.path.normpath('.env'),
            os.path.normpath('env'),
            os.path.join(settings.BASE_DIR, 'venv'),
            os.path.join(settings.BASE_DIR, '.venv'),
        ]

        # Добавляем пути из виртуального окружения Python
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            exclude_paths.append(sys.prefix)

        fixtures = []
        for root, dirs, files in os.walk(settings.BASE_DIR):
            # Пропускаем исключенные директории
            if any(ex_path in os.path.normpath(root) for ex_path in exclude_paths):
                self.stdout.write(f'Skipping excluded dir: {root}')
                continue

            if 'fixtures' in root.split(os.sep):
                for file in files:
                    if file.endswith('.json'):
                        full_path = os.path.join(root, file)
                        # Форматируем путь для Django
                        rel_path = os.path.relpath(full_path, settings.BASE_DIR)
                        django_fixture_path = rel_path.replace('\\', '/')
                        fixtures.append(django_fixture_path)

        # Загружаем только фикстуры из наших приложений
        valid_fixtures = []
        for fixture in fixtures:
            # Фильтруем фикстуры установленных пакетов
            if 'site-packages' in fixture or 'dist-packages' in fixture:
                continue
            valid_fixtures.append(fixture)
            self.stdout.write(f'Found fixture: {fixture}')

        # Загружаем все валидные фикстуры
        for fixture in valid_fixtures:
            try:
                self.stdout.write(f'Loading {fixture}...')
                call_command('loaddata', fixture)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error loading {fixture}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('✅ All project fixtures loaded!'))