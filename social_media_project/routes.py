from django.urls import path
# from Chat.consumers import ChatConsumer, NotificationConsumer
from Notification import consumers

websocket_urlpatterns = [
    path("count_notifications/", consumers.CountConsumer.as_asgi()),
]