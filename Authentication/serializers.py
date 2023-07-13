from rest_framework import serializers
from .models import CustomUser
from helpers.send_emails import send_activation_email
from helpers.validator import CustomPasswordValidator

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username','phone_number', 'full_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, password):
        validator = CustomPasswordValidator()
        validator.validate(password)
        return password

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email')
        user = CustomUser.objects.create_user(password=password, **validated_data)
        # send_activation_email(request=self.context.get('request'), user=user)
        return user
    

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, data):
        # Check if the email is associated with a registered user
        user = CustomUser.objects.filter(email=data).first()
        if not user:
            raise serializers.ValidationError("No account is associated with this email.")
        return data
    
class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("password","confirm_password")
    # password = serializers.CharField(
    #     write_only=True,
    #     required=True,
    #     # validators=[CustomPasswordValidator()]
    # )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True
    )

    def validate_password(self, password):
        validator = CustomPasswordValidator()
        validator.validate(password)
        return password
    
    def validate(self, data):
        
        password = data['password']
        
        # if user.check_password(password):
        #     raise serializers.ValidationError('New password cannot be the same as the old password.')
        
        """
        Check that the two password fields match
        """
        if password != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
class PasswordChangeSerializer(PasswordResetConfirmSerializer):
    current_password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta(PasswordResetConfirmSerializer.Meta):
        fields = ('current_password', 'password', 'confirm_password')
    def password_check(self,data):
        user = self.context['request'].user
        current_password = data['current_password']
        if not user.check_password(current_password):
            raise serializers.ValidationError('you have entered the wrong password check and try again.')
        
class DeleteAccountSerializer(PasswordResetSerializer):
    def get_user(self,email):
        user = CustomUser.objects.get(email=email)
        return user

class ResendSerializer(PasswordResetSerializer):
    pass