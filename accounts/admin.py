from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'email', 'mobile_number', 'is_staff', 'membership_active')
    list_filter = ('is_staff', 'is_active', 'membership_active', 'fitness_goal')
    search_fields = ('username', 'full_name', 'email', 'mobile_number')
    
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