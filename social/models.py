from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class FriendShip(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'
    
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships_received', on_delete=models.CASCADE)
    status = models.CharField(choices=Status.choices, max_length=20, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError("You cannot send a friend request to yourself.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Friendship: {self.from_user.username} - {self.to_user.username} [{self.status}]"
