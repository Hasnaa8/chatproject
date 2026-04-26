from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes, schema
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import update_session_auth_hash
from .tasks import send_welcome_email, send_otp_email
from .serializers import LoginRequestSerializer, UserSerializer, ProfileSerializer, ChangePasswordSerializer, VerifyOTPSerializer
from .models import CustomUser, EmailOTP, Profile
from .permissions import IsOwnerOrReadOnly
from rest_framework.exceptions import PermissionDenied
            
from drf_spectacular.openapi import AutoSchema, OpenApiTypes
from drf_spectacular.utils import extend_schema

# registering users
@extend_schema(
    request=UserSerializer,
    responses={201: UserSerializer},
    description="Register a new user. An OTP will be sent to the provided email for verification."
)
@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# login(users)
@extend_schema(
    request=LoginRequestSerializer, 
    responses={200: UserSerializer},
    description="Login to the application and obtain an authentication token."
)
@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
                username = user.username
            except ObjectDoesNotExist:
                pass

        if not user:
            user = authenticate(username=username, password=password)

        if user is not None:
            if not user.is_verified:
                    return Response({"error": "Account not verified. Check your email."}, status=403)
        
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'user':UserSerializer(user).data, 'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
# logout(users)
@extend_schema(
    request=None,
    responses={204: None},
    description="Logout user and delete token."
)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# change pass
@extend_schema(
    request=ChangePasswordSerializer,
    responses={200: OpenApiTypes.OBJECT},
    description="Change the password of the authenticated user. Requires old and new password."
)
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == 'POST':
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)  # To update session after password change
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema(
    request=VerifyOTPSerializer,
    responses={200: OpenApiTypes.OBJECT},
    description="Verify the OTP sent to the user's email for account verification."
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        try:
            user = CustomUser.objects.get(email=email)    
            otp_obj = EmailOTP.objects.get(user=user, otp=otp)
            
            if not otp_obj.is_valid():
                return Response({"error": "OTP expired"}, status=400)
            
            send_welcome_email.delay(email)
            
            user.is_verified = True
            user.save()
            otp_obj.delete() # Cleanup
            return Response({"message": "Verification successful!"})
            
        except (CustomUser.DoesNotExist, EmailOTP.DoesNotExist):
            return Response({"error": "Invalid email or OTP"}, status=400)
    return Response(serializer.errors, status=400)


# 1. LIST ONLY (No Create)
class ProfileList(generics.ListAPIView):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # Anyone can see, must log in to filter
    authentication_classes = [TokenAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['gender']
    search_fields = ['user__username', 'first_name', 'last_name', 'email', 'phone_number']

# 2. RETRIEVE, UPDATE, DELETE
class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    authentication_classes = [TokenAuthentication]
    lookup_field = 'user__username' # Allows URL like /profiles/5/ where 5 is User ID
    lookup_url_kwarg = 'username'
    
    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        user = instance.user
        user.delete()     # Deletes User