from django.urls import path
from .views import Follow,Unfollow,GetFollowers,GetFollowing,ReactToAComment,ReactToAPost,MakeComments,MakePosts,GetTotalCommentLikes,GetTotalPostLikes,Timeline
urlpatterns = [
    path('follow/', Follow.as_view(), name='follow'),
    path('unfollow/', Unfollow.as_view(), name='unfollow'),
    path('get-followers/', GetFollowers.as_view(), name='followers'),
    path('get-following/', GetFollowing.as_view(), name='following'),
    path('like-post/', ReactToAPost.as_view(), name='like-post'),
    path('like-comment/', ReactToAComment.as_view(), name='like-comment'),
    path('make-post/', MakePosts.as_view(), name='make-post'),
    path('make-comment/', MakeComments.as_view(), name='make-comment'),
    path('get-likes/post/', GetTotalPostLikes.as_view(), name='get-likes-posts'),
    path('get-likes/comment/', GetTotalCommentLikes.as_view(), name='get-likes-comments'),
    path('timeline/', Timeline.as_view(), name='timeline'),
]