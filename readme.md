# <b><i>Инструкция по запуску проекта </i></b>
<i>Инструкция подразумевает, что вы уже клонировали репозиторий c GitHub и перешли в директорию проекта</i>

## Для Windows:

### Установить Postgresql
https://www.postgresql.org/download/windows/

#### После установки создать БД для данных.
БД можно создать через терминал и psql, либо с помощью UI pgAdmin.

### Добавить .env в /apm_project
Определить переменные окружения:<br><br>
<code>DJANGO_SECRET_KEY='любая-строка'<br>
DB_NAME='название_базы_данных'<br>
DB_USER='название_пользователя_базы_данных'<br>
DB_PASSWORD='пароль-базы_данных'
</code>

### Создать и активировать виртуальное окружение в проекте
<code>python -m venv venv</code>
<br>
<code>.\venv\Scripts\activate</code>

### Установить зависимости
<code> pip install -r requirements.txt </code>

### Мигрировать с помощью manage.py
#### Применение миграций:
<code>python manage.py migrate</code>

#### Опционально - создать суперпользователя:
<code>python manage.py createsuperuser</code>

[//]: # (#### Собрать статику:)

[//]: # (<code>python manage.py collectstatic</code>)

#### Загрузить данные из фикстур:
<code>python manage.py loadallfixtures</code>
<br><br>
<i>При возникновении ошибок во время переноса (например, не найден ключ элемента таблицы, используемый в другой таблице) <b>перезапустить скрипт</b>.</i>

### Запуск проекта
<code>uvicorn apm_project.asgi:application --reload --port 8000</code>

Параметры:
* <i><code>--reload</code> опционален, автоматически перезапускает проект при изменении кода<br>
* <code>--port</code> опционален, имеет значение по-умолчанию 8000</i>