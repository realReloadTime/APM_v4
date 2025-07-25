"""
ASGI config for apm_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apm_project.settings')
django.setup()

from channels.routing import ProtocolTypeRouter
from core.middleware import AsyncAuthMiddleware

application = ProtocolTypeRouter({
    "http":
        AsyncAuthMiddleware(get_asgi_application())
    ,
})