from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Bet, BulkBetAction

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Fields to display in the admin list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser')

    # Fields to show when viewing/editing a user
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields to show when creating a new user
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
    list_display = ['id', 'user', 'number', 'amount', 'bet_type', 'column_number', 'sub_type', 'created_at', 'is_winner']
    list_filter = ['bet_type', 'column_number', 'is_winner', 'created_at', 'sub_type']
    search_fields = ['number', 'user__email', 'user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'number', 'amount', 'bet_type')
        }),
        ('Bet Details', {
            'fields': ('column_number', 'sub_type', 'session_id')
        }),
        ('Result Information', {
            'fields': ('is_winner', 'winning_amount', 'result_declared_at')
        }),
        ('Metadata', {
            'fields': ('bulk_action', 'created_at')
        }),
    )
    
    list_per_page = 50
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'bulk_action')


@admin.register(BulkBetAction)
class BulkBetActionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'action_type', 'amount', 'total_bets', 'jodi_column', 'jodi_type', 'created_at', 'is_undone']
    list_filter = ['action_type', 'is_undone', 'created_at', 'jodi_column', 'jodi_type']
    search_fields = ['user__email', 'user__username']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    list_per_page = 50