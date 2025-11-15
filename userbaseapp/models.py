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
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('WON', 'Won'),
        ('LOST', 'Lost'),
        ('CANCELLED', 'Cancelled'),
        ('PENDING', 'Pending'),
    ]
    
    BAZAR_CHOICES = [
        ('SRIDEVI_OPEN', 'Sridevi Open'),
        ('SRIDEVI_CLOSED', 'Sridevi Closed'),
        ('TIME_OPEN', 'Time Open'),
        ('TIME_CLOSED', 'Time Closed'),
        ('DIVAS_MILAN_OPEN', 'Divas Milan Open'),
        ('DIVAS_MILAN_CLOSED', 'Divas Milan Closed'),
        ('KALYAN_OPEN', 'Kalyan Open'),
        ('KALYAN_CLOSED', 'Kalyan Closed'),
        ('NIGHT_MILAN_OPEN', 'Night Milan Open'),
        ('NIGHT_MILAN_CLOSED', 'Night Milan Closed'),
    ]
    
    # Core fields
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bets', db_index=True)
    number = models.CharField(max_length=10, db_index=True)  # "000", "999", "137", etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Bazar and Date
    bazar = models.CharField(max_length=30, choices=BAZAR_CHOICES, default='SRIDEVI_OPEN', db_index=True)
    bet_date = models.DateField(default=timezone.now, db_index=True)  # Date of bet placement
    
    # Bulk action tracking
    bulk_action = models.ForeignKey(
        'BulkBetAction', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='bets'
    )
    
    # Bet type and classification
    bet_type = models.CharField(max_length=20, choices=BET_TYPE_CHOICES, default='SINGLE', db_index=True)
    column_number = models.IntegerField(null=True, blank=True, db_index=True)  # Column 1-10 for applicable bet types
    sub_type = models.CharField(max_length=20, null=True, blank=True)  # For storing jodi_type (5,7,12) or panel_type (6,7)
    
    # Family/Group tracking for Set Pana
    family_group = models.CharField(max_length=10, null=True, blank=True, db_index=True)  # G1-G35 for Set Pana
    
    # Motar/Comman Pana specific
    input_digits = models.CharField(max_length=20, null=True, blank=True)  # Store original input for Motar
    search_digit = models.IntegerField(null=True, blank=True)  # Store digit for Common Pana searches
    
    # Session and grouping
    session_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)  # For grouping bets in same session
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    
    # Additional metadata
    notes = models.TextField(null=True, blank=True)  # Admin notes
    is_deleted = models.BooleanField(default=False, db_index=True)  # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_bets')

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'number']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'bet_type']),
            models.Index(fields=['user', 'column_number']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['bet_type', 'column_number']),
            models.Index(fields=['bulk_action', 'created_at']),
            models.Index(fields=['family_group', 'bet_type']),
            models.Index(fields=['user', 'bazar', 'bet_date']),
            models.Index(fields=['bazar', 'bet_date']),
        ]
        verbose_name = 'Bet'
        verbose_name_plural = 'Bets'

    def __str__(self):
        return f"{self.user.username} bet ₹{self.amount} on {self.number} ({self.bet_type}) - {self.status}"
    
    def soft_delete(self, deleted_by_user):
        """Soft delete the bet"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by_user
        self.status = 'CANCELLED'
        self.save()


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
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('UNDONE', 'Undone'),
        ('PARTIAL_UNDONE', 'Partially Undone'),
        ('COMPLETED', 'Completed'),
    ]
    
    BAZAR_CHOICES = [
        ('SRIDEVI_OPEN', 'Sridevi Open'),
        ('SRIDEVI_CLOSED', 'Sridevi Closed'),
        ('TIME_OPEN', 'Time Open'),
        ('TIME_CLOSED', 'Time Closed'),
        ('DIVAS_MILAN_OPEN', 'Divas Milan Open'),
        ('DIVAS_MILAN_CLOSED', 'Divas Milan Closed'),
        ('KALYAN_OPEN', 'Kalyan Open'),
        ('KALYAN_CLOSED', 'Kalyan Closed'),
        ('NIGHT_MILAN_OPEN', 'Night Milan Open'),
        ('NIGHT_MILAN_CLOSED', 'Night Milan Closed'),
    ]
    
    # Core fields
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bulk_actions', db_index=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_bets = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total amount across all bets
    
    # Bazar and Date
    bazar = models.CharField(max_length=30, choices=BAZAR_CHOICES, default='SRIDEVI_OPEN', db_index=True)
    action_date = models.DateField(default=timezone.now, db_index=True)
    
    # Column and type tracking
    jodi_column = models.IntegerField(null=True, blank=True, db_index=True)  # 1-10 (used for first column in multi-column)
    jodi_type = models.IntegerField(null=True, blank=True)  # 5, 7, or 12 for JODI; 6 or 7 for JODI_PANEL
    columns_used = models.CharField(max_length=100, null=True, blank=True)  # Comma-separated list of columns for multi-column bets
    
    # Family/Group tracking for Set Pana
    family_group = models.CharField(max_length=10, null=True, blank=True, db_index=True)  # G1-G35 for Set Pana
    family_numbers = models.TextField(null=True, blank=True)  # JSON array of numbers in the family
    
    # Motar/Comman Pana specific
    input_data = models.CharField(max_length=100, null=True, blank=True)  # Store original input
    search_digit = models.IntegerField(null=True, blank=True)  # Digit for Common Pana
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    is_undone = models.BooleanField(default=False, db_index=True)  # Track if already undone
    undone_at = models.DateTimeField(null=True, blank=True)
    undone_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='undone_bulk_actions')
    
    # Metadata
    notes = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'action_type']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['is_undone', 'status']),
            models.Index(fields=['user', 'bazar', 'action_date']),
            models.Index(fields=['bazar', 'action_date']),
        ]
        verbose_name = 'Bulk Bet Action'
        verbose_name_plural = 'Bulk Bet Actions'

    def __str__(self):
        return f"{self.user.username} - {self.action_type} - ₹{self.amount} ({self.total_bets} bets) - {self.status}"

    def undo(self, undone_by_user=None):
        """Undo this bulk action by deleting all associated bets"""
        if self.is_undone:
            return False, "Already undone"
        
        deleted_count = self.bets.all().delete()[0]
        self.is_undone = True
        self.status = 'UNDONE'
        self.undone_at = timezone.now()
        if undone_by_user:
            self.undone_by = undone_by_user
        self.save()
        return True, f"Undone {deleted_count} bets"
