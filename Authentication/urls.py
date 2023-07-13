from django.urls import path,include
from .views import (Login,SignUp,UserLists,PasswordResetView,PasswordResetConfirm,
                          PasswordChange,DeleteAccount,Activate,ResendActivationLink,LogoutView,FacebookLogin, GoogleLogin, google_auth_test)
urlpatterns = [
    path('signup', SignUp.as_view(), name = 'signup'),
    path('login', Login.as_view(), name = 'login'),
    path('userlists/', UserLists.as_view(), name= 'lists'),
    path('passwordreset/', PasswordResetView.as_view(), name= 'passwordreset'),
    path('passwordresetconfirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name= 'passwordresetconfirm'),
    path('passwordchange/', PasswordChange.as_view(), name= 'passwordchange'),
    path('delete/', DeleteAccount.as_view(), name= 'delete'),
    path('activate/<token>/', Activate.as_view(), name= 'activate'),
    path('resend/', ResendActivationLink.as_view(), name= 'resend'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dj-rest-auth/facebook/', FacebookLogin.as_view(), name='fb_login'),
    path('dj-rest-auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('google/test/', google_auth_test, name='google_auth_test'),
    # path('google/login/callback/', GoogleCallback.as_view(), name='google_callback'),
]
