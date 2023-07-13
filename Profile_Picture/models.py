from django.db import models
from Authentication.models import CustomUser

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.CharField(max_length=250,blank=True, null=True)
    
    def __str__(self):
        return self.user.email