# Authentication & Authorization Service

## Service Overview
Centralized authentication and authorization service managing user access, roles, permissions, and security features for the school management system.

## Core Responsibilities
- User authentication (login/logout/session management)
- Role-based access control (RBAC)
- Permission management
- JWT token generation and validation
- Password management and security policies
- Two-factor authentication (2FA)
- SSO integration support

## User Roles

### Role Hierarchy
```
Master (Level 100)
  ├── Principal (Level 80)
  │   ├── Coordinator (Level 60)
  │   ├── Teacher (Level 40)
  │   └── Accountant (Level 40)
  ├── Driver (Level 20)
  └── Student (Level 10)
```

### Role Definitions

#### 1. Master (Super Admin)
- **Access**: Full system access
- **Permissions**:
  - Manage all users and roles
  - Configure system settings
  - Access all data across all schools (multi-tenant support)
  - System-wide reporting
  - Database backups and maintenance

#### 2. Principal
- **Access**: School-wide administrative access
- **Permissions**:
  - Manage teachers, students, and accountants
  - View all financial data
  - Approve leave applications
  - Publish exam results
  - Generate school-wide reports
  - Manage academic calendar

#### 3. Coordinator
- **Access**: Department or grade-level management
- **Permissions**:
  - Manage assigned classes/departments
  - Coordinate teacher assignments
  - Monitor attendance and performance
  - Generate departmental reports
  - Limited financial view access

#### 4. Teacher
- **Access**: Class and subject-specific
- **Permissions**:
  - Manage assigned classes and subjects
  - Mark attendance for assigned classes
  - Enter exam marks
  - Create and grade assignments
  - Communicate with students and parents
  - View student performance for assigned students

#### 5. Student
- **Access**: Personal data and assigned resources
- **Permissions**:
  - View own attendance, marks, and results
  - Submit assignments
  - Access study materials
  - View fee details
  - Participate in quizzes and discussions
  - Communicate with teachers

#### 6. Accountant
- **Access**: Financial management
- **Permissions**:
  - Manage fee categories and structures
  - Generate bills and record payments
  - Financial reporting
  - Expense management
  - View student financial records

#### 7. Driver
- **Access**: Transportation management
- **Permissions**:
  - Update bus location (GPS)
  - View assigned route and students
  - Update trip status
  - View transportation schedules

## Authentication Flow

### Django Backend

```python
# JWT Token-based Authentication
1. User Login → POST /api/auth/login
   - Credentials: username + password
   - Response: access_token, refresh_token, user_profile

2. Token Refresh → POST /api/auth/refresh
   - Requires: valid refresh_token
   - Response: new access_token

3. Token Validation → Middleware on every request
   - Extract JWT from Authorization header
   - Verify signature and expiration
   - Attach user object to request

4. Logout → POST /api/auth/logout
   - Blacklist refresh token (using redis)
```

### Next.js Frontend

```javascript
// Authentication Context
1. Login Authentication
   - Call Django API
   - Store tokens in httpOnly cookies
   - Set user state in React Context

2. Protected Routes
   - Check auth status before rendering
   - Redirect to login if unauthenticated
   - Verify role-based access

3. Auto Token Refresh
   - Intercept 401 responses
   - Attempt token refresh
   - Retry original request
```

## Security Features

### 1. Password Policy
```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    # Custom: require uppercase, lowercase, digit, special char
]
```

- Minimum 12 characters
- Must include: uppercase, lowercase, number, special character
- Cannot be similar to username or email
- Password expiry: 90 days (configurable)
- Password history: Cannot reuse last 5 passwords

### 2. Two-Factor Authentication (2FA)
- **Methods**: TOTP (Google Authenticator), SMS, Email
- **Implementation**: django-otp
- **Enrollment**: Optional for students, required for admin roles
- **Backup codes**: 10 single-use recovery codes

### 3. Account Security
- **Failed Login Attempts**: Lock after 5 failed attempts
- **Lockout Duration**: 15 minutes (progressive: 15m, 30m, 1h, 24h)
- **Session Timeout**: 30 minutes inactivity
- **Concurrent Sessions**: Maximum 3 devices
- **IP Whitelisting**: Optional for admin accounts

### 4. Audit Logging
```python
class SecurityAuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # login, logout, password_change, etc.
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField()
    failure_reason = models.TextField(blank=True)
```

Track:
- All authentication attempts
- Permission grant/revoke actions
- Role changes
- Sensitive data access
- Failed authorization attempts

## Permission System

### Django Permissions
```python
# Use Django's built-in Groups and Permissions
from django.contrib.auth.models import Group, Permission

# Create role-based groups
groups = ['Master', 'Principal', 'Teacher', 'Student', 'Accountant', 'Driver', 'Coordinator']

# Assign permissions to groups
principal_group = Group.objects.get(name='Principal')
principal_group.permissions.add(
    Permission.objects.get(codename='view_all_students'),
    Permission.objects.get(codename='publish_results'),
    Permission.objects.get(codename='approve_leaves'),
)
```

