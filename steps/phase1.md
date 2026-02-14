# Phase 1: Authentication & User Management

## Summary

Phase 1 implements the complete authentication and user management system for EnlightBook, including JWT-based authentication, role-based access control, user management APIs, and frontend login/dashboard pages.

**Status**: ✅ **COMPLETE**

---

## What Was Built

### 1. Backend (Django)

#### Models Created

**`apps/users/models.py`** (3 models, ~280 lines)

1. **CustomUser Model** - Extended AbstractUser with:
   - 7 role flags (is_master, is_principal, is_coordinator, is_teacher, is_student, is_accountant, is_driver)
   - Profile fields (phone, address, DOB, profile_picture)
   - Security fields (2FA, password_changed_at, failed_login_attempts, account_locked_until)
   - Archive/soft-delete support
   - Utility methods: `get_roles()`, `get_primary_role()`, `is_account_locked()`, `lock_account()`, `unlock_account()`, etc.

2. **SecurityAuditLog Model** - Tracks:
   - Login/logout events
   - Password changes
   - Account locks/unlocks
   - 2FA events
   - Permission changes
   - IP address and user agent tracking

3. **LoginSession Model** - Manages:
   - Active user sessions
   - Device information
   - Concurrent session limiting
   - Session invalidation

#### Serializers Created

**`apps/users/serializers.py`** (7 serializers, ~250 lines)

- **CustomTokenObtainPairSerializer** - JWT with user data
- **UserListSerializer** - Minimal user data for lists
- **UserDetailSerializer** - Full user information
- **UserCreateSerializer** - User creation with password validation
- **UserUpdateSerializer** - User updates
- **PasswordChangeSerializer** - Password change with old password verification
- **PasswordResetRequestSerializer** - Password reset request
- **PasswordResetConfirmSerializer** - Password reset confirmation
- **UserProfileSerializer** - Current user profile

#### Views Created

**`apps/users/views.py`** (9 view classes, ~350 lines)

- **CustomTokenObtainPairView** - Login with account lock check
- **LogoutView** - Logout with token blacklisting
- **UserViewSet** - Full CRUD for user management (admin only)
  - Actions: archive, restore, unlock, reset_password
- **CurrentUserView** - Get/update current user profile
- **PasswordChangeView** - Change password
- **PasswordResetRequestView** - Request password reset email
- **PasswordResetConfirmView** - Confirm password reset with token

#### Admin Configuration

**`apps/users/admin.py`** (~140 lines)

- CustomUserAdmin with role filtering and search
- SecurityAuditLogAdmin (read-only)
- LoginSessionAdmin (read-only)
- Bulk actions: activate, deactivate, unlock accounts

#### URLs

**`apps/users/urls.py`** - 11 endpoints:

```
POST   /api/auth/login/                # Login
POST   /api/auth/logout/               # Logout
POST   /api/auth/token/refresh/        # Refresh JWT token
GET    /api/auth/me/                   # Current user profile
PATCH  /api/auth/me/                   # Update profile
POST   /api/auth/password/change/      # Change password
POST   /api/auth/password/reset/       # Request password reset
POST   /api/auth/password/reset/confirm/ # Confirm password reset
GET    /api/auth/users/                # List users (admin)
POST   /api/auth/users/                # Create user (admin)
GET    /api/auth/users/{id}/           # Get user details
PATCH  /api/auth/users/{id}/           # Update user
DELETE /api/auth/users/{id}/           # Delete user
POST   /api/auth/users/{id}/archive/   # Archive user
POST   /api/auth/users/{id}/restore/   # Restore user
POST   /api/auth/users/{id}/unlock/    # Unlock account
POST   /api/auth/users/{id}/reset_password/ # Force password reset
```

### 2. Frontend (Next.js)

#### Authentication System

**`components/auth/auth-provider.tsx`** (~170 lines)

- React Context for global auth state
- Automatic token refresh on mount
- Login/logout functions
- Cookie-based token storage (httpOnly not available in browser, using secure + sameSite)
- Role-based redirect after login

**`components/auth/protected-route.tsx`** (~100 lines)

