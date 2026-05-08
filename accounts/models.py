import random
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    
    contacts = models.ManyToManyField(
        'self', 
        symmetrical=True, 
        blank=True,
    )

    def __str__(self):
        return self.username
    
class EmailOTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='otp_device')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # OTP expires after 10 minutes
        return timezone.now() < self.created_at + timedelta(minutes=10)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.created_at = timezone.now()
        self.save()

    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp}"


class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
            upload_to='profiles/%Y/%m/', 
            default='profiles/default_user.png',
            blank=True,
            null=True
        )    
    other_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=10, unique=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True, null=True)
    url = models.URLField(max_length=255, blank=True, null=True)    
    links = models.JSONField(default=dict, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
    
    @staticmethod
    def is_fill(att):
        if att is not None and str(att).strip()!="":
            return True
        return False
        
    def save(self, *args, **kwargs):
        required_fields = [
            self.is_fill(self.bio), 
            self.is_fill(self.phone_number), 
            self.is_fill(self.first_name), 
            self.is_fill(self.last_name),
            self.is_fill(self.url),
            self.is_fill(self.gender)
        ]
        self.is_completed = all(required_fields)
        
        super().save(*args, **kwargs)