from django.db import models
from Authentication.models import CustomUser


class Conversation(models.Model):
    name = models.CharField(max_length=128)
    online = models.ManyToManyField(to=CustomUser, blank=True, related_name='online')

    def get_online_count(self):
        return self.online.count()
    
    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()
        
    def __str__(self):
        return f"{self.name} ({self.get_online_count()})"

class Messages(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='sender')
    receiver = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='receiver')
    message = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now=True)
    
    
        
    
