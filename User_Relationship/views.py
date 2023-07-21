from .models import UserRelationship
from Authentication.models import CustomUser
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Posts,Comments,Likes
from django.db.models import Q
from rest_framework.response import Response
from .signals import get_new_followers,get_new_comments,like_a_post,like_a_comment
from helpers.utils import RecommendationAlgorithm


class Follow(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        followed_id = request.data.get('followed_id')

        user_to_follow = get_object_or_404(CustomUser, id=followed_id)
        if user_to_follow == user:
            return Response({'detail': 'You cannot follow yourself'}, status=400)

        UserRelationship.objects.create(follower=user, followed=user_to_follow)
        # cache.delete(cache_key)
        get_new_followers.send(sender=self.__class__, sender_user=user, receiver=user_to_follow)
        return Response({'detail': f'You have followed {user_to_follow.email}'}, status=200)


    
    
class Unfollow(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def post(self,request,*args, **kwargs):
        user = self.request.user
        user_id = request.data.get('user_id')
        try:
            user_to_unfollow = CustomUser.objects.get(id=user_id)
            if user_to_unfollow == user:
                return JsonResponse({'detail': 'you cannot unfollow yourself'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'detail':'user does not exist'})
        
        UserRelationship.objects.filter(follower=user, followed=user_to_unfollow).delete()
        return JsonResponse({'detail': f'You have unfollowed {user_to_unfollow.email}'})
    
class GetFollowers(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self,request,*args, **kwargs):
        user = request.user
        followers = UserRelationship.objects.filter(followed=user).values()
        print(followers)
        count = followers.count()
        return JsonResponse({'detail':list(followers), 'count':count})
    
class GetFollowing(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def get(self,request,*args, **kwargs):
        user = self.request.user
        print('here')
        following = UserRelationship.objects.filter(follower=user).values()
        count = following.count()
        return JsonResponse({'detail':list(following), 'count':count})
    
class MakePosts(APIView):
    def post(self,request, *args, **kwargs):
        user = request.user
        post = request.data.get('post')
        details = {
            'user_id':user.id,
            'post':post
        }
        Posts.objects.create(**details)
        return JsonResponse({'detail':'post created successfully'})
    
class MakeComments(APIView):
    def post(self,request,*args, **kwargs):
        user = request.user
        post_id = request.data.get('post_id')
        comment = request.data.get('comments')
        post = get_object_or_404(Posts, id= post_id)
        details = {
            'user_id':user.id,
            'post_id':post_id,
            'comment':comment
        }
        Comments.objects.create(**details)
        get_new_comments.send(sender=self.__class__, sender_user=user, post=post)
        return JsonResponse({'detail':'comment created successfully'})
    
class ReactToAPost(APIView):
    def post(self,request,*args, **kwargs):
        user = request.user
        post_id = request.data.get('post_id')
        post = get_object_or_404(Posts, id= post_id)
        Likes.objects.create(user_id = user.id, post_id=post_id)
        like_a_post.send(sender=self.__class__, sender_user=user, post=post)
        return JsonResponse({'detail':'reaction created successfully'})
    
class ReactToAComment(APIView):
    def post(self,request,*args, **kwargs):
        user = request.user
        comment_id = request.data.get('comment_id')
        comment = get_object_or_404(Comments, id= comment_id)
        Likes.objects.create(user_id = user.id, comment_id=comment_id)
        like_a_comment.send(sender=self.__class__, sender_user=user, comment=comment)
        return JsonResponse({'detail':'reaction created successfully'})
class Unlike(APIView):
    def delete(self,request):
        user = request.user
        post_id = request.data.get('post_id')
        comment_id = request.data.get('comment_id')
        if post_id:
            likes = Likes.objects.get(user_id = user.id, post_id=post_id)
            likes.delete()
        elif comment_id:
            likes = Likes.objects.get(user_id = user.id, comment_id=comment_id)
            likes.delete()
        return JsonResponse({'detail': 'unlike done successfully'})
    
        
    
class GetTotalPostLikes(APIView):
    def get(self,request,*args, **kwargs):
        post_id = request.data.get('post_id')
        post = get_object_or_404(Posts, id= post_id)
        likes = Likes.objects.filter(post_id = post_id).values()
        count =likes.count()
        return JsonResponse({'detail':list(likes),'count':count})
    

class GetTotalCommentLikes(APIView):
    def get(self,request,*args, **kwargs):
        comment_id = request.data.get('comment_id')
        comment = get_object_or_404(Comments, id= comment_id)
        likes = Likes.objects.filter(comment_id = comment_id).values()
        count = likes.count()
        return JsonResponse({'detail':list(likes),'count':count})  
    


class Timeline(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        followed_users_ids = UserRelationship.objects.filter(follower=user_id).values_list('followed_id', flat=True)
        timeline_posts = Posts.objects.filter(Q(user=user_id) | Q(user__in=followed_users_ids)).prefetch_related('comments', 'likes').values_list
        timeline_posts = timeline_posts.order_by('-created_at')

        recommendation_algorithm = RecommendationAlgorithm()
        recommended_posts = recommendation_algorithm.get_content_based_filtered_posts(timeline_posts, k=5)

        timeline_posts |= recommended_posts


        return JsonResponse({'detail': list(timeline_posts)})