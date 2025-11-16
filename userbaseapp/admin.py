from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Bet, BulkBetAction

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'date_joined')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 50


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_link', 'number', 'formatted_amount', 'bet_type_badge', 
        'column_number', 'bazar_display', 'bet_date', 'status_badge', 
        'created_at', 'is_deleted'
    ]
    list_filter = [
        'bet_type', 'bazar', 'status', 'is_deleted', 'bet_date', 
        'created_at', 'column_number', 'family_group'
    ]
    search_fields = [
        'number', 'user__email', 'user__username', 'user__first_name', 
        'user__last_name', 'session_id', 'input_digits'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'number', 'amount', 'bet_type', 'status')
        }),
        ('Bazar & Date', {
            'fields': ('bazar', 'bet_date'),
            'description': 'Market and date information'
        }),
        ('Bet Details', {
            'fields': ('column_number', 'sub_type', 'bulk_action', 'session_id'),
            'classes': ('collapse',)
        }),
        ('Special Bet Types', {
            'fields': ('family_group', 'input_digits', 'search_digit'),
            'classes': ('collapse',),
            'description': 'Fields for Set Pana, Motar, and Common Pana bets'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'notes'),
            'classes': ('collapse',)
        }),
        ('Deletion Info', {
            'fields': ('is_deleted', 'deleted_at', 'deleted_by'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 100
    actions = ['soft_delete_bets']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'bulk_action', 'deleted_by')
    
    def user_link(self, obj):
        return format_html(
            '<a href="/admin/userbaseapp/customuser/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def formatted_amount(self, obj):
        return f'₹{obj.amount:,.2f}'
    formatted_amount.short_description = 'Amount'
    formatted_amount.admin_order_field = 'amount'
    
    def bet_type_badge(self, obj):
        colors = {
            'SINGLE': '#6366f1',  # Indigo
            'SP': '#84cc16',      # Lime
            'DP': '#3b82f6',      # Blue
            'JODI': '#a855f7',    # Purple
            'DADAR': '#eab308',   # Yellow
            'EKI': '#06b6d4',     # Cyan
            'BEKI': '#06b6d4',    # Cyan
            'ABR_CUT': '#ec4899', # Pink
            'JODI_PANEL': '#14b8a6', # Teal
            'MOTAR': '#f97316',   # Orange
            'COMMAN_PANA_36': '#3b82f6', # Blue
            'COMMAN_PANA_56': '#6366f1', # Indigo
            'SET_PANA': '#8b5cf6', # Violet
        }
        color = colors.get(obj.bet_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_bet_type_display()
        )
    bet_type_badge.short_description = 'Type'
    bet_type_badge.admin_order_field = 'bet_type'
    
    def status_badge(self, obj):
        colors = {
            'ACTIVE': '#22c55e',    # Green
            'CANCELLED': '#6b7280', # Gray
        }
        color = colors.get(obj.status, '#22c55e')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def bazar_display(self, obj):
        return obj.get_bazar_display()
    bazar_display.short_description = 'Bazar'
    bazar_display.admin_order_field = 'bazar'
    
    # Admin actions
    def soft_delete_bets(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(is_deleted=False).update(
            is_deleted=True,
            deleted_at=timezone.now(),
            deleted_by=request.user,
            status='CANCELLED'
        )
        self.message_user(request, f'{updated} bets soft deleted')
    soft_delete_bets.short_description = 'Soft delete selected bets'


@admin.register(BulkBetAction)
class BulkBetActionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_link', 'action_type_badge', 'formatted_amount', 
        'total_bets', 'formatted_total_amount', 'bazar_display', 
        'action_date', 'status_badge', 'is_undone', 'created_at'
    ]
    list_filter = [
        'action_type', 'bazar', 'is_undone', 'status', 'action_date',
        'created_at', 'jodi_column', 'jodi_type', 'family_group'
    ]
    search_fields = [
        'user__email', 'user__username', 'user__first_name', 
        'user__last_name', 'input_data', 'columns_used'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'undone_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'action_type', 'amount', 'total_bets', 'total_amount')
        }),
        ('Bazar & Date', {
            'fields': ('bazar', 'action_date'),
            'description': 'Market and date information'
        }),
        ('Bet Configuration', {
            'fields': ('jodi_column', 'jodi_type', 'columns_used'),
            'classes': ('collapse',),
            'description': 'Column and type settings for Jodi and Panel bets'
        }),
        ('Special Bet Types', {
            'fields': ('family_group', 'family_numbers', 'input_data', 'search_digit'),
            'classes': ('collapse',),
            'description': 'Settings for Set Pana, Motar, and Common Pana bets'
        }),
        ('Status & Undo', {
            'fields': ('status', 'is_undone', 'undone_at', 'undone_by'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'notes', 'is_deleted', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 100
    actions = ['undo_bulk_actions']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'undone_by').prefetch_related('bets')
    
    def user_link(self, obj):
        return format_html(
            '<a href="/admin/userbaseapp/customuser/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def formatted_amount(self, obj):
        return f'₹{obj.amount:,.2f}'
    formatted_amount.short_description = 'Bet Amount'
    formatted_amount.admin_order_field = 'amount'
    
    def formatted_total_amount(self, obj):
        return f'₹{obj.total_amount:,.2f}'
    formatted_total_amount.short_description = 'Total Amount'
    formatted_total_amount.admin_order_field = 'total_amount'
    
    def action_type_badge(self, obj):
        colors = {
            'SP': '#84cc16',      # Lime
            'DP': '#3b82f6',      # Blue
            'JODI': '#a855f7',    # Purple
            'DADAR': '#eab308',   # Yellow
            'EKI': '#06b6d4',     # Cyan
            'BEKI': '#06b6d4',    # Cyan
            'ABR_CUT': '#ec4899', # Pink
            'JODI_PANEL': '#14b8a6', # Teal
            'MOTAR': '#f97316',   # Orange
            'COMMAN_PANA_36': '#3b82f6', # Blue
            'COMMAN_PANA_56': '#6366f1', # Indigo
            'SET_PANA': '#8b5cf6', # Violet
        }
        color = colors.get(obj.action_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_action_type_display()
        )
    action_type_badge.short_description = 'Action Type'
    action_type_badge.admin_order_field = 'action_type'
    
    def status_badge(self, obj):
        colors = {
            'ACTIVE': '#22c55e',       # Green
            'UNDONE': '#6b7280',       # Gray
        }
        color = colors.get(obj.status, '#22c55e')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def bazar_display(self, obj):
        return obj.get_bazar_display()
    bazar_display.short_description = 'Bazar'
    bazar_display.admin_order_field = 'bazar'
    
    # Admin actions
    def undo_bulk_actions(self, request, queryset):
        undone_count = 0
        for bulk_action in queryset.filter(is_undone=False):
            success, message = bulk_action.undo(undone_by_user=request.user)
            if success:
                undone_count += 1
        self.message_user(request, f'{undone_count} bulk actions undone successfully')
    undo_bulk_actions.short_description = 'Undo selected bulk actions'
