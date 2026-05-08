from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.shortcuts import get_object_or_404
            
from .models import FriendShip
from .serializers import FriendShipSerializer



class FriendShipList(generics.ListCreateAPIView):
    serializer_class = FriendShipSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['to_user__username']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            sent = FriendShip.objects.filter(from_user=user).select_related('from_user', 'to_user')
            recieved = FriendShip.objects.filter(to_user=user).select_related('from_user', 'to_user')
            return sent | recieved
        return FriendShip.objects.none()
        
    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)