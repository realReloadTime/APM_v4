# <b><i>Инструкция по запуску проекта </i></b>

## Для Windows:

### Установить Postgresql
https://www.postgresql.org/download/windows/

#### После установки создать БД для данных, вписать название, пользователя и пароль в settings.py переменной DATABASES

### Создать и активировать виртуальное окружение в проекте
<code>python -m venv venv</code>
<br><br>
<code>.\venv\Scripts\activate</code>

### Установить зависимости
<code> pip install -r requirements.txt </code>

### Мигрировать с помощью manage.py
#### Применение миграций:
<code>python manage.py migrate</code>
<br><br>
#### Опционально - создать суперпользователя:
<code>python manage.py createsuperuser</code>
<br><br>
#### Собрать статику:
<code>python manage.py collectstatic</code>
<br><br>
#### Загрузить данные из фикстур:
<code>python manage.py loaddata systems subsystems subsystem_statuses sources regions precipitations conditions objecttypes locationtypes categories loas</code>

### Запуск проекта
<code>uvicorn apm_project.asgi:application --reload --port 8000</code>
