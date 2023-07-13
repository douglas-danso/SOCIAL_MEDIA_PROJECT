from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from Authentication.models import CustomUser
from Profile_Picture.models import Profile
from .serializers import ProfileSerializer
import cloudinary
import cloudinary.uploader
from django.conf import settings
from django.http import JsonResponse

class ProfileImageView(generics.GenericAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)
        image_file= request.FILES.get('image_file')
        if image_file:
           try:
            cloudinary_response = cloudinary.uploader.upload(image_file)
            image = cloudinary_response['secure_url']
            profile.image = image
            profile.save()
           
           except cloudinary.exceptions.Error as e:
                return Response({'detail': 'Invalid image file'}, status=status.HTTP_400_BAD_REQUEST) 
        else:
                profile.image ='NULL'
                profile.save()
        context  ={"id" : user.id,
                 "image": profile.image
            }
        return JsonResponse({'profile': context, 'detail' :'success'})
                
               


        