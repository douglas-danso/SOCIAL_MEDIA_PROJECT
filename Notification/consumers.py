from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from Authentication.models import CustomUser
from Notification.models import Notifications

class CountConsumer(JsonWebsocketConsumer):
    authentication_classes = (JWTAuthentication,)
    permission_classes = IsAuthenticated
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None

    def connect(self):
        self.user_id = self.scope["auth_user"]["user_id"]
        self.user = CustomUser.objects.get(id=self.user_id)
        self.accept()

        self.notification_group_name = "count_notifications"
        async_to_sync(self.channel_layer.group_add)(
            self.notification_group_name,
            self.channel_name,
        )

        number_of_notifs = Notifications.objects.filter(read=False).count()
        

        self.send_json(
            {
                "type": "notification_count",
                "unread_count": number_of_notifs,
            }
        )
        

    def disconnect(self, code):

        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name,
            self.channel_name,
        )
        return super().disconnect(code)
    
    def number_of_notifs(self,event):
        self.send_json(event)

    def notification_count(self,event):
        self.send_json(event)


class FollowersNotification(JsonWebsocketConsumer):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    def connect(self):
        self.user_id = self.scope["auth_user"]["user_id"]
        self.user = CustomUser.objects.get(id=self.user_id)
        self.accept()

        self.notification_group_name = 'follower_notifications'
        async_to_sync(self.channel_layer.group_add)(
            self.notification_group_name,
            self.channel_name
        )

    def disconnect(self,code):
        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name,
            self.channel_name
        )
        return super().disconnect(code)