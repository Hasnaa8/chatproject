from celery import shared_task
from django.core.mail import send_mail

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

    