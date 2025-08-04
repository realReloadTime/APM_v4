# <b><i>Инструкция по запуску проекта </i></b>
<i>Инструкция подразумевает, что вы уже клонировали репозиторий c GitHub и перешли в директорию проекта</i>

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
<code>python manage.py loadallfixtures</code>
<br><br>
<i>При возникновении ошибок во время переноса (например, не найден ключ элемента таблицы, используемый в другой таблице) <b>перезапустить скрипт</b>.</i>

### Запуск проекта
<code>uvicorn apm_project.asgi:application --reload --port 8000</code>
