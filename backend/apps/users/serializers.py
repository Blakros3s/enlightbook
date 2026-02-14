from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user data.
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'roles': user.get_roles(),
            'primary_role': user.get_primary_role(),
            'two_factor_enabled': user.two_factor_enabled,
        }
        
        return data


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users (minimal data).
    """
    roles = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'roles', 'is_active', 'last_login', 'created_at'
        ]
    
    def get_roles(self, obj):
        return obj.get_roles()


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed user information.
    """
    roles = serializers.SerializerMethodField()
    primary_role = serializers.CharField(source='get_primary_role', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone_number', 'address', 'date_of_birth',
            'profile_picture', 'roles', 'primary_role',
            'is_active', 'is_archived', 'two_factor_enabled',
            'last_login', 'last_login_ip', 'created_at', 'updated_at',
            # Role flags
            'is_master', 'is_principal', 'is_coordinator', 'is_teacher',
            'is_student', 'is_accountant', 'is_driver',
        ]
        read_only_fields = [
            'id', 'last_login', 'last_login_ip', 'created_at', 'updated_at',
            'is_archived', 'account_locked_until', 'failed_login_attempts'
        ]
    
    def get_roles(self, obj):
        return obj.get_roles()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users.
    """
    password = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone_number', 'address',
            'date_of_birth', 'profile_picture',
            # Role flags
            'is_master', 'is_principal', 'is_coordinator', 'is_teacher',
            'is_student', 'is_accountant', 'is_driver',
        ]
    
    def validate(self, data):
        # Check password match
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        
        # Validate password strength
        try:
            validate_password(data.get('password'))
        except ValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })
        
        return data
    
    def create(self, validated_data):
        # Remove password_confirm from data
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Create user
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing users.
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'address', 'date_of_birth', 'profile_picture',
            'is_active',
            # Role flags
            'is_master', 'is_principal', 'is_coordinator', 'is_teacher',
            'is_student', 'is_accountant', 'is_driver',
        ]
        read_only_fields = ['id', 'username']


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        # Check new password match
        if data.get('new_password') != data.get('new_password_confirm'):
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        
        # Validate password strength
        try:
            validate_password(data.get('new_password'))
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return data
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    """
    token = serializers.CharField(required=True)
    uid = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        # Check new password match
        if data.get('new_password') != data.get('new_password_confirm'):
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match.'
            })
        
        # Validate password strength
        try:
            validate_password(data.get('new_password'))
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile (current user).
    """
    roles = serializers.SerializerMethodField()
    primary_role = serializers.CharField(source='get_primary_role', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone_number', 'address', 'date_of_birth',
            'profile_picture', 'roles', 'primary_role',
            'two_factor_enabled', 'last_login', 'created_at'
        ]
        read_only_fields = [
            'id', 'username', 'email', 'roles', 'primary_role',
            'two_factor_enabled', 'last_login', 'created_at'
        ]
    
    def get_roles(self, obj):
        return obj.get_roles()
