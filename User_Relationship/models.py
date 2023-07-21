from django.db import models
from Authentication.models import CustomUser

class UserRelationship(models.Model):
    follower = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='following_relationships')
    followed = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='follower_relationships')
    created_at = models.DateTimeField(auto_now_add=True)

class Posts(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='posts')
    post = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

class Comments(models.Model):
    comment_user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='comments' )
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE,null=True,blank=True,related_name='replies')
    comment = models.CharField(max_length=200)
    post = models.ForeignKey(Posts,on_delete=models.CASCADE,related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

class Likes(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Posts,on_delete=models.CASCADE,related_name='likes')
    comment = models.ForeignKey(Comments,on_delete=models.CASCADE,related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)


   