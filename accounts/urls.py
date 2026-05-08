from django.urls import path
from .views import ProfileDetail, ProfileList, register_user, user_login, user_logout, change_password, verify_otp, ContactList, ContactDetail

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('change_password/', change_password, name='change_password'),
    path('verify_otp/', verify_otp, name='verify_otp'),

    path('profiles/', ProfileList.as_view(), name='profile_list'),
    path('profiles/<str:username>/', ProfileDetail.as_view(), name='profile_detail'),

    path('contacts/', ContactList.as_view(), name='contact_list'),
    path('contacts/<str:username>/', ContactDetail.as_view(), name='contact_detail'),   
]