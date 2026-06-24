from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'email', 'mobile_number', 'age', 
                 'gender', 'height', 'weight', 'fitness_goal', 'profile_picture',
                 'membership_active', 'membership_expiry', 'is_verified']
        read_only_fields = ['id', 'membership_active', 'membership_expiry', 'is_verified']

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for User Registration"""
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=True, validators=[
        UniqueValidator(queryset=CustomUser.objects.all(), message="A user with that username already exists.")
    ])
    email = serializers.EmailField(required=True, validators=[
        UniqueValidator(queryset=CustomUser.objects.all(), message="A user with that email already exists.")
    ])
    mobile_number = serializers.CharField(required=True, allow_blank=False, error_messages={
        'blank': 'Mobile number is required.',
        'required': 'Mobile number is required.'
    })
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'full_name', 'email', 'password', 'password2', 'mobile_number',
                 'age', 'gender', 'height', 'weight', 'fitness_goal']
    
    def validate_mobile_number(self, value):
        """Validate mobile number: must be exactly 10 digits"""
        if not value:
            raise serializers.ValidationError("Mobile number is required.")

        # Remove any spaces or special characters for checking
        clean_number = ''.join(filter(str.isdigit, value))

        if len(clean_number) != 10:
            raise serializers.ValidationError("Enter a valid 10-digit mobile number.")

        if not clean_number.isdigit():
            raise serializers.ValidationError("Mobile number must contain only digits.")

        return clean_number
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        first_name = attrs.get('first_name', '').strip()
        last_name = attrs.get('last_name', '').strip()
        full_name = attrs.get('full_name', '').strip()

        if not full_name:
            full_name = " ".join(part for part in [first_name, last_name] if part)

        if not full_name:
            raise serializers.ValidationError({"full_name": "Please provide either full name or both first and last name."})

        attrs['full_name'] = full_name
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        validated_data.pop('first_name', None)
        validated_data.pop('last_name', None)
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for User Profile Update"""
    
    class Meta:
        model = CustomUser
        fields = ['full_name', 'mobile_number', 'age', 'gender', 'height', 'weight', 
                 'fitness_goal', 'profile_picture']

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for Password Change"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs