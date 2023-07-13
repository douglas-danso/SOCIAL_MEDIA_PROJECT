from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer,PasswordResetSerializer,PasswordResetConfirmSerializer,PasswordChangeSerializer,DeleteAccountSerializer,ResendSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from helpers.permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CustomUser
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.http import Http404,JsonResponse
from rest_framework.exceptions import NotFound
import jwt
from helpers.send_emails import send_activation_email
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import authenticate, login,logout
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import UserSerializer
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.views import OAuth2View, OAuth2LoginView, OAuth2CallbackView
from dj_rest_auth.registration.views import SocialLoginView
from django.shortcuts import redirect
from rest_framework.decorators import api_view

class SignUp(APIView):
    def post(self,request,*args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    def post(self,request,*args, **kwargs):
        email= request.data.get('email')
        password = request.data.get('password')

        try:
            user = CustomUser.objects.get(email= email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.check_password(password):
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class ResendActivationLink(generics.GenericAPIView):
    permission_classes = ()
    serializer_class = ResendSerializer
    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = CustomUser.objects.get(email=serializer.validated_data['email'])
        except (CustomUser.DoesNotExist):
            return Response('detail: user does not exist')
        if user.is_active == True and user.is_verified== True:
            return Response('detail: user is already verified')
        else:
            send_activation_email(request, user)
            return Response('detail: activation email sent')

class Activate(APIView):
    permission_classes = ()
    def post(self, request, token):
        try:
            decoded_token = jwt.decode(token, 'secret_key', algorithms=['HS256'])
            user_id = decoded_token['user_id']
            user = CustomUser.objects.get(id=user_id)
        except (jwt.exceptions.DecodeError, CustomUser.DoesNotExist):
            raise Http404('Invalid activation link')
        
        if not user.is_verified:
            user.is_verified = True
            user.is_active = True
            user.save()
            return JsonResponse({'detail': 'User has been activated'})
        else:
            return JsonResponse({'detail': 'User has already been activated'})


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]
    def post(self, request, format=None,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(email=serializer.validated_data['email'])
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(
                 reverse('passwordresetconfirm', kwargs={'uidb64': uidb64, 'token': token}))
            # Send the reset URL to the user by email
        subject = 'Password reset'
        message = f'Use this link to reset your password: {reset_url}'
        from_email = 'douglasdanso66@gmail.com'
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        # Return a success message
        return Response({'success': 'Password reset email has been sent'}, status=status.HTTP_200_OK)
    
class PasswordResetConfirm(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                user = None
       
        if user is not None and default_token_generator.check_token(user, token):
            
            if  user.check_password(password):
                return Response({'detail':'password cannot be the same as previous password.'})
            user.set_password(password)
            user.save()
            return Response({'detail': 'Password has been reset.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordChange(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_password = serializer.validated_data['current_password']
        user = self.request.user
        
        if not user.check_password(current_password):
            raise NotFound("You have entered the wrong password, try again.")
        
        password = serializer.validated_data['password']
        user.set_password(password)
        user.save()
        return Response({'detail': 'Password has been changed.'}, status=status.HTTP_200_OK)

class DeleteAccount(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    # lookup_field ='pk'
    permission_classes = [IsAdminUser]
    serializer_class = DeleteAccountSerializer 
    def delete(self,request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(email=serializer.validated_data['email'])
        user.is_active = False
        user.delete()

class UserLists(generics.ListAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

class LogoutView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(request):
        refresh_token = request.data.get('refresh_token')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    

class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/auth/facebook/login/callback/"
    client_class = OAuth2Client

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/auth/google/login/callback/"
    client_class = OAuth2Client

@api_view(['GET'])
def google_auth_test(request):
    adapter = GoogleOAuth2Adapter
    redirect_url = request.build_absolute_uri('/auth/google/login/callback/')
    authorization_url = OAuth2View.authorization_url(request, adapter, redirect_url)
    return redirect(authorization_url)


# class GoogleLogin(OAuth2LoginView):
#     adapter_class = GoogleOAuth2Adapter
#     callback_url = "http://127.0.0.1:8000/auth/google/login/callback/"
#     client_class = OAuth2Client


# class GoogleCallback(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
#     callback_url = "http://127.0.0.1:8000/auth/google/login/callback/"
#     client_class = OAuth2Client

#     def callback(self, request, sociallogin):
#         # Obtain the access token, authorization code, and ID token
#         access_token = sociallogin.token.token  # Access Token
#         code = request.GET.get('code')  # Authorization Code
#         id_token = sociallogin.token.token_secret  # ID Token

#         # Use the obtained tokens as needed

#         return self.login()


    
