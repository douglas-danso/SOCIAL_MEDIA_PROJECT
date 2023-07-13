from rest_framework import serializers
from Authentication.models import CustomUser
from Profile_Picture.models import Profile
import cloudinary.uploader
import cloudinary
from django.conf import settings

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id',)  

class ProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    image = serializers.ImageField(write_only=False)  # Add this line
    
    class Meta:
        model = Profile
        fields = ('user', 'image')

    def update(self, instance, validated_data):
        image = validated_data.get('image')
        if image:
            print('yo')
            cloudinary_response = cloudinary.uploader.upload(image)
            instance.image = cloudinary_response['secure_url']

            print('helllllo')
            instance.save()
            return instance
