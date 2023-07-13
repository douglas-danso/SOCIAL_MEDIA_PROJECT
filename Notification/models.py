from django.db import models
from Authentication.models import CustomUser


class Notifications(models.Model):
    user = models.ForeignKey( CustomUser, on_delete=models.CASCADE)
    detail = models.CharField("detail",max_length=250,blank=True,null=True )
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.detail