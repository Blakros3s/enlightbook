from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class CustomUser(AbstractUser):
    """
    Custom User model with role-based access control for school management system.
    """
    
    # Role flags - A user can have multiple roles
    is_master = models.BooleanField(default=False, help_text="Super admin with full access")
    is_principal = models.BooleanField(default=False, help_text="School principal")
    is_coordinator = models.BooleanField(default=False, help_text="Department coordinator")
    is_teacher = models.BooleanField(default=False, help_text="Teacher")
    is_student = models.BooleanField(default=False, help_text="Student")
    is_accountant = models.BooleanField(default=False, help_text="Accountant")
    is_driver = models.BooleanField(default=False, help_text="Bus driver")
    
    # Profile information
    phone_number = models.CharField(
        max_length=20, 
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[\+]?[1-9][\d]{0,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Security fields
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False, help_text="Soft delete flag")
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        'self', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='archived_users'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_full_name() or 'No name'})"
    
    def get_roles(self):
        """Return list of user's roles."""
        roles = []
        if self.is_master:
            roles.append('master')
        if self.is_principal:
            roles.append('principal')
        if self.is_coordinator:
            roles.append('coordinator')
        if self.is_teacher:
            roles.append('teacher')
        if self.is_student:
            roles.append('student')
        if self.is_accountant:
            roles.append('accountant')
        if self.is_driver:
            roles.append('driver')
        return roles
    
    def get_primary_role(self):
        """Return the highest priority role."""
        if self.is_master:
            return 'master'
        if self.is_principal:
            return 'principal'
        if self.is_coordinator:
            return 'coordinator'
        if self.is_teacher:
            return 'teacher'
        if self.is_accountant:
            return 'accountant'
        if self.is_driver:
            return 'driver'
        if self.is_student:
            return 'student'
        return 'user'
    
    def is_account_locked(self):
        """Check if account is currently locked."""
        if self.account_locked_until and self.account_locked_until > timezone.now():
            return True
        return False
    
    def lock_account(self, minutes=15):
        """Lock account for specified minutes."""
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self):
        """Unlock account."""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])
    
    def increment_failed_login(self):
        """Increment failed login attempts and lock if necessary."""
        self.failed_login_attempts += 1
        
        # Lock after 5 failed attempts
        if self.failed_login_attempts >= 5:
            # Progressive lockout: 15min, 30min, 1hour, 24hours
            if self.failed_login_attempts < 10:
                self.lock_account(15)
            elif self.failed_login_attempts < 15:
                self.lock_account(30)
            elif self.failed_login_attempts < 20:
                self.lock_account(60)
            else:
                self.lock_account(1440)  # 24 hours
        else:
            self.save(update_fields=['failed_login_attempts'])
    
    def record_successful_login(self, ip_address=None):
        """Record successful login and reset counters."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.last_login_ip = ip_address
        self.last_login = timezone.now()
        self.save(update_fields=['failed_login_attempts', 'account_locked_until', 'last_login_ip', 'last_login'])
    
    def archive(self, archived_by=None):
        """Soft delete the user."""
        self.is_archived = True
        self.is_active = False
        self.archived_at = timezone.now()
        self.archived_by = archived_by
        self.save(update_fields=['is_archived', 'is_active', 'archived_at', 'archived_by'])
    
    def restore(self):
        """Restore archived user."""
        self.is_archived = False
        self.is_active = True
        self.archived_at = None
        self.archived_by = None
        self.save(update_fields=['is_archived', 'is_active', 'archived_at', 'archived_by'])


class SecurityAuditLog(models.Model):
    """
    Audit log for security-related events.
    """
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('login_failed', 'Login Failed'),
        ('password_change', 'Password Change'),
        ('password_reset_request', 'Password Reset Request'),
        ('password_reset_complete', 'Password Reset Complete'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('2fa_verified', '2FA Verified'),
        ('role_changed', 'Role Changed'),
        ('permission_granted', 'Permission Granted'),
        ('permission_revoked', 'Permission Revoked'),
    ]
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='security_logs'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    failure_reason = models.TextField(blank=True)
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Security Audit Log'
        verbose_name_plural = 'Security Audit Logs'
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"


class LoginSession(models.Model):
    """
    Track active user sessions for concurrent session management.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='login_sessions'
    )
    session_key = models.CharField(max_length=100, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_info = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.session_key[:20]}..."
    
    def deactivate(self):
        """Deactivate this session."""
        self.is_active = False
        self.save(update_fields=['is_active'])
