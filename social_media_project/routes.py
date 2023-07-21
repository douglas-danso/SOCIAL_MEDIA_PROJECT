from django.urls import path
from Notification import consumers
from Chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path("notifications/", consumers.UserNotificationConsumer.as_asgi()),

    path("chats/<conversation_name>/", ChatConsumer.as_asgi()),
]