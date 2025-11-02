# userbaseapp/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db import models
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    # You can add more fields later, e.g. profile_picture, bio, etc.
    pass

    def __str__(self):
        return self.email or self.username

# userbaseapp/models.py


CustomUser = get_user_model()

class Bet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bets')
    number = models.CharField(max_length=10)  # can store "000", "999", etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bet ₹{self.amount} on {self.number} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
