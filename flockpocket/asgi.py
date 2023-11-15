"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flockpocket.settings")
django.setup()
from django.core.asgi import get_asgi_application
from django.conf import settings
from django.urls import path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from api.consumers import FlockConsumer

from common import config as cfg
from common import logger as log

# initialize the config
cfg.init_config()

# initialize the logger
log.init("daphne.log", sync=False)

#http_application = AuthMiddlewareStack(get_asgi_application())
http_application = get_asgi_application()
ws_application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                path('ws/api/', FlockConsumer.as_asgi()),
            ]
        )
    )
})

async def application(scope, receive, send):
    await cfg.init()
    if scope["type"] == "http":
        await http_application(scope, receive, send)
    elif scope["type"] == "websocket":
        await ws_application(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")
