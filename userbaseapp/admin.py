from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Bet, BulkBetAction

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
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
    search_fields = ('email', 'username')
    ordering = ('email',)


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'number', 'amount', 'bet_type', 'column_number', 'sub_type', 'created_at', 'status']
    list_filter = ['bet_type', 'column_number', 'status', 'created_at', 'sub_type']
    search_fields = ['number', 'user__email', 'user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'number', 'amount', 'bet_type', 'status')
        }),
        ('Bet Details', {
            'fields': ('column_number', 'sub_type', 'session_id', 'family_group', 'input_digits', 'search_digit')
        }),
        ('Metadata', {
            'fields': ('bulk_action', 'created_at', 'updated_at', 'notes', 'is_deleted', 'deleted_at', 'deleted_by')
        }),
    )
    list_per_page = 50
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'bulk_action')


@admin.register(BulkBetAction)
class BulkBetActionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'action_type', 'amount', 'total_bets', 'jodi_column', 'jodi_type', 'created_at', 'is_undone', 'status']
    list_filter = ['action_type', 'is_undone', 'status', 'created_at', 'jodi_column', 'jodi_type']
    search_fields = ['user__email', 'user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'action_type', 'amount', 'total_bets', 'total_amount')
        }),
        ('Bet Details', {
            'fields': ('jodi_column', 'jodi_type', 'columns_used', 'family_group', 'family_numbers', 'input_data', 'search_digit')
        }),
        ('Status', {
            'fields': ('status', 'is_undone', 'undone_at', 'undone_by')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'notes', 'is_deleted', 'deleted_at')
        }),
    )
    list_per_page = 50
