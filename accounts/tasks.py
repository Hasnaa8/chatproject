from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from .models import EmailOTP
from django.utils import timezone

@shared_task
def send_otp_email(email, otp):
    # print(otp)
    return send_mail(
            "Your Verification Code",
            f"Your OTP is: {otp}. It expires in 10 minutes.",
            "hasnaaprogs@gmail.com",
            [email],
            )
        
@shared_task
def send_welcome_email(email):
    return send_mail(
            "Welcoming message",
            f"Welcome to our program.",
            "hasnaaprogs@gmail.com",
            [email],
        )

@shared_task
def cleanup_expired_otps():
    time_to_expired = timezone.now() - timedelta(minutes=10)
    deleted_count, _ = EmailOTP.objects.filter(created_at__lt=time_to_expired).delete()
    return f"Deleted {deleted_count} expired OTPs"