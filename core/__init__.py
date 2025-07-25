# Здесь будут команды, помогающие запустить проект / настроить БД

# python manage.py loaddata systems subsystems subsystem_statuses sources regions precipitations conditions objecttypes locationtypes categories loas
# ДЛЯ ЛИНУКС # gunicorn apm_project.asgi:application -k uvicorn.workers.UvicornWorker
# ДЛЯ ТЕСТА API НА WINDOWS  # uvicorn apm_project.asgi:application
# ДЛЯ ДОКУМЕНТАЦИИ НА WINDOWS отключить в settings.py ASYNC: TRUE python manage.py runserver