- ProtectedRoute component with role checking
- Loading states
- Access denied handling
- Pre-built wrappers: AdminRoute, TeacherRoute, StudentRoute, AccountantRoute

#### API Client

**`lib/api.ts`** (~250 lines)

- Axios instance with interceptors
- Automatic token attachment
- Automatic token refresh on 401
- API methods:
  - authApi: login, logout, refreshToken, getCurrentUser, updateProfile, changePassword, requestPasswordReset, confirmPasswordReset
  - usersApi: getUsers, getUser, createUser, updateUser, deleteUser, archiveUser, restoreUser, unlockUser

#### Pages

**`app/login/page.tsx`** (~130 lines)

- Complete login form
- Error handling
- Password visibility toggle
- Loading states
- Link to forgot password
- Responsive design

**`app/dashboard/page.tsx`** (~120 lines)

- Protected dashboard
- User info display
- Roles display
- Quick links
- Logout button

**`app/layout.tsx`** (updated)

- AuthProvider wrapper
- Global authentication context

#### UI Components

**`components/ui/`** (5 components)

- **button.tsx** - Reusable button with variants
- **input.tsx** - Form input component
- **label.tsx** - Form label component
- **card.tsx** - Card container components
- **alert.tsx** - Alert/notification component

---

## What You Need To Do

### Prerequisites

- ✅ Phase 0 completed and working
- ✅ Docker running
- ✅ All services up (`docker-compose ps` shows all containers)

---

### Step 1: Run Database Migrations

The new User model needs to be migrated to the database:

```bash
# Run migrations
docker-compose exec backend python manage.py migrate
```

**Expected output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, users
Running migrations:
  Applying users.0001_initial... OK
```

---

### Step 2: Create Superuser

Create an admin account to access the system:

```bash
docker-compose exec backend python manage.py createsuperuser
```

**Enter details:**
- Username: `admin`
- Email: `admin@enlightbook.com`
- Password: (12+ characters, e.g., `AdminPass123!`)

---

### Step 3: Verify Backend APIs

#### Test Login API

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"AdminPass123!"}'
```

**Expected response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@enlightbook.com",
    "roles": [],
    "primary_role": "user"
  }
}
```

#### Check API Documentation

1. Open http://localhost:8000/api/docs/
2. You should see Swagger UI with all auth endpoints
3. Try the `/api/auth/me/` endpoint with "Try it out" > "Execute"

---

### Step 4: Install Frontend Dependencies

The frontend has new dependencies (js-cookie, axios, radix-ui):

```bash
docker-compose exec frontend npm install
```

**Or if running locally:**
```bash
cd frontend
npm install
```

---

### Step 5: Test Frontend Login

1. Open http://localhost:3000
2. You should see the welcome page with "API Documentation" button
3. Click "API Documentation" to verify backend is accessible
4. Navigate to http://localhost:3000/login
5. You should see the login form
6. Enter credentials:
   - Username: `admin`
   - Password: `AdminPass123!`
7. Click "Sign in"

**Expected result:**
- Redirect to `/dashboard`
- Dashboard shows your user info
- Logout button works

---

### Step 6: Test User Management (Django Admin)

1. Go to http://localhost:8000/admin/
2. Login with superuser credentials
3. Navigate to "Users" section
4. You should see:
   - Your admin user
   - Role filters (Master, Principal, Teacher, etc.)
   - Security audit logs
   - Login sessions
5. Try creating a new user:
   - Click "Add User"
   - Fill in details
   - Assign roles (e.g., is_teacher=True)
   - Save

---

### Step 7: Test API Endpoints

#### Create a Teacher User (via API)

```bash
# Get admin token first
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"AdminPass123!"}' | jq -r '.access')

# Create teacher user
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "username": "teacher1",
    "email": "teacher1@school.com",
    "password": "TeacherPass123!",
    "password_confirm": "TeacherPass123!",
    "first_name": "John",
    "last_name": "Doe",
    "is_teacher": true
  }'
```

#### Login as Teacher

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"teacher1","password":"TeacherPass123!"}'
```

---

## API Reference

