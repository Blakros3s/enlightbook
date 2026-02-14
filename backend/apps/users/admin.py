from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import CustomUser, SecurityAuditLog, LoginSession


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model.
    """
    list_display = [
        'username', 'email', 'full_name', 'get_roles_display',
        'is_active', 'is_staff', 'last_login', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser',
        'is_master', 'is_principal', 'is_coordinator',
        'is_teacher', 'is_student', 'is_accountant', 'is_driver',
        'created_at', 'is_archived'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth', 'profile_picture')
        }),
        ('Roles', {
            'fields': (
                'is_master', 'is_principal', 'is_coordinator',
                'is_teacher', 'is_student', 'is_accountant', 'is_driver'
            ),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Security', {
            'fields': (
                'two_factor_enabled', 'last_login_ip', 'failed_login_attempts',
                'account_locked_until'
            ),
            'classes': ('collapse',)
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
        ('Archive Status', {
            'fields': ('is_archived', 'archived_at', 'archived_by'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = [
        'last_login', 'date_joined', 'created_at', 'updated_at',
        'last_login_ip', 'failed_login_attempts', 'archived_at', 'archived_by'
    ]
    
    def full_name(self, obj):
        return obj.get_full_name() or '-'
    full_name.short_description = 'Full Name'
    
    def get_roles_display(self, obj):
        roles = obj.get_roles()
        if not roles:
            return '-'
        return ', '.join(roles)
    get_roles_display.short_description = 'Roles'
    
    actions = ['make_active', 'make_inactive', 'unlock_accounts']
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Activate selected users"
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Deactivate selected users"
    
    def unlock_accounts(self, request, queryset):
        for user in queryset:
            user.unlock_account()
    unlock_accounts.short_description = "Unlock selected accounts"


@admin.register(SecurityAuditLog)
class SecurityAuditLogAdmin(admin.ModelAdmin):
    """
    Admin interface for security audit logs.
    """
    list_display = ['user', 'action', 'ip_address', 'timestamp', 'success']
    list_filter = ['action', 'success', 'timestamp']
    search_fields = ['user__username', 'user__email', 'ip_address']
    readonly_fields = [
        'user', 'action', 'ip_address', 'user_agent', 'timestamp',
        'success', 'failure_reason', 'additional_data'
    ]
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for login sessions.
    """
    list_display = ['user', 'session_key_short', 'ip_address', 'device_info', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'session_key', 'ip_address']
    readonly_fields = [
        'user', 'session_key', 'ip_address', 'user_agent',
        'device_info', 'location', 'created_at', 'last_activity'
    ]
    ordering = ['-created_at']
    
    def session_key_short(self, obj):
        return obj.session_key[:20] + '...' if len(obj.session_key) > 20 else obj.session_key
    session_key_short.short_description = 'Session Key'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
