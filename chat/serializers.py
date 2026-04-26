from rest_framework import serializers
from .models import Message, Conversation

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    by_me = serializers.SerializerMethodField()
    
    def get_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_username', 'content', 'timestamp', 'is_received', 'is_read', 'by_me']