### Authentication Endpoints

#### Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": { ... }
}
```

#### Logout
```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh": "jwt_refresh_token"
}
```

#### Get Current User
```http
GET /api/auth/me/
Authorization: Bearer <access_token>
```

#### Change Password
```http
POST /api/auth/password/change/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "old_password": "string",
  "new_password": "string",
  "new_password_confirm": "string"
}
```

### User Management Endpoints (Admin Only)

#### List Users
```http
GET /api/auth/users/?search=john&role=teacher&is_active=true
Authorization: Bearer <access_token>
```

#### Create User
```http
POST /api/auth/users/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "is_teacher": true
}
```

---

## Troubleshooting

### Issue: "No such table: users_customuser"

**Solution:** Run migrations
```bash
docker-compose exec backend python manage.py migrate
```

### Issue: "Invalid username or password" on login

**Solution:** 
1. Verify user exists: `docker-compose exec backend python manage.py shell -c "from apps.users.models import CustomUser; print(CustomUser.objects.filter(username='admin').exists())"`
2. Reset password: `docker-compose exec backend python manage.py changepassword admin`

### Issue: "Cannot read properties of undefined (reading 'get')" in frontend

**Solution:** Frontend dependencies not installed
```bash
docker-compose exec frontend npm install
docker-compose restart frontend
```

### Issue: CORS errors in browser console

**Solution:** Check CORS settings in backend
```bash
# In .env, ensure:
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Issue: Token refresh not working

**Solution:** Check that refresh token is being stored
1. Open browser dev tools > Application > Cookies
2. Verify `access_token` and `refresh_token` exist
3. Check they have proper expiration dates

---

## Security Features Implemented

✅ **Password Requirements:**
- Minimum 12 characters
- Cannot be common password
- Cannot be similar to username/email

✅ **Account Lockout:**
- 5 failed attempts = 15 min lock
- 10 failed attempts = 30 min lock
- 15 failed attempts = 1 hour lock
- 20+ failed attempts = 24 hour lock

✅ **JWT Security:**
- Access token: 15 minutes
- Refresh token: 7 days
- Automatic token rotation
- Token blacklisting on logout

✅ **Audit Logging:**
- All logins/logouts
- Password changes
- Account locks/unlocks
- IP address tracking

✅ **Role-Based Access:**
- 7 distinct roles
- Role-based API permissions
- Frontend protected routes

---

## Verification Checklist

Before moving to Phase 2, verify:

- [ ] Migrations applied successfully
- [ ] Superuser created
- [ ] Can login via API (curl test works)
- [ ] Can login via frontend (/login page works)
- [ ] Dashboard displays user info
- [ ] Logout works properly
- [ ] Token refresh works (test by waiting 15+ minutes)
- [ ] Django Admin accessible
- [ ] Can create users in Django Admin
- [ ] Can create users via API (admin only)
- [ ] Password validation works (try weak password)
- [ ] Audit logs are created (check /admin/users/securityauditlog/)
- [ ] Role assignment works
- [ ] Protected routes redirect unauthenticated users
- [ ] Protected routes check roles properly

---

## What's Next (Phase 2)

Once Phase 1 is verified, proceed to **Phase 2: Academic Management**:

### Phase 2 Will Build:
1. AcademicYear model
2. Semester model
3. Class and Section models
4. Subject and SubjectCategory models
5. Teacher assignments
6. Student enrollment
7. Academic structure APIs
8. Academic management UI

### Skills Needed:
- Django model relationships (ForeignKey, ManyToMany)
- Complex serializers with nested data
- Advanced Django Admin configuration
- Frontend forms with validation
- Data tables with filtering/sorting

---

## Support

If you encounter issues:

1. Check logs: `docker-compose logs <backend|frontend>`
2. Verify migrations: `docker-compose exec backend python manage.py showmigrations`
3. Test API directly with curl
4. Check browser console for frontend errors
5. Verify database: `docker-compose exec db psql -U postgres -d enlightbook -c "\dt"`

---

**Ready to proceed?** Once you've completed the steps above and verified everything works, we can begin **Phase 2: Academic Management**!
