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
    BET_TYPE_CHOICES = [
        ('SINGLE', 'Single Bet'),
        ('SP', 'All SP'),
        ('DP', 'All DP'),
        ('JODI', 'Jodi Vagar'),
        ('DADAR', 'Dadar'),
        ('EKI', 'Eki'),
        ('BEKI', 'Beki'),
        ('ABR_CUT', 'ABR Cut'),
        ('JODI_PANEL', 'Jodi Panel'),
        ('MOTAR', 'Motar'),
        ('COMMAN_PANA_36', 'Comman Pana 36'),
        ('COMMAN_PANA_56', 'Comman Pana 56'),
        ('SET_PANA', 'Set Pana'),
    ]
    
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
    
    # Additional fields for better filtration
    bet_type = models.CharField(max_length=20, choices=BET_TYPE_CHOICES, default='SINGLE')
    column_number = models.IntegerField(null=True, blank=True)  # Column 1-10 for applicable bet types
    sub_type = models.CharField(max_length=20, null=True, blank=True)  # For storing jodi_type (5,7,12) or panel_type (6,7)
    
    # Session tracking
    session_id = models.CharField(max_length=100, null=True, blank=True)  # For grouping bets in same session
    
    # Result tracking (for future use)
    is_winner = models.BooleanField(default=False)
    winning_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    result_declared_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'number']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'bet_type']),
            models.Index(fields=['user', 'column_number']),
            models.Index(fields=['created_at']),
            models.Index(fields=['bet_type', 'column_number']),
        ]

    def __str__(self):
        return f"{self.user.username} bet ₹{self.amount} on {self.number} ({self.bet_type})"


class BulkBetAction(models.Model):
    """Track bulk betting operations for undo functionality"""
    ACTION_TYPES = [
        ('SP', 'All SP'),
        ('DP', 'All DP'),
        ('JODI', 'Jodi Vagar'),
        ('DADAR', 'Dadar'),
        ('EKI', 'Eki'),
        ('BEKI', 'Beki'),
        ('ABR_CUT', 'ABR Cut'),
        ('JODI_PANEL', 'Jodi Panel'),
        ('MOTAR', 'Motar'),
        ('COMMAN_PANA_36', 'Comman Pana 36'),
        ('COMMAN_PANA_56', 'Comman Pana 56'),
        ('SET_PANA', 'Set Pana'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bulk_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_bets = models.IntegerField(default=0)
    
    # For tracking column-based bets
    jodi_column = models.IntegerField(null=True, blank=True)  # 1-10 (used for first column in multi-column)
    jodi_type = models.IntegerField(null=True, blank=True)  # 5, 7, or 12 for JODI; 6 or 7 for JODI_PANEL
    
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