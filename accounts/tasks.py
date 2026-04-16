from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_welcome_email(email):
    return send_mail(
            "Welcoming message",
            f"Welcome to our program.",
            "hasnaaprogs@gmail.com",
            [email],
        )