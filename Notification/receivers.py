from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from Notification.models import Notifications
from User_Relationship.signals import get_new_followers, get_new_comments

@receiver(get_new_followers)
def followers_notification(user):
    channel_layer = get_channel_layer()
    details = {
        'user':user,
        'detail':f'{user} has followed you'
    }

    notification = Notifications.objects.create(**details)

    message ={
        "id" : notification.id,
        "name" : user.first_name + " " + user.last_name,
        "profile_picture" : user.profile_picture,
        "detail" : notification.detail,
        "read" : notification.read,
        "timestamp" : str(notification.timestamp)
    }
    async_to_sync(channel_layer.group_send)(
        'follower_notifications', 
        {
         'type': 'new_notification', 
         'notification': message
        }
    )
    
    count_notifs = Notifications.objects.filter(read=False).count()

    async_to_sync(channel_layer.group_send)(
        'count_notifications',
        {
            'type' : 'notification_count',
            'unread_count' : count_notifs
        }
    )


# @receiver(get_new_comments)
# def new_comments_notificat