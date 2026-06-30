from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'user_full_name', 'email', 'user_mobile', 'is_staff', 'membership_active')
    list_filter = ('is_staff', 'is_active', 'membership_active', 'fitness_goal')
    search_fields = ('username', 'email')
    
    def user_full_name(self, obj):
        """Safe full name display"""
        return obj.full_name or obj.first_name or obj.username or 'N/A'
    user_full_name.short_description = 'Full Name'
    
    def user_mobile(self, obj):
        """Safe mobile number display"""
        return obj.mobile_number or 'N/A'
    user_mobile.short_description = 'Mobile Number'
    
    fieldsets = UserAdmin.fieldsets + (
        ('Personal Info', {'fields': ('full_name', 'mobile_number', 'age', 'gender', 'height', 'weight')}),
        ('Fitness Info', {'fields': ('fitness_goal', 'profile_picture')}),
        ('Membership Info', {'fields': ('membership_expiry', 'membership_active')}),
        ('Verification', {'fields': ('is_verified', 'email_verified')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Personal Info', {'fields': ('full_name', 'mobile_number', 'age', 'gender', 'height', 'weight', 'fitness_goal')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)