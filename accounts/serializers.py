from rest_framework import serializers

from social.models import FriendShip
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
    
    is_own_profile = serializers.SerializerMethodField()
    def get_is_own_profile(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.pk == obj.user.pk
        return False
        
    is_contact = serializers.SerializerMethodField()
    def get_is_contact(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if user.pk == obj.user.pk:
                return False
            return user.contacts.filter(pk=obj.user.pk).exists()
        return False

    friend_status = serializers.SerializerMethodField()
    def get_friend_status(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if user.pk == obj.user.pk:
                return None
        
        from_user = user
        to_user = obj.user      
        friendship1 = FriendShip.objects.filter(from_user=from_user, to_user=to_user)
        friendship2 = FriendShip.objects.filter(from_user=to_user, to_user=from_user)
        friendship = (friendship1 | friendship2).first()
        
        if friendship:
            if friendship.status == "accepted":
                return "friends"
            elif friendship.status == "rejected":
                friendship.delete()
            elif friendship.status == "pending":
                if friendship.from_user == from_user:
                    return "friend_request_sent"
                else:
                    return "friend_request_received"
        else:
            return "not_friends"
        return None
            


    class Meta:
        model = Profile
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'bio', 'gender', 'profile_picture', 'phone_number', 
            'created', 'updated', 'is_completed', 'url', 'links', 'other_email',
            'is_contact', 'is_own_profile', 'friend_status'
        ]
        read_only_fields = ['username', 'email', 'created', 'updated', 'is_completed', 'is_contact', 'friend_status']


class OwnProfileSerializer(ProfileSerializer):
    contacts = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='username',
        source='user.contacts'
    )
    contacts_count = serializers.IntegerField(source='user.contacts.count', read_only=True)
    
    class Meta(ProfileSerializer.Meta):
        fields = ProfileSerializer.Meta.fields + ['contacts', 'contacts_count']
        read_only_fields = ProfileSerializer.Meta.read_only_fields + ['contacts_count']

class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class ContactSerializer(ProfileSerializer):
    class Meta(ProfileSerializer.Meta):
        fields = [
            'username', 'first_name', 'last_name', 
            'profile_picture', 'phone_number',
            'is_completed', 'is_contact'
        ]
        read_only_fields = ['username', 'profile_picture', 'phone_number']
        