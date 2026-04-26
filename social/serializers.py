from rest_framework import serializers
from .models import FriendShip

class FriendShipSerializer(serializers.ModelSerializer):
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
        
        if FriendShip.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("Friend request already sent.")
        
        if FriendShip.objects.filter(from_user=to_user, to_user=from_user).exists():
            raise serializers.ValidationError("You have a pending friend request from this user.")
        
        return data
    
    class Meta:
        model = FriendShip
        fields = ['id', 'from_user', 'from_user_username', 'to_user', 'to_user_username', 'status', 'created_at', 'by_me']
        read_only_fields = ['created_at']