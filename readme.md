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

### Установить Redis и запустить
https://github.com/tporadowski/redis/releases/download/v5.0.14.1/Redis-x64-5.0.14.1.msi

Если установка выполнена успешно, сервер Redis запустится автоматически.

Чтобы проверить статус Redis, необходимо через CMD перейти в директорию установленного Redis (C:\Program Files\Redis стандартно) и выполнить команду:
<code>redis-cli</code>. Если сервер работает, появится строка <code>127.0.0.1:6379></code>, которая говорит о том, что сервер отвечает на команды.

Если возникает ошибка подключения, сервер Redis можно запустить вручную, запустив файл redis-server.exe в той же директории, либо введя команду: <code>redis-server --service-start</code>


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

#### Собрать статику:

<code>python manage.py collectstatic</code>

<i>Обязательно вызывать эту команду при любом изменении CSS, JS файлов.</i>
#### Загрузить данные из фикстур:
<code>python manage.py loadallfixtures</code>
<br><br>
<i>При возникновении ошибок во время переноса (например, не найден ключ элемента таблицы, используемый в другой таблице) <b>перезапустить скрипт, пока не останется ошибок</b>. (в текущий момент с чистой БД 5-6 запусков)</i>

### Запуск проекта
<code>uvicorn apm_project.asgi:application --reload --port 8000</code>

Параметры:
* <i><code>--reload</code> опционален, автоматически перезапускает проект при изменении кода<br>
* <code>--port</code> опционален, имеет значение по-умолчанию 8000</i>


### Возможные проблемы

Если во время работы сервера Redis выдает ошибку: 
<blockquote>MISCONF Redis is configured to save RDB snapshots, but it is currently not able to persist on disk. Commands that may modify the data set are disabled, because this instance is configured to report errors during writes if RDB snapshotting fails (stop-writes-on-bgsave-error option). Please check the Redis logs for details about the RDB error.</blockquote>
Необходимо открыть CMD, перейти в директорию Redis (C:\Program Files\Redis стандартно) и ввести следующие команды:<br><br>
<code>redis-cli</code><br>
<code>config set stop-writes-on-bgsave-error no</code><br>
<code>FLUSHALL</code><br><br>
При правильном вводе в терминале должна появиться строка "ОК".