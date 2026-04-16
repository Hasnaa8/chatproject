from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse

from django_rest_passwordreset.signals import reset_password_token_created

# 1. Signal tools to connect the "Eavesdropper" to the User model
from django.db.models.signals import post_save
from django.dispatch import receiver

# 2. Your Custom Models
from .models import CustomUser, EmailOTP

# 3. Email and Utilities
from django.core.mail import send_mail
from django.utils import timezone  # Useful for timestamping OTP creation
import random
from .tasks import send_otp_email


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
            reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('email/password_reset_email.html', context)
    email_plaintext_message = render_to_string('email/password_reset_email.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Your Website Title"),
        # message:
        email_plaintext_message,
        # from:
        "hasnaaprogs@gmail.com",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()



@receiver(post_save, sender=CustomUser)
def send_otp_on_register(sender, instance, created, **kwargs):
    if created and not instance.is_verified:
        # Create or get OTP object
        otp_obj, _ = EmailOTP.objects.get_or_create(user=instance)        
        otp_obj.generate_otp()
        send_otp_email.delay(instance.email, otp_obj.otp)
        
        
        