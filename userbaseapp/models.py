# userbaseapp/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class CustomUser(AbstractUser):
    """Custom user model"""
    pass

    def __str__(self):
        return self.email or self.username


CustomUser = get_user_model()


class Bet(models.Model):
    """Individual bet model"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bets')
    number = models.CharField(max_length=10)  # "000", "999", "137", etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New fields for tracking bulk operations
    bulk_action = models.ForeignKey(
        'BulkBetAction', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='bets'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'number']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} bet ₹{self.amount} on {self.number}"


class BulkBetAction(models.Model):
    """Track bulk betting operations for undo functionality"""
    ACTION_TYPES = [
        ('SP', 'All SP'),
        ('DP', 'All DP'),
        ('JODI', 'Jodi Vagar'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bulk_actions')
    action_type = models.CharField(max_length=10, choices=ACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_bets = models.IntegerField(default=0)
    
    # For Jodi Vagar tracking
    jodi_column = models.IntegerField(null=True, blank=True)  # 1-10
    jodi_type = models.IntegerField(null=True, blank=True)  # 5, 7, or 12
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_undone = models.BooleanField(default=False)  # Track if already undone

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.action_type} - ₹{self.amount} ({self.total_bets} bets)"

    def undo(self):
        """Undo this bulk action by deleting all associated bets"""
        if self.is_undone:
            return False, "Already undone"
        
        deleted_count = self.bets.all().delete()[0]
        self.is_undone = True
        self.save()
        return True, f"Undone {deleted_count} bets"