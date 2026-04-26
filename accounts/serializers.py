from rest_framework import serializers
from .models import CustomUser, Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'is_verified']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['is_verified']
    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            is_verified=False
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = Profile
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'bio', 'gender', 'profile_picture', 'phone_number', 
            'created', 'updated', 'is_completed', 'url', 'links', 'other_email'
        ]
        # user__id is read-only because it's set during registration
        read_only_fields = ['username', 'email', 'created', 'updated', 'is_completed']

class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)