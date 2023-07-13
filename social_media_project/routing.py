from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from .routes import websocket_urlpatterns
from django.core.asgi import get_asgi_application
from .channelsmiddleware import JWTAuthMiddleware

application = ProtocolTypeRouter({
    # ...
    "http": get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(JWTAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        )
    )),
})