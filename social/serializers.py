from rest_framework import serializers

from accounts.models import CustomUser
from .models import FriendShip

class FriendShipSerializer(serializers.ModelSerializer):
    to_user = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(),
        slug_field='username'
    )
    
    from_user_username = serializers.CharField(source='from_user.username', read_only=True)
    to_user_username = serializers.CharField(source='to_user.username', read_only=True)

    by_me = serializers.SerializerMethodField()
    
    def get_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return "Sent" if obj.from_user == request.user else "Received"
        return None

    def validate(self, data):
        request = self.context.get('request')
        from_user = request.user
        to_user = data.get('to_user')

        if from_user == to_user:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")
        
        
        friendship1 = FriendShip.objects.filter(from_user=from_user, to_user=to_user)
        friendship2 = FriendShip.objects.filter(from_user=to_user, to_user=from_user)
        friendship = (friendship1 | friendship2).first()
        
        if friendship:
            if friendship.status == "accepted":
                raise serializers.ValidationError("You are already friends.")
            elif friendship.status == "rejected":
                # friendship.delete()
                pass
            elif friendship.status == "pending":
                if friendship.from_user == from_user:
                    raise serializers.ValidationError("Friend request already sent.")
                else:
                    raise serializers.ValidationError("You have a pending friend request from this user.")

        return data
    
    class Meta:
        model = FriendShip
        fields = ['id', 'from_user', 'from_user_username', 'to_user', 'to_user_username', 'status', 'created_at', 'by_me']
        read_only_fields = ['created_at', 'from_user']