from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import SecurityAuditLog
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    UserProfileSerializer,
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view that includes user data in response.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        # Check if user exists and account is locked
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
            if user.is_account_locked():
                return Response(
                    {'detail': 'Account is locked. Please try again later.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except User.DoesNotExist:
            pass
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            # Record successful login
            user = User.objects.get(username=username)
            ip_address = request.META.get('REMOTE_ADDR')
            user.record_successful_login(ip_address)
            
            # Log the login
            SecurityAuditLog.objects.create(
                user=user,
                action='login',
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True
            )
        
        return response


class LogoutView(APIView):
    """
    Logout view that blacklists the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Log the logout
            SecurityAuditLog.objects.create(
                user=request.user,
                action='logout',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True
            )
            
            return Response(
                {'detail': 'Successfully logged out.'},
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {'detail': 'Invalid token.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management (admin only).
    """
    queryset = User.objects.filter(is_archived=False)
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'list':
            return UserListSerializer
        return UserDetailSerializer
    
    def get_queryset(self):
        queryset = User.objects.filter(is_archived=False)
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            role_filter = {f'is_{role}': True}
            queryset = queryset.filter(**role_filter)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        
        return queryset.select_related().order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Soft delete a user."""
        user = self.get_object()
        user.archive(archived_by=request.user)
        
        SecurityAuditLog.objects.create(
            user=user,
            action='role_changed',
            ip_address=request.META.get('REMOTE_ADDR'),
            additional_data={'action': 'user_archived', 'by': request.user.username}
        )
        
        return Response(
            {'detail': 'User archived successfully.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore an archived user."""
        user = self.get_object()
        user.restore()
        
        SecurityAuditLog.objects.create(
            user=user,
            action='role_changed',
            ip_address=request.META.get('REMOTE_ADDR'),
            additional_data={'action': 'user_restored', 'by': request.user.username}
        )
        
        return Response(
            {'detail': 'User restored successfully.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Unlock a locked user account."""
        user = self.get_object()
        user.unlock_account()
        
        SecurityAuditLog.objects.create(
            user=user,
            action='account_unlocked',
            ip_address=request.META.get('REMOTE_ADDR'),
            additional_data={'by': request.user.username}
        )
        
        return Response(
            {'detail': 'Account unlocked successfully.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Force password reset for a user."""
        user = self.get_object()
        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # TODO: Send email with reset link
        
        return Response({
            'detail': 'Password reset initiated.',
            'reset_url': f'/auth/password-reset-confirm/{uid}/{token}/'
        }, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """
    Get current authenticated user details.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """
    Change password for authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.password_changed_at = timezone.now()
            user.save()
            
            # Log password change
            SecurityAuditLog.objects.create(
                user=user,
                action='password_change',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True
            )
            
            return Response(
                {'detail': 'Password changed successfully.'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    Request password reset email.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # TODO: Send actual email with reset link
                # For now, just log it
                SecurityAuditLog.objects.create(
                    user=user,
                    action='password_reset_request',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    success=True
                )
                
                return Response({
                    'detail': 'Password reset email sent.',
                    'uid': uid,  # Remove in production
                    'token': token  # Remove in production
                }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                # Don't reveal if email exists
                pass
            
            return Response(
                {'detail': 'Password reset email sent if account exists.'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
                user = User.objects.get(pk=uid)
                token = serializer.validated_data['token']
                
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['new_password'])
                    user.password_changed_at = timezone.now()
                    user.save()
                    
                    SecurityAuditLog.objects.create(
                        user=user,
                        action='password_reset_complete',
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        success=True
                    )
                    
                    return Response(
                        {'detail': 'Password reset successful.'},
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {'detail': 'Invalid or expired token.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response(
                    {'detail': 'Invalid token.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Import models for filter
from django.db import models
from django.utils import timezone
