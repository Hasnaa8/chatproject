from django.urls import path
from .views import ProfileDetail, ProfileList, register_user, user_login, user_logout, change_password, verify_otp

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('change_password/', change_password, name='change_password'),
    path('verify_otp/', verify_otp, name='verify_otp'),

    path('profiles/', ProfileList.as_view(), name='profile_list'),

    # Path: /api/profiles/5/ (where 5 is the CustomUser's ID)
    # Action: GET (Retrieve), PUT/PATCH (Update), DELETE (Delete Account)
    path('profiles/<str:username>/', ProfileDetail.as_view(), name='profile_detail'),
]