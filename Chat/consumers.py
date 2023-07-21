from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from Authentication.models import CustomUser
from asgiref.sync import async_to_sync
from .models import Conversation,Messages

class ChatConsumer(AsyncJsonWebsocketConsumer): 
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    def connect(self,*args, **kwargs):
        self.user_id = self.scope["auth_user"]["user_id"]
        self.conversation_name = f"{self.scope['url_route']['kwargs']['conversation_name']}"
        self.user = CustomUser.objects.get(id=self.user_id)
        self.accept()
        self.conversation, created = Conversation.objects.get_or_create(name=self.conversation_name)

        async_to_sync(self.channel_layer.group_add)(
            self.conversation_name,
            self.channel_name,
        )

        # Send a welcome message to the user
        self.conversation.online.add(self.user)
        self.send_json(
            {
                "type": "welcome_message",
                "message": "Hey there! You've successfully connected!",
            }
        )

        # self.send_json(
        #     {
        #         "type" : "doctor_user_status",
        #         "status" : self.get_receiver().is_online
                
        #     }
        # )

        messages = Messages.objects.filter(conversation = self.conversation.id).order_by("-timestamp").values("content", "sender__email", "receiver__email", "timestamp")[:50]
        serialized_messages = []
        for message in reversed(messages):
            serialized_messages.append({
                "content": message["content"],
                "from_user": message["from_user__email"],
                "to_user": message["to_user__email"],
                "timestamp": str(message["timestamp"])
            })
        self.send_json({
            "type": "last_50_messages",
            "messages": serialized_messages
        })

        messages_to_me = self.conversation.messages.filter(receiver=self.user)
        messages_to_me.update(read=True)

        # Send the unread count to the doctor
        unread_count = Messages.objects.filter(receiver=self.user, read=False).count()
        async_to_sync(self.channel_layer.group_send)(
            str(self.user.id) + "__notifications",
            {
                "type": "unread_count",
                "unread_count": unread_count,
            },
        )
    def disconnect(self, code):
        print("Disconnected!")
        self.conversation.online.remove(self.user)
        self.send_json(
            {
                "type": "user_status",
                "user" : self.user.email,
                "status": self.user.is_online,
                "message" : self.user.first_name + " " + self.user.last_name + " is disconnected"
            }
        )
        return super().disconnect(code)
    def receive_json(self, content, **kwargs):
        message_type = content["type"]

        if message_type == "typing":
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    "type": "typing",
                    "user": self.user.first_name,
                    "typing": content["typing"],
                },
            )

        #if message type is chat_message a message objected is created
        if message_type == "chat_message":
            message = Messages.objects.create(
                sender=self.user,
                receiverr=self.get_receiver(),
                content=content["message"],
                conversation=self.conversation
            )
            #the message is echoed in the conversation
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    "type": "chat_message_echo",
                    "name" : self.sender_id,
                    "message":{
                            "content" : message.content,
                            "sender" : self.user.email,
                            "receiver" : message.sender.email,
                            "timestamp" : str(message.timestamp),
                    },
                },
            )
            
    def chat_message_echo(self, event):
        self.send_json(event)

    def new_message_notification(self, event):
        self.send_json(event)
    def typing(self, event):
        self.send_json(event)        
    
    def get_receiver(self):
        ids = self.conversation_name.split("__")
        for id in ids:
            if int(id) != self.user.id:
                # This is the receiver
                return CustomUser.objects.get(id=id)