### Custom Permissions
```python
class Meta:
    permissions = [
        ("view_all_students", "Can view all students"),
        ("publish_results", "Can publish exam results"),
        ("approve_leaves", "Can approve leave applications"),
        ("manage_fees", "Can manage fee structures"),
        ("view_financial_reports", "Can view financial reports"),
        # ... more custom permissions
    ]
```

### Resource-Level Permissions
```python
# Teachers can only edit their assigned classes
class IsTeacherOfClass(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_teacher:
            teacher = request.user.teacher
            return obj.class_assigned in teacher.classes.all()
        return False
```

## API Endpoints

### Authentication
```
POST   /api/auth/login               # User login
POST   /api/auth/logout              # User logout
POST   /api/auth/refresh             # Refresh access token
POST   /api/auth/register            # New user registration (admin only)
POST   /api/auth/password/change     # Change password
POST   /api/auth/password/reset      # Request password reset
POST   /api/auth/password/reset/confirm  # Confirm password reset
GET    /api/auth/me                  # Get current user profile
```

### 2FA Management
```
POST   /api/auth/2fa/enable          # Enable 2FA
POST   /api/auth/2fa/verify          # Verify 2FA code
POST   /api/auth/2fa/disable         # Disable 2FA
GET    /api/auth/2fa/recovery-codes  # Get backup codes
```

### User Management (Admin)
```
GET    /api/users                    # List all users
POST   /api/users                    # Create user
GET    /api/users/:id                # Get user details
PUT    /api/users/:id                # Update user
DELETE /api/users/:id                # Deactivate user
POST   /api/users/:id/reset-password # Force password reset
```

### Role & Permission Management
```
GET    /api/roles                    # List all roles
GET    /api/roles/:id/permissions    # Get role permissions
PUT    /api/roles/:id/permissions    # Update role permissions
POST   /api/users/:id/assign-role    # Assign role to user
```

## Database Schema

### Core Models
```python
class CustomUser(AbstractUser):
    # Role flags (to be migrated to Groups)
    is_master = models.BooleanField(default=False)
    is_principal = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_accountant = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)
    is_coordinator = models.BooleanField(default=False)
    
    # Security fields
    phone_number = models.CharField(max_length=20, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    password_changed_at = models.DateTimeField(null=True)
    last_login_ip = models.GenericIPAddressField(null=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True)
    
    # Status
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True)
    archived_by = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
```

## Implementation Priorities

### Phase 1: Security Foundation (Week 1-2)
1. Implement JWT authentication with refresh tokens
2. Add password policy enforcement
3. Set up account lockout mechanism
4. Create security audit logging
5. Implement CORS properly

### Phase 2: Advanced Auth (Week 3-4)
1. Add 2FA support (TOTP)
2. Implement session management
3. Create password reset flow
4. Add email verification
5. Set up role-based access control

### Phase 3: User Management (Week 5-6)
1. Build admin user management interface
2. Create role assignment workflow
3. Implement permission management UI
4. Add bulk user operations
5. Create user activity dashboard

## Technology Stack

### Backend
- **Framework**: Django 4.2+
- **Authentication**: Django REST Framework + SimpleJWT
- **2FA**: django-otp + qrcode
- **Password Security**: django-password-validators
- **Session Storage**: Redis (for token blacklisting)
- **Rate Limiting**: django-ratelimit

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **State Management**: React Context API + Zustand
- **HTTP Client**: Axios with interceptors
- **Form Validation**: Zod + React Hook Form
- **Cookie Management**: js-cookie
- **2FA**: speakeasy (for TOTP)

## Security Best Practices

1. **Token Management**
   - Access token: 15 minutes expiry
   - Refresh token: 7 days expiry
   - Rotate refresh tokens on use
   - Store tokens in httpOnly cookies (Not localStorage)

2. **API Security**
   - HTTPS only in production
   - CORS whitelist (no wildcards)
   - Rate limiting on auth endpoints
   - Input validation on all endpoints
   - SQL injection prevention (ORM)

3. **Password Security**
   - Bcrypt with 12 rounds (Django default)
   - Never store plain text
   - Secure password reset tokens (1-hour expiry)
   - Password change requires old password

4. **Session Security**
   - Secure flag on cookies
   - HttpOnly flag on auth cookies
   - SameSite=Lax or Strict
   - CSRF token for state-changing requests

## Testing Strategy

### Unit Tests
- Password validation rules
- JWT token generation and verification
- Permission checking logic
- Account lockout mechanism

### Integration Tests
- Complete authentication flow
- Token refresh flow
- 2FA enrollment and verification
- Role assignment and permission checks

### Security Tests
- Brute force protection
- Token expiration handling
- CSRF protection
- XSS prevention
- SQL injection attempts

## Monitoring & Alerts

### Metrics to Track
- Failed login attempts per hour
- Successful logins by role
- Token refresh rate
- Account lockouts
- 2FA enrollment rate
- Session durations

### Alerts
- Unusual login patterns (location, time)
- Multiple failed login attempts
- Bulk permission changes
- Admin account creation/deletion
- Disabled 2FA on admin accounts
