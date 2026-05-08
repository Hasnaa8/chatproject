from django.urls import path
from .views import FriendShipList
urlpatterns = [
       path('friends/', FriendShipList.as_view(), name='friendship_list'),
]